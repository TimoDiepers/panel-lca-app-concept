import panel as pn
import panel_material_ui as pmu


def create_process_definition_view():
    """Create the process definition page main content."""
    return pmu.Column(
        pmu.pane.Markdown("# Process Definition"),
        pmu.pane.Markdown(
            "This page is for defining and managing LCA processes.\n\n"
            "Here you can:\n"
            "- Define new processes\n"
            "- Edit existing process parameters\n"
            "- Configure process relationships\n\n"
            "This is a placeholder for the process definition functionality."
        ),
        sizing_mode="stretch_width",
    )


def create_process_definition_sidebar():
    """Create the process definition page sidebar content."""
    return pmu.Column(
        pmu.pane.Markdown("## Process Tools\nTools for process definition and management."),
        sizing_mode="stretch_width",
    )