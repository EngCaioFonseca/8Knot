"""
Registry and helpers for share-URL validation and composition.

VALID_GRAPH_REGISTRY maps every page path to the list of graph
component IDs that can be targeted. Anything not listed here is
rejected before a short link is minted.
"""

from urllib.parse import urlencode, urlparse, parse_qs

MAX_REPOS_PER_SHARE = 200

VALID_GRAPH_REGISTRY: dict[str, list[str]] = {
    "/repo_overview": [
        "repo_info-code-languages",
        "repo_info-package-version",
        "repo_info-ossf-scorecard",
        "repo_info-repo-general-info",
    ],
    "/contributions": [
        "contributions-pr-staleness",
        "contributions-prs-over-time",
        "contributions-commits-over-time",
        "contributions-issues-over-time",
        "contributions-issue-staleness",
        "contributions-self-merge-rate",
        "contributions-pr-first-response",
        "contributions-pr-review-response",
        "contributions-pr_assignment",
        "contributions-issue_assignment",
        "contributions-cntrb-pr-assignment",
        "contributions-cntrib-issue-assignment",
    ],
    "/contributors/behavior": [
        "contributors-active-drifting-contributors",
        "contributors-contrib-drive-repeat",
        "contributors-first-time-contribution",
        "contributors-new-contributor",
        "contributors-contributors-types-over-time",
    ],
    "/contributors/contribution_types": [
        "contributors-contribs-by-action",
        "contributors-contrib-activity-cycle",
        "contributors-contrib-importance-pie",
        "contributors-contrib-importance-over-time",
    ],
    "/chaoss": [
        "chaoss-contrib-importance-pie",
        "chaoss-project-velocity",
    ],
    "/affiliation": [
        "affiliation-commit-domains",
        "affiliation-unqiue-domains",
        "affiliation-org-associated-activity",
        "affiliation-org-core-contributors",
        "affiliation-gh-org-affiliation",
    ],
    "/codebase": [
        "codebase-cntrb-file-heatmap",
        "codebase-contribution-file-heatmap",
        "codebase-reviewer-file-heatmap",
    ],
}

# Maps (old_path, old_graph_id) → (new_path, new_graph_id) | None
DEPRECATED_GRAPH_REGISTRY: dict[tuple, tuple | None] = {}


def validate_target(pathname: str, graph_id: str) -> bool:
    graphs = VALID_GRAPH_REGISTRY.get(pathname)
    if graphs is None:
        return False
    return graph_id in graphs


def compose_short_url(base_url: str, short_id: str, pathname: str, graph_id: str) -> str:
    """Build the full shareable short URL."""
    params = urlencode({"s": short_id})
    return f"{base_url}{pathname}?{params}#{graph_id}"


def extract_url_params(search: str) -> dict:
    """Parse ?s=<id> or ?state=<blob> from dcc.Location search string."""
    if not search:
        return {}
    parsed = parse_qs(search.lstrip("?"))
    result = {}
    if "s" in parsed:
        result["short_id"] = parsed["s"][0]
    if "state" in parsed:
        result["state"] = parsed["state"][0]
    return result
