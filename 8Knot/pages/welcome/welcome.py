from dash import dcc, html, Input, Output, callback
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from app import augur

# import other sections
from .sections.general_section import layout as general_tab_contents
from .sections.plotly_section import layout as plotly_tab_contents
from .sections.augur_login_section import layout as augur_tab_contents
from .sections.user_group_section import layout as group_tab_contents

# register the page
dash.register_page(__name__, path="/", order=1)

# Create layout matching the target design exactly
layout = html.Div(
    style={
        "background": "#FFFFFF",  # pure white like Figma base
        "minHeight": "100vh",
        "padding": "0",
        "margin": "0",
        "position": "relative",
    },
    children=[
        # Main content area
        dbc.Container(
            fluid=True,
            style={"padding": "0"},
            children=[
                # Unified hero section with gradients throughout entire page
                html.Div(
                    style={
                        "padding": "80px 20px",
                        "textAlign": "center",
                        "minHeight": "100vh",  # Full viewport height
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "center",
                        "alignItems": "center",
                        "position": "relative",  # For absolute positioning of ellipses
                        "overflow": "hidden",  # Hide overflowing ellipses
                    },
                    children=[
                        # Background decorative ellipses (exactly as in working Figma)
                        html.Div(
                            [
                                # Ellipse 5 (Pink gradient)
                                html.Div(
                                    style={
                                        "position": "absolute",
                                        "width": "2329px",
                                        "height": "2329px",
                                        "left": "-1305px",
                                        "top": "-887px",
                                        "background": "radial-gradient(50% 50% at 50% 50%, rgba(255, 107, 160, 0.2) 0%, rgba(255, 255, 255, 0) 62.81%)",
                                        "filter": "blur(9.3138px)",
                                        "zIndex": "1",
                                    }
                                ),
                                # Ellipse 6 (Green gradient) - RESTORED
                                html.Div(
                                    style={
                                        "position": "absolute",
                                        "width": "2278px",
                                        "height": "2278px",
                                        "left": "106px",
                                        "top": "20px",
                                        "background": "radial-gradient(50% 50% at 50% 50%, rgba(94, 184, 148, 0.3) 0%, rgba(255, 255, 255, 0) 62.81%)",
                                        "backdropFilter": "blur(5px)",
                                        "zIndex": "1",
                                    }
                                ),
                                # Ellipse 7 (Blue gradient)
                                html.Div(
                                    style={
                                        "position": "absolute",
                                        "width": "1978px",
                                        "height": "1978px",
                                        "left": "350px",
                                        "top": "-989px",
                                        "background": "radial-gradient(50% 50% at 50% 50%, rgba(98, 203, 251, 0.3) 0%, rgba(255, 255, 255, 0) 62.81%)",
                                        "filter": "blur(7.68531px)",
                                        "zIndex": "1",
                                    }
                                ),
                            ]
                        ),
                        # Content overlay - all content in one unified section
                        html.Div(
                            style={
                                "position": "relative",
                                "zIndex": "2",
                                "display": "flex",
                                "flexDirection": "column",
                                "alignItems": "center",
                                "width": "100%",
                                "maxWidth": "931px",  # Max width for content
                                "margin": "0 auto",
                                "gap": "40px",  # Space between sections
                            },
                            children=[
                                # Main content section
                                html.Div(
                                    style={"textAlign": "center"},
                                    children=[
                                        # Main heading
                                        html.H1(
                                            "Advanced open-source project analysis by Augur",
                                            style={
                                                "fontSize": "40px",
                                                "fontWeight": "800",
                                                "fontFamily": '"Eloquia Display", sans-serif',
                                                "color": "#030303",  # Exact Figma color
                                                "marginBottom": "16px",
                                                "lineHeight": "110%",
                                                "textAlign": "center",
                                            },
                                        ),
                                        # Subtitle
                                        html.P(
                                            "8Knot hosts advanced analysis of open source projects, enriching the study of communities for community architects, developers, and Business Intelligence experts alike.",
                                            style={
                                                "fontSize": "16px",
                                                "fontWeight": "400",
                                                "fontFamily": '"Inter", system-ui, -apple-system, sans-serif',
                                                "color": "#030303",
                                                "lineHeight": "120%",
                                                "textAlign": "center",
                                                "maxWidth": "797px",
                                                "margin": "0 auto 52px auto",
                                            },
                                        ),
                                        # Search bar exactly like the target
                                        html.Div(
                                            style={
                                                "background": "#292929",
                                                "borderRadius": "20px",
                                                "border": "1px solid #C7C7C7",
                                                "padding": "8px 16px",
                                                "width": "472px",
                                                "height": "48px",
                                                "display": "flex",
                                                "alignItems": "center",
                                                "justifyContent": "space-between",
                                                "boxSizing": "border-box",
                                                "margin": "0 auto",
                                            },
                                            children=[
                                                dmc.MultiSelect(
                                                    id="projects",  # ID matches index_callbacks for functionality
                                                    searchable=True,
                                                    clearable=True,
                                                    placeholder="Search for organization and repositories",
                                                    nothingFound="No matching repos/orgs.",
                                                    variant="unstyled",
                                                    debounce=100,
                                                    data=[
                                                        {"label": "org: chaoss", "value": "chaoss"}
                                                    ],  # Default CHAOSS
                                                    value=["chaoss"],  # Default CHAOSS
                                                    style={
                                                        "fontSize": 15,
                                                        "zIndex": 99999,  # Higher z-index
                                                        "border": "none",
                                                        "width": "100%",
                                                        "background": "transparent",
                                                        "color": "#FAFAFA",  # Placeholder color
                                                    },
                                                    maxDropdownHeight=300,
                                                    dropdownPosition="bottom",  # Force dropdown to go down
                                                    className="landing-searchbar-dropdown",
                                                ),
                                            ],
                                        ),
                                        # Search button (hidden, functionality handled by MultiSelect)
                                        dbc.Button(
                                            "Search",
                                            id="search",
                                            size="lg",
                                            style={
                                                "display": "none"
                                            },  # Hidden as per Figma, functionality via MultiSelect
                                        ),
                                    ],
                                ),
                                # CTA section - now part of the same unified section with gradients
                                html.Div(
                                    style={"textAlign": "center", "marginTop": "80px"},  # Space from search section
                                    children=[
                                        html.P(
                                            "Is this your first time here?",
                                            style={
                                                "fontSize": "1rem",
                                                "marginBottom": "20px",
                                                "fontWeight": "500",
                                                "color": "#333333",
                                            },
                                        ),
                                        dbc.Button(
                                            [
                                                "Learn how 8Knot works ",
                                                html.I(className="fas fa-chevron-down", style={"marginLeft": "8px"}),
                                            ],
                                            id="learn-button",
                                            color="light",
                                            style={
                                                "background": "#f8f9fa",
                                                "color": "#333",
                                                "padding": "12px 25px",
                                                "borderRadius": "25px",
                                                "fontWeight": "500",
                                                "boxShadow": "0 2px 8px rgba(0,0,0,0.1)",
                                                "border": "1px solid #e9ecef",
                                                "cursor": "pointer",
                                            },
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                # Welcome content section - initially hidden
                html.Div(
                    id="welcome-content",
                    style={
                        "background": "rgba(255, 255, 255, 0.95)",  # Semi-transparent white for readability
                        "padding": "40px 0",
                        "display": "none",  # Hidden by default
                    },
                    children=[
                        dbc.Container(
                            children=[
                                dcc.Tabs(
                                    value="plotlyfiguretools",
                                    style={"marginBottom": "30px"},
                                    children=[
                                        dcc.Tab(
                                            label="Using 8Knot Visualizations",
                                            value="plotlyfiguretools",
                                            children=[plotly_tab_contents],
                                            style={"padding": "10px 20px"},
                                        ),
                                        dcc.Tab(
                                            label="How 8Knot Works",
                                            value="general",
                                            children=[general_tab_contents],
                                            style={"padding": "10px 20px"},
                                        ),
                                        dcc.Tab(
                                            label="Logging into Augur",
                                            value="auguraccount",
                                            children=[augur_tab_contents],
                                            style={"padding": "10px 20px"},
                                        ),
                                        dcc.Tab(
                                            label="Creating Project Groups",
                                            value="usergroup",
                                            children=[group_tab_contents],
                                            style={"padding": "10px 20px"},
                                        ),
                                    ],
                                )
                            ]
                        )
                    ],
                ),
                # Store to track if welcome content should be shown
                dcc.Store(id="show-welcome-content", data=False),
                # JavaScript for smooth scrolling to welcome content
                html.Div(id="scroll-trigger", style={"display": "none"}),
                html.Script(
                    """
                    // Function to observe when welcome content appears and scroll to it
                    function observeWelcomeContent() {
                        console.log('Setting up welcome content observer...');
                        const welcomeContent = document.getElementById('welcome-content');
                        if (welcomeContent) {
                            console.log('Welcome content element found');
                            const observer = new MutationObserver(function(mutations) {
                                mutations.forEach(function(mutation) {
                                    if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                                        const target = mutation.target;
                                        console.log('Style changed:', target.style.display);
                                        if (target.style.display === 'block') {
                                            console.log('Scrolling to welcome content...');
                                            setTimeout(function() {
                                                target.scrollIntoView({
                                                    behavior: 'smooth',
                                                    block: 'start'
                                                });
                                            }, 300); // Increased delay
                                        }
                                    }
                                });
                            });

                            observer.observe(welcomeContent, {
                                attributes: true,
                                attributeFilter: ['style']
                            });
                        } else {
                            console.log('Welcome content element not found');
                        }
                    }

                    // Start observing when DOM is ready
                    if (document.readyState === 'loading') {
                        document.addEventListener('DOMContentLoaded', observeWelcomeContent);
                    } else {
                        observeWelcomeContent();
                    }

                    // Also try after a short delay in case of dynamic content
                    setTimeout(observeWelcomeContent, 1000);
                    """
                ),
                # Hidden components for search functionality
                html.Div(
                    style={"display": "none"},
                    children=[
                        dcc.Store(id="cached-options", storage_type="session"),
                        dcc.Store(id="search-cache-init-hidden", storage_type="session"),
                        html.Div(id="cache-init-trigger"),
                        dbc.Button("Search", id="search"),
                        dbc.Alert(
                            children="Please ensure that your spelling is correct.",
                            id="help-alert",
                            dismissable=True,
                            fade=True,
                            is_open=False,
                            color="info",
                        ),
                        dbc.Alert(
                            children="List of repos",
                            id="repo-list-alert",
                            dismissable=True,
                            fade=True,
                            is_open=False,
                            color="light",
                        ),
                        dcc.Loading(
                            children=[html.Div(id="results-output-container")],
                            color="#667eea",
                            type="dot",
                        ),
                        dcc.Loading(
                            dbc.Badge(
                                children="Data Loaded",
                                id="data-badge",
                                color="success",
                                style={"display": "none"},
                            ),
                            type="cube",
                            color="#667eea",
                        ),
                    ],
                ),
            ],
        )
    ],
)

# Callback to handle Learn button and show/hide welcome content
@callback(
    [Output("welcome-content", "style"), Output("scroll-trigger", "children")],
    Input("learn-button", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_welcome_content(n_clicks):
    if n_clicks:
        # Show the welcome content when button is clicked
        style = {
            "background": "rgba(255, 255, 255, 0.95)",  # Semi-transparent white for readability
            "padding": "40px 0",
            "display": "block",
        }
        # Trigger scroll with JavaScript
        scroll_script = html.Script(
            f"""
            setTimeout(function() {{
                const welcomeContent = document.getElementById('welcome-content');
                if (welcomeContent) {{
                    console.log('Scrolling to welcome content via callback...');
                    welcomeContent.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}
            }}, 500);
            """
        )
        return style, scroll_script

    return {
        "background": "rgba(255, 255, 255, 0.95)",  # Semi-transparent white for readability
        "padding": "40px 0",
        "display": "none",
    }, html.Div()


# Note: Search callbacks are handled by the main index_callbacks.py file
