import gzip
import json
import base64

CURRENT_VERSION = 1


def encode_state(
    repo_ids: list,
    org_names: list,
    pathname: str,
    graph_id: str | None,
    filters: dict | None = None,
) -> str:
    """Serialize and compress app state into a URL-safe base64 string."""
    payload = {
        "v": CURRENT_VERSION,
        "repo_ids": repo_ids,
        "org_names": org_names,
        "pathname": pathname,
        "graph_id": graph_id,
        "filters": filters or {},
    }
    raw = json.dumps(payload, separators=(",", ":")).encode()
    compressed = gzip.compress(raw, compresslevel=9)
    return base64.urlsafe_b64encode(compressed).decode().rstrip("=")


def decode_state(encoded: str) -> dict | None:
    """Decompress and deserialize a state string. Returns None on any error or version mismatch."""
    try:
        # restore stripped padding
        padded = encoded + "=" * (-len(encoded) % 4)
        compressed = base64.urlsafe_b64decode(padded)
        raw = gzip.decompress(compressed)
        payload = json.loads(raw)
        if payload.get("v") != CURRENT_VERSION:
            return None
        return payload
    except Exception:
        return None
