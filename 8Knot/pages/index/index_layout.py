from dash import html, dcc
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from app import augur
import os
import logging

# Import layout components
from .index_components import (
    create_main_content_area,
    create_sidebar_navigation,
    create_sidebar,
    create_main_layout,
    create_app_stores,
    create_storage_quota_script,
    initialize_components,
)

# Import search bar and bottom navbar utility functions
from .search_utils import (
    create_search_bar,
    create_bottom_navbar,
)

# Import login utility functions
from .login_utils import (
    create_login_disabled_banner,
    create_login_navbar,
    is_login_enabled,
)

# Note: Welcome sections are now imported in pages/landing/landing.py

# Top bar with logos and navigation links
topbar = html.Div(
    [
        # Left section with hamburger menu and logos
        html.Div(
            [
                # Hamburger menu toggle button
                dbc.Button(
                    html.I(className="fas fa-bars sidebar-toggle-icon"),
                    id="sidebar-toggle",
                    color="link",
                    size="sm",
                    className="sidebar-toggle",
                ),
                html.Img(
                    src="/assets/8Knot.svg",
                    alt="8Knot Logo",
                    className="logo",
                ),
                html.Img(
                    src="/assets/CHAOSS.svg",
                    alt="CHAOSS Logo",
                    className="logo logo--chaoss",
                ),
            ],
            className="topbar-left",
        ),
        # Middle section with navigation links
        html.Div(
            [
                dbc.NavLink(
                    "Welcome",
                    href="/",
                    active="exact",
                    className="nav-link",
                ),
                dbc.NavLink(
                    "Visualizations",
                    href="/repo_overview",
                    active="exact",
                    className="nav-link nav-link--visualization",
                ),
            ],
            className="topbar-center",
        ),
        # Right section (empty for now, can be used for future additions)
        html.Div(className="topbar-right"),
    ],
    id="rectangular-bar",
    className="topbar",
)


# Login status logging
if is_login_enabled():
    logging.warning("LOGIN ENABLED")
else:
    logging.warning("LOGIN DISABLED")

# Create login banner (shown when login is disabled)
login_banner = create_login_disabled_banner()

# Create login navbar (shown when login is enabled)
login_navbar = create_login_navbar(augur)

# Create search bar with initial option from augur
search_bar = create_search_bar(augur.initial_multiselect_option())

# Create bottom navigation bar with request links
navbar_bottom = create_bottom_navbar()

# Initialize components with required references
initialize_components(search_bar)

# Note: Index layout provides the main application structure
# The landing page is now registered separately in pages/landing/landing.py

# Share modal - shown when user clicks a Share button
share_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Share this graph")),
        dbc.ModalBody(
            [
                dbc.Label("Copy the link below to share this graph with the current repo selection:"),
                dbc.InputGroup(
                    [
                        dbc.Input(id="share-url-display", readonly=True, className="share-url-input"),
                        dcc.Clipboard(
                            target_id="share-url-display",
                            title="Copy link",
                            style={"display": "inline-flex", "alignItems": "center", "padding": "0.375rem 0.75rem"},
                        ),
                    ]
                ),
            ]
        ),
        dbc.ModalFooter(dbc.Button("Close", id="share-modal-close", className="ms-auto")),
    ],
    id="share-modal",
    is_open=False,
)

# Toast shown when a share URL is loaded successfully
share_load_toast = dbc.Toast(
    id="share-load-toast",
    header="Graph loaded from shared link",
    is_open=False,
    dismissable=True,
    duration=4000,
    style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 9999},
)

# Main application layout
layout = html.Div(
    dbc.Container(
        [
            # Application stores and scripts
            *create_app_stores(),
            create_storage_quota_script(),
            # Share UI overlays
            share_modal,
            share_load_toast,
            # Login banner overlay
            login_banner if login_banner else html.Div(),
            # Main application structure
            dbc.Row(
                [
                    dbc.Col(
                        [
                            topbar,
                            create_main_layout(),
                        ],
                    ),
                ],
                justify="start",
            ),
            navbar_bottom,
        ],
        fluid=True,
        className="dbc app-main-container",
    ),
    className="app-container",
)
