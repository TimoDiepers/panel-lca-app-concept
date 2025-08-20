import panel as pn
import panel_material_ui as pmu

from data import STAGES, PRODUCTS, compute_footprint
from charts import plot_stacked_bars, update_stacked_bars, plot_sankey, update_sankey


def create_impact_overview_view():
    """Create the impact overview page main content."""
    
    # palette for bars (use PMU to keep your look)
    colors = pmu.theme.generate_palette("#5a4fcf", n_colors=len(STAGES))

    # widgets
    products_mc = pmu.widgets.MultiChoice(
        name="Products", options=PRODUCTS, value=PRODUCTS[:5], sizing_mode="stretch_width"
    )
    normalize = pmu.widgets.Checkbox(name="Normalize bars (100%)", value=False)

    # panes
    source_df = compute_footprint(products_mc.value)
    plotly_pane = pn.pane.Plotly(
        plot_stacked_bars(source_df, normalize.value, colors),
        sizing_mode="stretch_width",
        config={"responsive": True},
    )

    sankey_pane = pn.pane.Plotly(
        plot_sankey(source_df), sizing_mode="stretch_width", config={"responsive": True}
    )

    # callbacks
    def _recalc(_=None):
        nonlocal source_df
        source_df = compute_footprint(products_mc.value)
        update_stacked_bars(plotly_pane.object, source_df, normalize.value, colors)
        update_sankey(sankey_pane.object, source_df)

    def _toggle_normalize(_):
        update_stacked_bars(plotly_pane.object, source_df, normalize.value, colors)

    def _on_theme_change(_):
        # re-apply backgrounds and line colors after theme flips
        update_stacked_bars(plotly_pane.object, source_df, normalize.value, colors)

    # watch theme by polling (pn.config.theme is not a Param)
    _prev_theme = [str(getattr(pn.config, "theme", "dark"))]

    def _poll_theme():
        cur = str(getattr(pn.config, "theme", "dark"))
        if cur != _prev_theme[0]:
            _prev_theme[0] = cur
            _on_theme_change(None)

    # Only add periodic callback if we have a running event loop
    try:
        pn.state.add_periodic_callback(_poll_theme, period=200, start=True)
    except RuntimeError:
        # No event loop running yet, skip for now
        pass

    normalize.param.watch(_toggle_normalize, "value")
    products_mc.param.watch(_recalc, "value")

    # layout
    header = pmu.pane.Markdown(
        "Stacked bar chart of carbon footprint by stage and product."
    )

    # --- Results page (main content) ---
    results_tabs = pn.Tabs(
        ("Stacked Bars", plotly_pane),
        ("Sankey", sankey_pane),
    )
    
    # Store references to widgets for sidebar access
    _impact_overview_widgets = {
        'products_mc': products_mc,
        'normalize': normalize,
    }

    return pmu.Column(header, results_tabs, sizing_mode="stretch_width"), _impact_overview_widgets


def create_impact_overview_sidebar(widgets):
    """Create the impact overview page sidebar content."""
    return pmu.Column(
        widgets['products_mc'],
        widgets['normalize'],
        sizing_mode="stretch_width",
    )