import panel as pn
import panel_material_ui as pmu


def create_home_view():
    """Create the home page main content."""
    return pmu.Column(
        pmu.pane.Markdown("# Home"),
        pmu.pane.Markdown(
            "Welcome to a Demo.\n\n"
            "- Go to Setup to choose a project, database, and filter processes.\n"
            "- Open Results to explore stacked bars and Sankey diagrams.\n\n"
            "This is a placeholder home page with explanatory text."
        ),
        sizing_mode="stretch_width",
    )


def create_home_sidebar():
    """Create the home page sidebar content."""
    return pmu.Column(
        pmu.pane.Markdown("## About\nThis app demonstrates an LCA workflow.\nUse the menu to navigate."),
        sizing_mode="stretch_width",
    )