import panel as pn
import panel_material_ui as pmu

from panel_lca_app_concept.theming import theme_config
from panel_lca_app_concept.demo_databases import add_chem_demo_project

# Import page components
from panel_lca_app_concept.pages.home import create_home_view
from panel_lca_app_concept.pages.calculation_setup import create_calculation_setup_view
from panel_lca_app_concept.pages.impact_overview import create_impact_overview_view

# Initialize Panel extensions
pn.extension("plotly", "tabulator", theme="dark", notifications=True)
pn.config.css_files.append("https://fonts.googleapis.com/icon?family=Material+Icons+Outlined")

# Initialize demo data
add_chem_demo_project()

# Route mapping for hash-based navigation
ROUTES = {
    "home": create_home_view,
    "modeling/calculation-setup": create_calculation_setup_view,
    "results/impact-overview": create_impact_overview_view,
}

class App:
    def __init__(self):
        # Create containers for main content
        self.main_container = pn.Column(sizing_mode="stretch_width")

        # Create nav buttons BEFORE any rendering so highlight logic works
        self.home_button = pmu.Button(
            icon="home_outlined",
            icon_size="2em",
            label="Home",
            color="light",
            variant="text",
            width=170,
            stylesheets=[
                ":host .MuiButton-text {font-size: 14px;} .MuiIcon-root {margin-right: 8px; font-family: 'Material Icons Outlined' !important;}"
            ],
        )
        self.modeling_button = pmu.Button(
            icon="settings_outlined",
            icon_size="2em",
            label="Modeling",
            color="light",
            variant="text",
            width=170,
            stylesheets=[
                ":host .MuiButton-text {font-size: 14px;} .MuiIcon-root {margin-right: 8px; font-family: 'Material Icons Outlined' !important;}"
            ],
        )
        self.results_button = pmu.Button(
            icon="insert_chart_outlined",
            icon_size="2em",
            label="Results",
            color="light",
            variant="text",
            width=170,
            stylesheets=[
                ":host .MuiButton-text {font-size: 14px;} .MuiIcon-root {margin-right: 8px; font-family: 'Material Icons Outlined' !important;}"
            ],
        )

        self.home_button.on_click(lambda event: self.set_route("home"))
        self.modeling_button.on_click(lambda event: self.set_route("modeling/calculation-setup"))
        self.results_button.on_click(lambda event: self.set_route("results/impact-overview"))

        self.BUTTON_MAPPING = {
            "home": self.home_button,
            "modeling/calculation-setup": self.modeling_button,
            "results/impact-overview": self.results_button,
        }

        nav = pn.Row(
           self.home_button, self.modeling_button, self.results_button,
            width=600,
            # sizing_mode="stretch_width",
            styles={
                "align-items": "center",
                "justify-content": "space-around",
                "margin-left": "auto",
                "margin-right": "auto",
            },
        )

        # self.page = pn.Column(
        #     nav, self.main_container,
        #     sizing_mode="stretch_width",
        #     # theme_config=theme_config,
        # )
        # Create the page
        self.page = pmu.Page(
            header=[nav],
            main=[self.main_container],
            # sidebar=[
            #     self.menu,
            #     pn.layout.Divider(
            #         stylesheets=[
            #             ":host hr {margin: 0px 10px 0 10px; border: 0; border-top: 1px solid var(--mui-palette-divider); }"
            #         ],
            #     ),
            #     self.sidebar_container,
            # ],
            # sidebar_open=False,
            # sidebar_variant="temporary",
            title="PMI-LCA Tool",
            theme_config=theme_config,
        )

        # Set up routing once the page is loaded (ensures hash is available on reload)
        pn.state.onload(self._setup_routing)

    def _setup_routing(self):
        """Set up hash-based routing when the app is loaded"""
        loc = pn.state.location
        if not loc:
            # Fallback when not in a server context
            self._render_route("home")
            return

        # Use current hash if present (supports deep-link reload)
        path = (loc.hash or "").lstrip("#/").strip("/") or "home"
        self._highlight_active_button(path)
        self._render_route(path)

        # Watch for future hash changes (back/forward, button clicks)
        loc.param.watch(self.render_from_location, "hash")

    def _highlight_active_button(self, path: str):
        default_ss = [
            ":host .MuiButton-text {font-size: 14px; font-weight: 400;} .MuiIcon-root {font-family: 'Material Icons Outlined' !important;}"
        ]
        highlighted_ss = [
            ":host .MuiButton-root {background: rgba(255, 255, 255, 0.08);} .MuiButton-text {font-size: 14px; font-weight: 600;} .MuiIcon-root {font-family: 'Material Icons' !important;}"
        ]

        config = {
            self.home_button: {
                "default": (default_ss, "home_outlined"),
                "highlighted": (highlighted_ss, "home"),
            },
            self.modeling_button: {
                "default": (default_ss, "settings_outlined"),
                "highlighted": (highlighted_ss, "settings"),
            },
            self.results_button: {
                "default": (default_ss, "insert_chart_outlined"),
                "highlighted": (highlighted_ss, "insert_chart"),
            },
        }

        # Determine active button once
        active_btn = self.BUTTON_MAPPING.get(path, self.home_button)

        # Iterate once, only change if needed to avoid flicker
        for btn in (self.home_button, self.modeling_button, self.results_button):
            if btn is active_btn:
                desired_ss, desired_icon = config[btn]["highlighted"]
            else:
                desired_ss, desired_icon = config[btn]["default"]

            if btn.stylesheets != desired_ss:
                btn.stylesheets = desired_ss

            if btn.icon != desired_icon:
                btn.icon = desired_icon

    def set_route(self, path: str):
        """Set the current route using hash"""
        self._highlight_active_button(path)
        if pn.state.location:
            pn.state.location.hash = f"#{path}"

    def get_route(self) -> str:
        """Get current route from hash, defaulting to 'home'"""
        if not pn.state.location:
            return "home"
        return (pn.state.location.hash or "").lstrip("#/").strip("/") or "home"

    def resolve_view(self, path: str):
        """Get the view function for a given path"""
        return ROUTES.get(path, ROUTES["home"])

    def render_from_location(self, _=None):
        """Update view and menu selection based on current hash"""
        path = self.get_route()
        self._highlight_active_button(path)
        self._render_route(path)

    def _render_route(self, path: str):
        """Render the given route path"""
        try:
            # Get view function for current path
            main_func = self.resolve_view(path)

            # Update main content
            main_view = main_func()
            self.main_container.clear()
            self.main_container.append(main_view)

        except Exception as e:
            print(f"Error rendering route {path}: {e}")
            # Fallback to home if there's an error
            if path != "home":
                self._render_route("home")

# Create and serve the app
app = App()
app.page.servable(title="PMI-LCA Tool")

if __name__ == "__main__":
    pn.serve(app.page, show=True)
