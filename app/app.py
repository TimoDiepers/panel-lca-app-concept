import panel as pn
import panel_material_ui as pmu

from theming import theme_config
from demo_databases import add_chem_demo_project

# Import page components
from components.menu import create_menu
from pages.home import create_home_view, create_home_sidebar
from pages.modeling.process_definition import create_process_definition_view, create_process_definition_sidebar
from pages.modeling.calculation_setup import create_calculation_setup_view, create_calculation_setup_sidebar
from pages.results.impact_overview import create_impact_overview_view, create_impact_overview_sidebar
from pages.results.contribution_analysis import create_contribution_analysis_view, create_contribution_analysis_sidebar

# Initialize Panel extensions
pn.extension("plotly", theme="dark")
pn.extension('tabulator')

# Initialize demo data
add_chem_demo_project()

# Route mapping for hash-based navigation
ROUTES = {
    "home": (create_home_view, create_home_sidebar),
    "modeling/process-definition": (create_process_definition_view, create_process_definition_sidebar),
    "modeling/calculation-setup": (create_calculation_setup_view, create_calculation_setup_sidebar),
    "results/impact-overview": (create_impact_overview_view, create_impact_overview_sidebar),
    "results/contribution-analysis": (create_contribution_analysis_view, create_contribution_analysis_sidebar),
}

class App:
    def __init__(self):
        self.menu = create_menu()
        
        # Create containers for main content and sidebar
        self.main_container = pn.Column(sizing_mode="stretch_width")
        self.sidebar_container = pn.Column(sizing_mode="stretch_width")
        
        # Set up menu click handler
        self.menu.param.watch(self._on_menu_select, "value")
        
        # Initialize with home view
        self._render_route("home")
        
        # Create the page
        self.page = pmu.Page(
            main=[self.main_container],
            sidebar=[self.menu, self.sidebar_container],
            title="Demo App",
            theme_config=theme_config,
        )
        
        # Set up location watching when page is served
        pn.state.onload(self._setup_routing)

    def _setup_routing(self):
        """Set up hash-based routing when the app is loaded"""
        # Check if location is available (when running in server context)
        if not pn.state.location:
            return
            
        # Set initial route if no hash is present
        if not (pn.state.location.hash or "").lstrip("#/"):
            self.set_route("home")
        
        # Initial render
        self.render_from_location()
        
        # Watch for hash changes (browser back/forward, URL changes)
        pn.state.location.param.watch(self.render_from_location, "hash")

    def set_route(self, path: str):
        """Set the current route using hash"""
        if pn.state.location:
            pn.state.location.hash = f"#{path}"

    def get_route(self) -> str:
        """Get current route from hash, defaulting to 'home'"""
        if not pn.state.location:
            return "home"
        return (pn.state.location.hash or "").lstrip("#/").strip("/") or "home"

    def resolve_view(self, path: str):
        """Get the view functions for a given path"""
        return ROUTES.get(path, ROUTES["home"])

    def _flatten(self, items):
        """Yield dict-like items depth-first for menu traversal"""
        if not items:
            return
        for it in items:
            if isinstance(it, dict):
                yield it
                # Recurse into children if any
                children = it.get("items") or []
                for ch in self._flatten(children):
                    yield ch

    def select_menu_item_by_path(self, path: str):
        """Highlight the menu item whose custom 'path' matches"""
        for it in self._flatten(self.menu.items):
            if it.get("path") == path:
                self.menu.value = it
                return
        # If nothing matches, clear selection
        self.menu.value = None

    def _on_menu_select(self, event):
        """React to menu clicks: update hash for navigation"""
        it = event.new
        if not it:
            return
        
        # Get path from menu item
        path = it.get("path") if isinstance(it, dict) else None
        if path:
            self.set_route(path)

    def render_from_location(self, _=None):
        """Update view and menu selection based on current hash"""
        path = self.get_route()
        self._render_route(path)

    def _render_route(self, path: str):
        """Render the given route path"""
        try:
            # Get view functions for current path
            main_func, sidebar_func = self.resolve_view(path)
            
            # Update main content
            main_view = main_func()
            self.main_container.clear()
            self.main_container.append(main_view)
            
            # Update sidebar content
            sidebar_view = sidebar_func()
            self.sidebar_container.clear()
            self.sidebar_container.append(sidebar_view)
            
            # Update menu selection
            self.select_menu_item_by_path(path)
            
        except Exception as e:
            print(f"Error rendering route {path}: {e}")
            # Fallback to home if there's an error
            if path != "home":
                self._render_route("home")

# Create and serve the app
app = App()
app.page.servable(title="Demo App")

if __name__ == "__main__":
    pn.serve(app.page, show=True)