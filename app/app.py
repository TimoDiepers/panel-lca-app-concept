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

# Route mapping for URL-based navigation (using query parameters)
ROUTE_MAP = {
    "": ("Home", create_home_view, create_home_sidebar),
    "home": ("Home", create_home_view, create_home_sidebar),
    "process-definition": ("Process Definition", create_process_definition_view, create_process_definition_sidebar),
    "calculation-setup": ("Calculation Setup", create_calculation_setup_view, create_calculation_setup_sidebar),
    "impact-overview": ("Impact Overview", create_impact_overview_view, create_impact_overview_sidebar),
    "contribution-analysis": ("Contribution Analysis", create_contribution_analysis_view, create_contribution_analysis_sidebar),
}

# Menu label to route mapping (for menu item clicks)
MENU_TO_ROUTE = {
    "Home": "",
    "Process Definition": "process-definition",
    "Calculation Setup": "calculation-setup",
    "Impact Overview": "impact-overview",
    "Contribution Analysis": "contribution-analysis",
}

class App:
    def __init__(self):
        self.menu = create_menu()
        self.location = None  # Will be set when app is served
        
        # Create containers for main content and sidebar
        self.main_container = pn.Column(sizing_mode="stretch_width")
        self.sidebar_container = pn.Column(sizing_mode="stretch_width")
        
        # Initialize views with default route
        self._update_views("")
        
        # Watch for menu changes
        self.menu.param.watch(self._on_menu_change, "value")
        
        # Set initial menu selection
        self._sync_menu_with_location("")
        
        # Create the page
        self.page = pmu.Page(
            main=[self.main_container],
            sidebar=[self.menu, self.sidebar_container],
            title="Demo App",
            theme_config=theme_config,
        )
        
        # Set up location watching when page is served
        pn.state.onload(self._setup_location_watching)

    def _setup_location_watching(self):
        """Set up location watching when the app is loaded"""
        self.location = pn.state.location
        if self.location and hasattr(self.location, 'search'):
            # Watch for location changes (browser navigation)
            self.location.param.watch(self._on_location_change, "search")
            # Update to current location
            current_route = self._get_current_route()
            self._update_views(current_route)
            self._sync_menu_with_location(current_route)

    def _label_of(self, v):
        """Extract label from menu item"""
        return (v.get("label") if isinstance(v, dict) else getattr(v, "label", v))

    def _get_current_route(self):
        """Get current route from location search parameters"""
        if self.location and hasattr(self.location, 'search'):
            search = self.location.search or ""
            # Extract page parameter from search string
            if "page=" in search:
                # Parse page=value from search string
                for param in search.split("&"):
                    if param.startswith("page="):
                        return param.split("=", 1)[1]
            return ""
        return ""

    def _update_views(self, route=None):
        """Update main and sidebar views based on route"""
        if route is None:
            route = self._get_current_route()
        
        # Get route configuration
        route_config = ROUTE_MAP.get(route, ROUTE_MAP[""])
        label, main_func, sidebar_func = route_config
        
        # Update containers
        try:
            main_view = main_func()
            sidebar_view = sidebar_func()
            
            self.main_container.clear()
            self.main_container.append(main_view)
            
            self.sidebar_container.clear()
            self.sidebar_container.append(sidebar_view)
            
        except Exception as e:
            print(f"Error updating views for route {route}: {e}")
            # Fallback to home
            if route != "":
                self._update_views("")

    def _on_menu_change(self, event):
        """Handle menu item selection"""
        if event.new is None:
            return
        
        label = self._label_of(event.new)
        route = MENU_TO_ROUTE.get(label, "")
        
        # Update location to trigger route change
        if self.location and hasattr(self.location, 'search'):
            if route:
                self.location.search = f"page={route}"
            else:
                self.location.search = ""
        else:
            # Fallback for when location is not available
            self._update_views(route)

    def _on_location_change(self, event):
        """Handle browser navigation (back/forward buttons, URL changes)"""
        route = event.new or "/"
        self._update_views(route)
        self._sync_menu_with_location()

    def _sync_menu_with_location(self, route=None):
        """Sync menu selection with current location"""
        if route is None:
            route = self._get_current_route()
        route_config = ROUTE_MAP.get(route, ROUTE_MAP[""])
        target_label = route_config[0]
        
        # Find and select the corresponding menu item
        for item in self.menu.items:
            if self._label_of(item) == target_label:
                self.menu.value = item
                return
            # Check nested items
            if "items" in item:
                for sub_item in item["items"]:
                    if self._label_of(sub_item) == target_label:
                        self.menu.value = sub_item
                        return

# Create and serve the app
app = App()
app.page.servable(title="Demo App")

if __name__ == "__main__":
    pn.serve(app.page, show=True)