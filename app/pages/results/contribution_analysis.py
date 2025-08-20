import panel as pn
import panel_material_ui as pmu


def create_contribution_analysis_view():
    """Create the contribution analysis page main content."""
    return pmu.Column(
        pmu.pane.Markdown("# Contribution Analysis"),
        pmu.pane.Markdown(
            "This page provides detailed contribution analysis of LCA results.\n\n"
            "Here you can:\n"
            "- Analyze contributions by process\n"
            "- View contribution breakdowns by stage\n"
            "- Compare contribution patterns across products\n"
            "- Export detailed contribution data\n\n"
            "This is a placeholder for the contribution analysis functionality."
        ),
        sizing_mode="stretch_width",
    )


def create_contribution_analysis_sidebar():
    """Create the contribution analysis page sidebar content."""
    return pmu.Column(
        pmu.pane.Markdown("## Analysis Tools\nTools for detailed contribution analysis."),
        sizing_mode="stretch_width",
    )