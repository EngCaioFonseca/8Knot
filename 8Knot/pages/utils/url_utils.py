from urllib.parse import parse_qs

# Maps each registered page path to the list of graph component IDs
# (formatted as "{PAGE}-{VIZ_ID}") that live on that page.
# Add new graph IDs here when introducing them.
# Move removed entries to DEPRECATED_GRAPH_REGISTRY below.
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
        "contributions-cntrib-pr-assignment",
        "contributions-pr_assignment",
        "contributions-issue-staleness",
        "contributions-issues-over-time",
        "contributions-cntrib_issue-assignment",
        "contributions-issue_assignment",
        "contributions-commits-over-time",
        "contributions-pr-first-response",
        "contributions-pr-review-response",
    ],
    "/contributors/behavior": [
        "contributors-contrib-drive-repeat",
        "contributors-first-time-contribution",
        "contributors-active-drifting-contributors",
        "contributors-new-contributor",
        "contributors-contrib-types-over-time",
    ],
    "/contributors/contribution_types": [
        "contributors-contribs-by-action",
        "contributors-contrib-activity-cycle",
        "contributors-contrib-importance-pie",
        "contributors-lottery-factor-over-time",
    ],
    "/chaoss": [
        "chaoss-contrib-importance-pie",
        "chaoss-project-velocity",
    ],
    "/affiliation": [
        "affiliation-commit-domains",
        "affiliation-unique-domains",
        "affiliation-organization-associated-activity",
        "affiliation-org-core-contributors",
        "affiliation-gh-org-affiliation",
    ],
    "/codebase": [
        "codebase-cntrb-file-heatmap",
        "codebase-contribution-file-heatmap",
        "codebase-reviewer-file-heatmap",
    ],
}

# Maps (old_pathname, old_graph_id) → (new_pathname, new_graph_id) or None if removed.
# Populate this when renaming or removing pages/graphs so old shared links get
# a helpful redirect instead of a generic error.
DEPRECATED_GRAPH_REGISTRY: dict[tuple, tuple | None] = {
    # Example:
    # ("/heatmaps", "heatmaps-file-heatmap"): ("/codebase", "codebase-cntrb-file-heatmap"),
    # ("/old-page", "old-page-some-graph"): None,  # removed, no replacement
}

MAX_REPOS_PER_SHARE = 200


def validate_target(pathname: str, graph_id: str | None) -> tuple[bool, tuple | None]:
    """Check whether a pathname + graph_id combination is still valid.

    Returns:
        (True, None)                   – target is valid
        (False, (new_path, new_graph)) – deprecated but redirectable
        (False, None)                  – unknown / removed
    """
    if pathname in VALID_GRAPH_REGISTRY:
        return True, None
    redirect = DEPRECATED_GRAPH_REGISTRY.get((pathname, graph_id))
    if redirect is not None:
        return False, redirect
    return False, None


def compose_short_url(base: str, short_id: str, pathname: str, graph_id: str | None) -> str:
    frag = f"#{graph_id}" if graph_id else ""
    return f"{base.rstrip('/')}{pathname}?s={short_id}{frag}"


def compose_long_url(base: str, encoded_state: str, pathname: str, graph_id: str | None) -> str:
    """Build a self-contained long URL that can be decoded without a DB lookup."""
    frag = f"#{graph_id}" if graph_id else ""
    return f"{base.rstrip('/')}{pathname}?state={encoded_state}{frag}"


def extract_url_params(search: str) -> dict:
    """Parse ?s= and ?state= from the URL search string."""
    if not search:
        return {"short_id": None, "state": None}
    params = parse_qs(search.lstrip("?"))
    return {
        "short_id": (params.get("s") or [None])[0],
        "state": (params.get("state") or [None])[0],
    }
