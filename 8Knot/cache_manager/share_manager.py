import secrets
import string
import logging
import psycopg2 as pg
from .cx_common import cache_cx_string

_ALPHABET = string.ascii_letters + string.digits  # base62, no ambiguous chars
_ID_LENGTH = 8


def _gen_id() -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(_ID_LENGTH))


def shorten(full_state: str) -> str:
    """Store encoded state and return a short_id mapping to it.

    Retries ID generation on the rare collision. The DB table is the
    authoritative source of uniqueness via the PRIMARY KEY constraint.
    """
    for _ in range(5):
        short_id = _gen_id()
        try:
            with pg.connect(cache_cx_string) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO share_links (short_id, full_state) VALUES (%s, %s)",
                        (short_id, full_state),
                    )
            return short_id
        except pg.errors.UniqueViolation:
            logging.warning("share_manager.shorten: ID collision, retrying")
            continue
    raise RuntimeError("share_manager.shorten: could not generate unique ID after 5 attempts")


def expand(short_id: str) -> str | None:
    """Return full_state for a valid, non-expired short_id and bump access stats.

    Returns None if the ID is not found or has expired.
    """
    with pg.connect(cache_cx_string) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE share_links
                SET last_accessed = NOW(), access_count = access_count + 1
                WHERE short_id = %s AND expires_at > NOW()
                RETURNING full_state
                """,
                (short_id,),
            )
            row = cur.fetchone()
    return row[0] if row else None


def cleanup_expired() -> int:
    """Delete expired share links. Returns the number of rows removed."""
    with pg.connect(cache_cx_string) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM share_links WHERE expires_at <= NOW()")
            count = cur.rowcount
    logging.warning(f"share_manager.cleanup_expired: removed {count} expired link(s)")
    return count
