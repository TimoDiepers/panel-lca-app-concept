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

def create_page_app(page_type):
    """Create a page application for the given page type."""
    
    # Create menu with current page highlighted
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

    # Navigation helper function
    def navigate_to_url(url):
        """Navigate to a URL using JavaScript."""
        js_code = f"""
        <script>
        window.location.href = '{url}';
        </script>
        """
        return pn.pane.HTML(js_code, width=0, height=0)

    # Add navigation handler to the page
    nav_pane = pn.pane.HTML("", width=0, height=0)
    
    # Handle menu clicks to navigate to other pages
    def handle_menu_click(event):
        if hasattr(event, 'new') and event.new:
            item = event.new
            if isinstance(item, dict):
                label = item.get('label', '')
                
                # Map labels to URLs
                url_map = {
                    'Home': '/',
                    'Process Definition': '/modeling/process-definition',
                    'Calculation Setup': '/modeling/calculation-setup',
                    'Impact Overview': '/results/impact-overview',
                    'Contribution Analysis': '/results/contribution-analysis',
                }
                
                target_url = url_map.get(label)
                if target_url:
                    # Update navigation pane to trigger browser navigation
                    nav_pane.object = f"""
                    <script>
                    if (window.location.pathname !== '{target_url}') {{
                        window.location.href = '{target_url}';
                    }}
                    </script>
                    """
    
    menu.param.watch(handle_menu_click, 'value')

    # Create page content based on page type
    if page_type == 'home':
        main_view = create_home_view()
        sidebar_view = create_home_sidebar()
        # Set home as selected
        for item in menu.items:
            if item.get('label') == 'Home':
                menu.value = item
                break
                
    elif page_type == 'modeling/process-definition':
        main_view = create_process_definition_view()
        sidebar_view = create_process_definition_sidebar()
        # Set Process Definition as selected
        for item in menu.items:
            if 'items' in item:
                for subitem in item['items']:
                    if subitem.get('label') == 'Process Definition':
                        menu.value = subitem
                        break
                        
    elif page_type == 'modeling/calculation-setup':
        main_view, widgets = create_calculation_setup_view()
        sidebar_view = create_calculation_setup_sidebar(widgets)
        # Set Calculation Setup as selected
        for item in menu.items:
            if 'items' in item:
                for subitem in item['items']:
                    if subitem.get('label') == 'Calculation Setup':
                        menu.value = subitem
                        break
                        
    elif page_type == 'results/impact-overview':
        main_view, widgets = create_impact_overview_view()
        sidebar_view = create_impact_overview_sidebar(widgets)
        # Set Impact Overview as selected
        for item in menu.items:
            if 'items' in item:
                for subitem in item['items']:
                    if subitem.get('label') == 'Impact Overview':
                        menu.value = subitem
                        break
                        
    elif page_type == 'results/contribution-analysis':
        main_view = create_contribution_analysis_view()
        sidebar_view = create_contribution_analysis_sidebar()
        # Set Contribution Analysis as selected
        for item in menu.items:
            if 'items' in item:
                for subitem in item['items']:
                    if subitem.get('label') == 'Contribution Analysis':
                        menu.value = subitem
                        break
    else:
        # Default to home
        main_view = create_home_view()
        sidebar_view = create_home_sidebar()

    # Create the page
    page = pmu.Page(
        main=[main_view, nav_pane],
        sidebar=[menu, sidebar_view],
        title="Demo App",
        theme_config=theme_config,
    )
    
    return page


def home_app():
    """Home page application."""
    return create_page_app('home')


def process_definition_app():
    """Process Definition page application."""
    return create_page_app('modeling/process-definition')


def calculation_setup_app():
    """Calculation Setup page application."""
    return create_page_app('modeling/calculation-setup')


def impact_overview_app():
    """Impact Overview page application."""
    return create_page_app('results/impact-overview')


def contribution_analysis_app():
    """Contribution Analysis page application."""
    return create_page_app('results/contribution-analysis')


# Define the routing dictionary for Panel's serve function
apps = {
    '': home_app,  # Root path
    'modeling/process-definition': process_definition_app,
    'modeling/calculation-setup': calculation_setup_app,
    'results/impact-overview': impact_overview_app,
    'results/contribution-analysis': contribution_analysis_app,
}


if __name__ == "__main__":
    pn.serve(apps, show=True, location=True)
