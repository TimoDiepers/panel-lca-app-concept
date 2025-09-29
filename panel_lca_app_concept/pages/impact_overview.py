import panel as pn
import panel_material_ui as pmu
from panel_lca_app_concept.data import STAGES, PRODUCTS, compute_footprint
from panel_lca_app_concept.charts import plot_stacked_bars, update_stacked_bars, plot_sankey, update_sankey


def _new_state():
    """Initialize state container for one session."""
    return {
        "source_df": None,
        "colors": None,
        "widgets": None,
    }


_fallback_state = _new_state()


def _get_state():
    """Return state scoped to the active Panel session when possible."""
    doc = getattr(pn.state, "curdoc", None)
    if doc is None:
        return _fallback_state

    state = getattr(doc, "_impact_overview_state", None)
    if state is None:
        state = _new_state()
        setattr(doc, "_impact_overview_state", state)
    return state

def initialize_results_data():
    """Initialize results data and charts"""
    # palette for bars (use PMU to keep your look)
    state = _get_state()
    state['colors'] = pmu.theme.generate_palette("#5a4fcf", n_colors=len(STAGES))
    state['source_df'] = compute_footprint(PRODUCTS[:5])

def get_impact_overview_widgets():
    """Get or create impact overview widgets (singleton pattern)"""
    state = _get_state()
    if state['widgets'] is not None:
        return state['widgets']

    state['widgets'] = create_impact_overview_widgets()
    return state['widgets']

def create_impact_overview_widgets():
    """Create widgets for impact overview page"""
    state = _get_state()

    if state['source_df'] is None:
        initialize_results_data()
    
    # Widgets
    products_mc = pmu.widgets.MultiChoice(
        name="Products", options=PRODUCTS, value=PRODUCTS[:5], sizing_mode="stretch_width"
    )
    normalize = pmu.widgets.Checkbox(name="Normalize bars (100%)", value=False)

    # Charts
    plotly_pane = pn.pane.Plotly(
        plot_stacked_bars(state['source_df'], normalize.value, state['colors']),
        sizing_mode="stretch_width",
        config={"responsive": True},
    )

    sankey_pane = pn.pane.Plotly(
        plot_sankey(state['source_df']), sizing_mode="stretch_width", config={"responsive": True}
    )

    # Callbacks
    def _recalc(_=None):
        state['source_df'] = compute_footprint(products_mc.value)
        update_stacked_bars(plotly_pane.object, state['source_df'], normalize.value, state['colors'])
        update_sankey(sankey_pane.object, state['source_df'])

    def _toggle_normalize(_):
        update_stacked_bars(plotly_pane.object, state['source_df'], normalize.value, state['colors'])

    def _on_theme_change(_):
        # re-apply backgrounds and line colors after theme flips
        update_stacked_bars(plotly_pane.object, state['source_df'], normalize.value, state['colors'])

    # Wire up callbacks
    normalize.param.watch(_toggle_normalize, "value")
    products_mc.param.watch(_recalc, "value")

    # Theme polling (if needed globally)
    _prev_theme = [str(getattr(pn.config, "theme", "dark"))]

    def _poll_theme():
        cur = str(getattr(pn.config, "theme", "dark"))
        if cur != _prev_theme[0]:
            _prev_theme[0] = cur
            _on_theme_change(None)

    # Add periodic callback if not already added globally
    try:
        pn.state.add_periodic_callback(_poll_theme, period=200, start=False)
    except:
        pass  # Already added or no event loop

    return {
        'products_mc': products_mc,
        'normalize': normalize,
        'plotly_pane': plotly_pane,
        'sankey_pane': sankey_pane,
    }

def create_impact_overview_view():
    """Create the impact overview page view"""
    widgets = get_impact_overview_widgets()

    header = pmu.pane.Markdown(
        "Explore PMI-LCA results through interactive visualizations."
    )

    results_tabs = pmu.Tabs(
        ("Stacked Bars", widgets['plotly_pane']),
        ("Sankey", widgets['sankey_pane']),
    )

    return pmu.Container(header, results_tabs)

def create_impact_overview_sidebar():
    """Create the impact overview page sidebar"""
    widgets = get_impact_overview_widgets()
    
    return pmu.Column(
        widgets['products_mc'],
        widgets['normalize'],
        sizing_mode="stretch_width",
    )
