from dash import html, dcc
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from app import augur
import os
import logging

#  login banner that will be displayed when login is disabled
login_banner = None
if os.getenv("AUGUR_LOGIN_ENABLED", "False") != "True":
    login_banner = html.Div(
        dbc.Alert(
            [
                html.H4(
                    "Login is Currently Disabled",
                    className="alert-heading",
                    style={"color": "black", "fontWeight": "600", "margin": "0 0 8px 0", "textShadow": "none"},
                ),
                html.P(
                    [
                        "If you need to collect data on new repositories, please ",
                        html.A(
                            "create a repository collection request",
                            href="https://github.com/oss-aspen/8Knot/issues/new?template=augur_load.md",
                            target="_blank",
                            style={"fontWeight": "500", "color": "#1565C0"},
                        ),
                        ".",
                    ],
                    style={"color": "#333333", "margin": "0 0 10px 0"},
                ),
            ],
            color="light",
            dismissable=True,
            id="login-disabled-banner",
            className="mb-0",
            style={
                "backgroundColor": "#EDF7ED",  # Light green background
                "borderColor": "#6b8976",  # Darker green border from palette
                "border": "1px solid #6b8976",
                "borderLeft": "5px solid #6b8976",
                "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.15)",
                "maxWidth": "400px",
                "padding": "15px",
                "zIndex": "1000",
            },
        ),
        style={"position": "fixed", "top": "70px", "right": "20px", "zIndex": "1000"},  # Position below navbar
    )

# if param doesn't exist, default to False. Otherwise, use the param's value.
# this determines if the login option will be shown or not
if os.getenv("AUGUR_LOGIN_ENABLED", "False") == "True":
    logging.warning("LOGIN ENABLED")
    login_navbar = [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Nav(
                        [
                            dcc.Loading(
                                children=[
                                    html.Div(
                                        id="nav-login-container",
                                        children=[],
                                    ),
                                ]
                            ),
                            dbc.NavItem(
                                dbc.NavLink("Refresh Groups", id="refresh-button", disabled=True),
                            ),
                            dbc.NavItem(
                                dbc.NavLink(
                                    "Manage Groups",
                                    id="manage-group-button",
                                    disabled=True,
                                    href=f"{augur.user_account_endpoint}?section=tracker",
                                    external_link="True",
                                    target="_blank",
                                ),
                            ),
                            dbc.NavItem(
                                dbc.NavLink(
                                    "Log out",
                                    id="logout-button",
                                    disabled=True,
                                    href="/logout/",
                                    external_link=True,
                                ),
                            ),
                            dbc.Popover(
                                children="Login Failed",
                                body=True,
                                id="login-popover",
                                is_open=False,
                                placement="bottom-end",
                                target="nav-dropdown",
                            ),
                        ]
                    )
                )
            ],
            align="center",
        ),
    ]
else:
    logging.warning("LOGIN DISABLED")
    login_navbar = [html.Div()]

# Clean navbar matching target design - no borders or lines
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.Div(
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                    "width": "100%",
                    "height": "32px",
                    "gap": "48px",
                },
                children=[
                    # Logo section
                    html.Div(
                        style={"display": "flex", "flexDirection": "row", "alignItems": "center", "gap": "10.41px"},
                        children=[
                            html.Img(
                                src=dash.get_asset_url("8knot-logo-vertical.png"),
                                style={"width": "23.79px", "height": "22.31px"},
                            ),
                            html.Span(
                                "8KNOT",
                                style={
                                    "fontFamily": "Inter",
                                    "fontWeight": "700",
                                    "fontSize": "16px",
                                    "color": "#222D33",
                                },
                            ),
                            html.Div(
                                "CHAOSS",
                                style={
                                    "background": "#222D33",
                                    "borderRadius": "16.22px",
                                    "padding": "6.49px",
                                    "color": "#FFFFFF",
                                    "fontSize": "10px",
                                    "fontWeight": "500",
                                },
                            ),
                        ],
                    ),
                    # Navigation items
                    html.Div(
                        style={
                            "display": "flex",
                            "flexDirection": "row",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "gap": "24px",
                            "flexGrow": "1",
                        },
                        children=[
                            dbc.NavLink(
                                "Welcome",
                                href="/",
                                active="exact",
                                style={
                                    "color": "#222D33",
                                    "fontFamily": "Inter",
                                    "fontWeight": "500",
                                    "fontSize": "16px",
                                    "borderBottom": "1px solid #D61B5E",
                                    "padding": "4px 0px",
                                    "textDecoration": "none",
                                },
                            ),
                            dbc.DropdownMenu(
                                [
                                    dbc.DropdownMenuItem("Repo Overview", href="/repo_overview"),
                                    dbc.DropdownMenuItem("Contributions", href="/contributions"),
                                    dbc.DropdownMenuItem("Contributors - Behavior", href="/contributors/behavior"),
                                    dbc.DropdownMenuItem(
                                        "Contributors - Types", href="/contributors/contribution_types"
                                    ),
                                    dbc.DropdownMenuItem("Affiliation", href="/affiliation"),
                                    dbc.DropdownMenuItem("CHAOSS", href="/chaoss"),
                                ],
                                label="Visualizations",
                                nav=True,
                                style={
                                    "color": "#222D33",
                                    "fontFamily": "Inter",
                                    "fontWeight": "500",
                                    "fontSize": "16px",
                                    "padding": "4px 0px",
                                },
                            ),
                            dbc.NavLink(
                                "Repo list",
                                href="/repo_overview",
                                active="exact",
                                style={
                                    "color": "#222D33",
                                    "fontFamily": "Inter",
                                    "fontWeight": "500",
                                    "fontSize": "16px",
                                    "padding": "4px 0px",
                                    "textDecoration": "none",
                                },
                            ),
                        ],
                    ),
                    # Login section
                    html.Div(
                        style={"display": "flex", "flexDirection": "row", "alignItems": "center", "gap": "4px"},
                        children=[
                            html.I(
                                className="fas fa-user", style={"width": "32px", "height": "32px", "color": "#292D32"}
                            ),
                            html.Span(
                                "Log in",
                                style={
                                    "fontFamily": "Inter",
                                    "fontWeight": "400",
                                    "fontSize": "16px",
                                    "color": "#222D33",
                                },
                            ),
                        ],
                    ),
                ],
            ),
            login_navbar[0] if login_navbar else html.Div(),
        ],
        fluid=True,
        style={"border": "none"},
    ),
    style={
        "background": "#FFFFFF",
        "border": "none",
        "borderBottom": "none",
        "borderTop": "none",
        "boxShadow": "none",
        "padding": "8px 0",
    },
    sticky="top",
    className="navbar-no-border",
)

navbar_bottom = dbc.NavbarSimple(
    children=[
        dbc.NavItem(
            dbc.NavLink(
                "Visualization request",
                href="https://github.com/oss-aspen/8Knot/issues/new?assignees=&labels=enhancement%2Cvisualization&template=visualizations.md",
                external_link="True",
                target="_blank",
                style={"color": "white", "fontSize": "0.9rem"},
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Bug",
                href="https://github.com/oss-aspen/8Knot/issues/new?assignees=&labels=bug&template=bug_report.md",
                external_link="True",
                target="_blank",
                style={"color": "white", "fontSize": "0.9rem"},
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Repo/Org Request",
                href="https://github.com/oss-aspen/8Knot/issues/new?assignees=&labels=augur&template=augur_load.md",
                external_link="True",
                target="_blank",
                style={"color": "white", "fontSize": "0.9rem"},
            )
        ),
    ],
    brand="",
    brand_href="#",
    style={
        "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "border": "none",
        "boxShadow": "0 -2px 10px rgba(0,0,0,0.1)",
    },
    fluid=True,
)

layout = dbc.Container(
    [
        # Custom CSS to remove all navbar borders - using proper Dash method
        html.Script(
            """
            // Add CSS to remove navbar borders
            const style = document.createElement('style');
            style.textContent = `
                .navbar, .navbar-no-border {
                    border: none !important;
                    border-bottom: none !important;
                    border-top: none !important;
                    box-shadow: none !important;
                }
                .navbar .container-fluid {
                    border: none !important;
                }
                .nav-link {
                    border: none !important;
                }
            `;
            document.head.appendChild(style);
            """
        ),
        # Job data storage for query management (required for the application)
        dcc.Store(id="repo-choices", storage_type="session", data=[]),
        dcc.Store(id="job-ids", storage_type="session", data=[]),
        dcc.Store(id="user-group-loading-signal", data="", storage_type="memory"),
        dcc.Location(id="url"),
        # Add client-side script to handle storage quota issues
        html.Script(
            """
            window.addEventListener('error', function(event) {
                if (event.message && event.message.toLowerCase().includes('quota') &&
                    event.message.toLowerCase().includes('exceeded')) {
                    var warningEl = document.getElementById('storage-quota-warning');
                    if (warningEl) {
                        warningEl.style.display = 'block';
                    }
                }
            });

            // Test storage capacity
            try {
                var testKey = 'storage_test';
                var testString = new Array(512 * 1024).join('a');  // 512KB
                sessionStorage.setItem(testKey, testString);
                sessionStorage.removeItem(testKey);
            } catch (e) {
                if (e.name === 'QuotaExceededError' ||
                    (e.message &&
                    (e.message.toLowerCase().includes('quota') ||
                     e.message.toLowerCase().includes('exceeded')))) {
                    var warningEl = document.getElementById('storage-quota-warning');
                    if (warningEl) {
                        warningEl.style.display = 'block';
                    }
                }
            }
        """
        ),
        navbar,
        # Add login banner overlay (will be positioned via CSS)
        login_banner if login_banner else html.Div(),
        # Main content area
        html.Div(
            style={"minHeight": "100vh", "padding": "0"},
            children=[
                # where our page will be rendered
                dash.page_container,
            ],
        ),
        navbar_bottom,
    ],
    fluid=True,
    className="dbc",
)
