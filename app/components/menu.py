import panel_material_ui as pmu

def create_menu():
    """Create the main navigation menu"""
    return pmu.widgets.MenuList(
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
        margin=(0, 0, 20, 0), # space on bottom
        stylesheets=[
            ":host .MuiMenuItem-root.Mui-disabled {cursor: default !important; pointer-events: none;}"
        ]
    )