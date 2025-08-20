import panel_material_ui as pmu

def create_process_definition_view():
    """Create the process definition page view"""
    return pmu.Column(
        pmu.pane.Markdown("# Process Definition"),
        pmu.pane.Markdown(
            "This page is for defining and configuring process parameters.\n\n"
            "**Coming Soon**: Process definition functionality will be implemented here."
        ),
        sizing_mode="stretch_width",
    )

def create_process_definition_sidebar():
    """Create the process definition page sidebar"""
    return pmu.Column(
        pmu.pane.Markdown("## Process Definition Tools\n\nTools for process configuration will appear here."),
        sizing_mode="stretch_width",
    )