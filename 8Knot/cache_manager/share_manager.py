"""
URL shortener: maps 8-character base62 IDs to full encoded state blobs.

Uses the same PostgreSQL instance as the rest of the cache (augur_cache).
The share_links table is created in db_init.py.
"""

import secrets
import string
import random
import logging
import psycopg2 as pg
import psycopg2.errors

from cx_common import cache_cx_string

_ALPHABET = string.ascii_letters + string.digits
_ID_LENGTH = 8
_CLEANUP_PROBABILITY = 0.01  # 1% chance to run cleanup on each shorten call


def _gen_id() -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(_ID_LENGTH))


def shorten(full_state: str) -> str:
    """Store full_state blob and return a short ID.

    Retries up to 5 times on the unlikely ID collision.
    """
    if random.random() < _CLEANUP_PROBABILITY:
        try:
            cleanup_expired()
        except Exception as e:
            logging.warning(f"share_manager: background cleanup failed: {e}")

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
            continue

    raise RuntimeError("could not generate unique share ID after 5 attempts")


def expand(short_id: str) -> str | None:
    """Return the full_state for short_id, or None if not found / expired."""
    try:
        with pg.connect(cache_cx_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE share_links
                       SET last_accessed = NOW(),
                           access_count  = access_count + 1
                     WHERE short_id  = %s
                       AND expires_at > NOW()
                    RETURNING full_state
                    """,
                    (short_id,),
                )
                row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        logging.error(f"share_manager.expand: {e}")
        return None


def cleanup_expired() -> int:
    """Delete expired share links. Returns count of deleted rows."""
    with pg.connect(cache_cx_string) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM share_links WHERE expires_at <= NOW()")
            return cur.rowcount
