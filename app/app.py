import panel as pn
import panel_material_ui as pmu

from theming import theme_config
from demo_databases import add_chem_demo_project

# Import page modules
from pages.home import create_home_view, create_home_sidebar
from pages.modeling.process_definition import create_process_definition_view, create_process_definition_sidebar
from pages.modeling.calculation_setup import create_calculation_setup_view, create_calculation_setup_sidebar
from pages.results.impact_overview import create_impact_overview_view, create_impact_overview_sidebar
from pages.results.contribution_analysis import create_contribution_analysis_view, create_contribution_analysis_sidebar

pn.extension("plotly", theme="dark")
pn.extension('tabulator')

add_chem_demo_project()

# Helper function to get label from menu item
def _label_of(menu_item):
    """Extract label from menu item."""
    if isinstance(menu_item, dict):
        return menu_item.get("label", "")
    return ""

# Create menu
menu = pmu.widgets.MenuList(
    items=[
        {
            "label": "Home",
            "icon": "home_rounded",
        },
        {
            "label": "Modeling",
            "icon": "settings_rounded",
            "selectable": False,
            "items": [
                {'label': 'Process Definition', 'icon': 'handyman_rounded'},
                {'label': 'Calculation Setup', 'icon': 'calculate_rounded'},
            ]
        },
        {
            "label": "Results",
            "icon": "query_stats_rounded",
            "selectable": False,
            "items": [
                {'label': 'Impact Overview', 'icon': 'leaderboard_rounded'},
                {'label': 'Contribution Analysis', 'icon': 'pie_chart_rounded'},
            ]
        },
    ],
    sizing_mode="stretch_width",
    label="Menu",
    margin=(0, 0, 20, 0),  # space on bottom
    stylesheets=[
        ":host .MuiMenuItem-root.Mui-disabled {cursor: default !important; pointer-events: none;}"
    ]
)

# Page content mappings
_main_views = {}
_sidebar_views = {}

def setup_page_views():
    """Set up the page view mappings with proper initialization."""
    global _main_views, _sidebar_views
    
    # Home page
    _main_views["Home"] = create_home_view()
    _sidebar_views["Home"] = create_home_sidebar()
    
    # Process Definition page
    _main_views["Process Definition"] = create_process_definition_view()
    _sidebar_views["Process Definition"] = create_process_definition_sidebar()
    
    # Calculation Setup page
    calc_main, calc_widgets = create_calculation_setup_view()
    _main_views["Calculation Setup"] = calc_main
    _sidebar_views["Calculation Setup"] = create_calculation_setup_sidebar(calc_widgets)
    
    # Impact Overview page
    impact_main, impact_widgets = create_impact_overview_view()
    _main_views["Impact Overview"] = impact_main
    _sidebar_views["Impact Overview"] = create_impact_overview_sidebar(impact_widgets)
    
    # Contribution Analysis page
    _main_views["Contribution Analysis"] = create_contribution_analysis_view()
    _sidebar_views["Contribution Analysis"] = create_contribution_analysis_sidebar()

# Initialize page views
setup_page_views()

# URL to page mapping
url_to_page = {
    '/': 'Home',
    '/modeling/process-definition': 'Process Definition',
    '/modeling/calculation-setup': 'Calculation Setup',
    '/results/impact-overview': 'Impact Overview',
    '/results/contribution-analysis': 'Contribution Analysis',
}

page_to_url = {v: k for k, v in url_to_page.items()}

def update_url_from_menu(event):
    """Update URL when menu selection changes."""
    if hasattr(event, 'new') and event.new:
        label = _label_of(event.new)
        target_url = page_to_url.get(label)
        if target_url and pn.state.location:
            # Update URL without page reload
            pn.state.location.search = ''
            pn.state.location.pathname = target_url

def update_menu_from_url():
    """Update menu selection based on current URL."""
    if pn.state.location:
        current_path = pn.state.location.pathname or '/'
        current_page = url_to_page.get(current_path, 'Home')
        
        # Find and set the menu item
        for item in menu.items:
            if _label_of(item) == current_page:
                menu.value = item
                return
            elif 'items' in item:
                for subitem in item['items']:
                    if _label_of(subitem) == current_page:
                        menu.value = subitem
                        return

# Set up URL handling
if pn.state.location:
    pn.state.location.param.watch(lambda event: update_menu_from_url(), 'pathname')

# Set up menu handling
menu.param.watch(update_url_from_menu, 'value')

# Create reactive views based on menu selection
def get_main_view():
    """Get the main view for the current page."""
    if menu.value:
        label = _label_of(menu.value)
        return _main_views.get(label, _main_views["Home"])
    return _main_views["Home"]

def get_sidebar_view():
    """Get the sidebar view for the current page."""
    if menu.value:
        label = _label_of(menu.value)
        return _sidebar_views.get(label, _sidebar_views["Home"])
    return _sidebar_views["Home"]

# Create bound views that update when menu changes
main_switch = pn.bind(lambda v: _main_views.get(_label_of(v), _main_views["Home"]), menu.param.value)
sidebar_switch = pn.bind(lambda v: _sidebar_views.get(_label_of(v), _sidebar_views["Home"]), menu.param.value)

# Initialize based on current URL
update_menu_from_url()

# If no menu item is selected, default to Home
if not menu.value:
    for item in menu.items:
        if _label_of(item) == "Home":
            menu.value = item
            break

# Configure Panel to use absolute URLs for static resources
pn.config.global_css = []
pn.config.apply_theme = 'dark'

# Create the page with Material UI theme
page = pmu.Page(
    main=[main_switch],
    sidebar=[menu, sidebar_switch],
    title="Demo App",
    theme_config=theme_config,
)

def create_app():
    """Create the main application."""
    # Initialize URL handling for this instance
    update_menu_from_url()
    
    # If no menu item is selected, default based on current URL
    if not menu.value:
        if pn.state.location and pn.state.location.pathname:
            current_path = pn.state.location.pathname
            current_page = url_to_page.get(current_path, 'Home')
            
            # Find and set the appropriate menu item
            for item in menu.items:
                if _label_of(item) == current_page:
                    menu.value = item
                    break
                elif 'items' in item:
                    for subitem in item['items']:
                        if _label_of(subitem) == current_page:
                            menu.value = subitem
                            break
        else:
            # Default to Home
            for item in menu.items:
                if _label_of(item) == "Home":
                    menu.value = item
                    break
    
    # Return the page instance
    app_page = pmu.Page(
        main=[main_switch],
        sidebar=[menu, sidebar_switch], 
        title="Demo App",
        theme_config=theme_config,
    )
    return app_page

if __name__ == "__main__":
    # Solution: Use Panel's multi-route serving approach
    # Serve the same app from all routes to handle direct URL access and page refresh
    apps = {
        '/': create_app,
        '/modeling/process-definition': create_app,
        '/modeling/calculation-setup': create_app,
        '/results/impact-overview': create_app,
        '/results/contribution-analysis': create_app,
    }
    
    pn.serve(apps, show=True, port=5007, 
             allow_websocket_origin=["localhost:5007"])
