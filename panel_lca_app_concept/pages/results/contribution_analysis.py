import panel as pn
import panel_material_ui as pmu
from panel_lca_app_concept.data import STAGES, PRODUCTS, compute_footprint
from panel_lca_app_concept.charts import plot_stacked_bars, update_stacked_bars, plot_sankey, update_sankey

# Module-level shared state for results
_shared_state = {
    'source_df': None,
    'colors': None,
    'widgets': None,
}

def initialize_results_data():
    """Initialize results data and charts"""
    # palette for bars (use PMU to keep your look)
    _shared_state['colors'] = pmu.theme.generate_palette("#5a4fcf", n_colors=len(STAGES))
    _shared_state['source_df'] = compute_footprint(PRODUCTS[:5])

def get_contribution_analysis_widgets():
    """Get or create impact overview widgets (singleton pattern)"""
    if _shared_state['widgets'] is not None:
        return _shared_state['widgets']
    
    _shared_state['widgets'] = create_contribution_analysis_widgets()
    return _shared_state['widgets']

def create_contribution_analysis_widgets():
    """Create widgets for impact overview page"""
    
    if _shared_state['source_df'] is None:
        initialize_results_data()
    
    sankey_pane = pn.pane.Plotly(
        plot_sankey(_shared_state['source_df']), sizing_mode="stretch_width", config={"responsive": True}
    )

    return {
        'sankey_pane': sankey_pane,
    }

def create_contribution_analysis_view():
    """Create the impact overview page view"""
    widgets = get_contribution_analysis_widgets()
    
    header = pmu.pane.Markdown(
        "Stacked bar chart of carbon footprint by stage and product."
    )

    return pmu.Column(header, widgets['sankey_pane'], sizing_mode="stretch_width")

def create_contribution_analysis_sidebar():
    """Create the impact overview page sidebar"""
    widgets = get_contribution_analysis_widgets()
    
    return pmu.Markdown("This is a sankey showing multi-tier contributions.")