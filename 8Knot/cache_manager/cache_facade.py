"""
Cache facade: interface between application callbacks and the local Postgres
cache database.

We use psycopg2 directly rather than SQLAlchemy because the cache's data model
is simple and the ORM abstraction adds measurable memory overhead for the
high-volume insert and read paths we rely on.

Read path (retrieve_from_cache):
  Uses PostgreSQL COPY TO STDOUT → pyarrow CSV reader → pandas DataFrame.
  This bypasses Python-object materialisation from fetchall(), reducing peak
  memory by ~3-8× depending on the number of columns fetched.

Write path (cache_query_results):
  Uses a server-side named cursor on Augur + execute_values batched INSERT
  into the local UNLOGGED cache tables.
"""
import io
import logging
from uuid import uuid4

import pandas as pd
import psycopg2 as pg
import pyarrow.csv as pa_csv
from psycopg2 import sql as pg_sql
from psycopg2.extras import execute_values

# requires relative import syntax "import .cx_common" because
# other files importing cache_facade need to know how to resolve
# .cx_common- interpreter is invoked at a higher level, so relative
# import required.
from .cx_common import db_cx_string, env_augur_schema, cache_cx_string


def cache_query_results(
    db_connection_string: str,
    query: str,
    vars: tuple[tuple],
    target_table: str,
    bookkeeping_data: tuple[dict],
    server_pagination=2000,
    client_pagination=2000,
) -> None:
    """Runs {query} against primary database specified by {db_connection_string} with variables {vars}.
    Retrieves results from db with paginations {server_pagination} and {client_pagination}.

    Args:
        db_connection_string (str): _description_
        query (str): _description_
        vars (tuple(tuple)): _description_
        target_table (str): _description_
        bookkeeping_data (tuple(dict)): _description_
        server_pagination (int, optional): _description_. Defaults to 2000.
        client_pagination (int, optional): _description_. Defaults to 2000.
    """
    logging.warning(f"{target_table} -- CQR CACHE_QUERY_RESULTS BEGIN")
    with pg.connect(
        db_connection_string,
        options=f"-c search_path={env_augur_schema}",
    ) as augur_conn:
        with augur_conn.cursor(name=f"{target_table}-{uuid4()}") as augur_cur:
            # set number of rows we want from primary db at a time
            augur_cur.itersize = server_pagination

            logging.warning(f"{target_table} -- CQR EXECUTING QUERY")

            # execute query
            augur_cur.execute(query, vars)

            logging.warning(f"{target_table} -- CQR STARTING TRANSACTION")
            # connect to cache
            with pg.connect(cache_cx_string) as cache_conn:
                logging.warning(f"{target_table} -- CQR COMPOSING SQL")
                # compose SQL w/ table name
                # ref: https://www.psycopg.org/docs/sql.html
                composed_query = pg_sql.SQL(
                    "INSERT INTO {tbl_name} VALUES %s ON CONFLICT DO NOTHING".format(tbl_name=target_table)
                ).as_string(cache_conn)

                # iterate through pages of rows from server.
                logging.warning(f"{target_table} -- CQR FETCHING AND STORING ROWS")
                while rows := augur_cur.fetchmany(client_pagination):
                    if not rows:
                        # we're out of rows
                        break

                    # write available rows to cache.
                    with cache_conn.cursor() as cache_cur:
                        execute_values(
                            cur=cache_cur,
                            sql=composed_query,
                            argslist=rows,
                            page_size=client_pagination,
                        )

                # after all data has successfully been written to cache from the primary db,
                # insert record of existence for each (cache_func, repo_id) pair.
                logging.warning(f"{target_table} -- CQR UPDATING BOOKKEEPING")
                with cache_conn.cursor() as cache_cur:
                    execute_values(
                        cur=cache_cur,
                        sql="""
                        INSERT INTO cache_bookkeeping (cache_func, repo_id)
                        VALUES %s
                        """,
                        template="(%(cache_func)s, %(repo_id)s)",
                        argslist=bookkeeping_data,
                    )

                logging.warning(f"{target_table} -- CQR COMMITTING TRANSACTION")
                # TODO: end of context block, on success, should commit. On failure, should rollback. Need to write test for this.

        # don't need to commit on primary db
        logging.warning(f"{target_table} -- CQR SUCCESS")


def get_uncached(func_name: str, repolist: list[int]) -> list[int]:  # or None
    """
    Checks bookkeeping data to find, for a given querying function, which
    repos' data are noted as present in cache vs. those that arent.

    Returns a list of repos that AREN'T resident in cache.
    """
    # Handle None or empty repolist
    if not repolist:
        return []

    with pg.connect(cache_cx_string) as cache_conn:
        with cache_conn.cursor() as cache_cur:
            composed_query = pg_sql.SQL(
                """
                SELECT cb.repo_id
                FROM cache_bookkeeping cb
                WHERE cb.cache_func = '{cache_func_name}' AND cb.repo_id in %s
                """.format(
                    cache_func_name=func_name
                )
            ).as_string(cache_conn)

            # exec query
            cache_cur.execute(query=composed_query, vars=(tuple(repolist),))

            # get list of cached repos
            already_cached: list[tuple] = cache_cur.fetchall()

            # process list of single-value tuples to get list of values.
            # looks like: [(val1,), (val2,), ...]
            already_cached: set[int] = set([v[0] for v in already_cached])

            # repos that are already cached will be removed from repolist set,
            # leaving uncached remaining.
            not_cached: list[int] = list(set(repolist) - already_cached)

            return not_cached


def caching_wrapper(func_name: str, query: str, repolist: list[int], n_repolist_uses=1) -> None:
    """Combines steps of (1) identifying which repos aren't already cached and
    (2) querying + caching repos those repos.

    Args:
        func_name (str): literal name of querying function for bookkeeping
        query (str): sql query as a string
        repolist (list[int]): list of repos requested by user.
        n_repolist_uses (int): if the repolist is used more than once in the query, simply inject it again.
                                TODO: remove this hack and parameterize queries by name

    Raises:
        Exception: If a step fails, will print exception and re-raise.

    Returns:
        _type_: None
    """

    # Handle None or empty repolist
    if not repolist:
        logging.warning(f"{func_name} COLLECTION - NO REPOS TO CACHE")
        return 0

    try:
        # STEP 1: Which repos need to be queried for?
        #           some might already be in cache.
        uncached_repos: list[int] | None = get_uncached(func_name=func_name, repolist=repolist)
        if not uncached_repos:
            logging.warning(f"{func_name} COLLECTION - ALL REQUESTED REPOS IN CACHE")
            return 0
        else:
            logging.warning(f"{func_name} COLLECTION - CACHING {len(uncached_repos)} NEW REPOS")

            # inject the repolist multiple times because the SQL uses it more
            # than once and the wildcard %s are ordered.
            uncached_repos: tuple[tuple] = tuple([tuple(uncached_repos) for _ in range(n_repolist_uses)])

        # STEP 2: Query for those repos
        logging.warning(f"{func_name} COLLECTION - EXECUTING CACHING QUERY")
        cache_query_results(
            db_connection_string=db_cx_string,
            query=query,
            vars=uncached_repos,
            target_table=func_name,
            bookkeeping_data=tuple({"cache_func": func_name, "repo_id": r} for r in repolist),
        )
    except Exception as e:
        logging.critical(f"{func_name}_POSTGRES ERROR: {e}")

        # raise exception so caching function knows to restart
        raise Exception(e)


def retrieve_from_cache(
    tablename: str,
    repolist: list[int],
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """Fetch cached query results for the given repositories.

    Uses PostgreSQL COPY TO STDOUT to stream data directly into a pyarrow
    CSV reader, avoiding the Python-object materialisation overhead of
    fetchall() + pd.DataFrame(rows). The database connection is released
    before the buffer is parsed, keeping connection hold-time minimal.

    Args:
        tablename: Cache table name — always a query function's __name__
                   (e.g. "issues_query"), which are valid SQL identifiers.
        repolist:  Repository IDs to filter on.
        columns:   Subset of columns to fetch. Omit or pass None for all
                   columns. Column pruning reduces both network transfer and
                   peak memory proportionally to the columns skipped.

    Returns:
        pd.DataFrame with columns matching the requested schema.
        Returns an empty DataFrame (no rows, no columns) if repolist is empty.
    """
    if not repolist:
        return pd.DataFrame()

    col_expr = ", ".join(f"t.{c}" for c in columns) if columns else "t.*"
    # Integer cast is the injection guard: repo IDs are always integers and
    # str(int(x)) raises on anything that isn't, so malformed values never
    # reach the query string.
    ids_literal = ", ".join(str(int(r)) for r in repolist)

    copy_sql = (
        f"COPY (SELECT {col_expr} FROM {tablename} t"
        f" WHERE t.repo_id IN ({ids_literal}))"
        " TO STDOUT WITH (FORMAT CSV, HEADER TRUE)"
    )

    logging.warning(f"{tablename} - LOADING DATA FROM CACHE")

    buf = io.BytesIO()
    with pg.connect(cache_cx_string) as conn:
        with conn.cursor() as cur:
            cur.copy_expert(copy_sql, buf)
    # Connection released here — before the (potentially slow) CSV parse.

    buf.seek(0)
    # pyarrow infers column types from the CSV values: integer ID columns
    # become int64, datetime text columns become datetime64[s] (tz-naive).
    # All downstream callers already call pd.to_datetime() on datetime
    # columns, which is a no-op when the column is already datetime64 and
    # correctly localises to UTC when utc=True is passed. NULL fields in
    # the CSV become NaT, and df["col"].isnull() handles NaT correctly.
    df = pa_csv.read_csv(buf).to_pandas()

    logging.warning(f"{tablename} - DATA LOADED - {df.shape} rows,cols")
    return df
