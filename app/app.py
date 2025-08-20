import panel as pn
import panel_material_ui as pmu
import pandas as pd

from theming import theme_config
from data import STAGES, PRODUCTS, compute_footprint
from charts import plot_stacked_bars, update_stacked_bars, plot_sankey, update_sankey
from bw import list_projects, set_current_project, list_databases, list_processes
from demo_databases import add_chem_demo_project
import re

pn.extension("plotly", theme="dark")
pn.extension('tabulator')

# palette for bars (use PMU to keep your look)
colors = pmu.theme.generate_palette("#5a4fcf", n_colors=len(STAGES))

add_chem_demo_project()

# --- Project & Database selection (set project once, then pick DB) ---
select_project = pmu.widgets.Select(
    label="Project",
    value=None,
    options=list_projects(),  # filled onload
    searchable=True,
)

def _on_project_select(event):
    print(f"Project selected: {event.new}")
    set_current_project(event.new)
    select_db.disabled = False
    select_db.options = list_databases()[::-1]

select_project.param.watch(_on_project_select, "value")

select_db = pmu.widgets.Select(
    label="Database",
    searchable=True,
    options=["Select project first"],  # filled on project select
    disabled=True,
    # visible=False,
    # margin=(10, 10, 40, 10), # space on bottom
)

current_db = None

# Show an alert until a database is selected
no_db_alert = pmu.Markdown("*To browse products & processes, please select a project and database first.*")


# pn.pane.Alert(    
#     "To browse products & processes, please select a project and database first.",
#     sizing_mode="stretch_width",
#     visible=True,
#     alert_type="info",
#     stylesheets=[":host(.alert) {border-radius: var(--mui-shape-borderRadius);}"],
# )

df_processes = pd.DataFrame(columns=["Product", "Process", "Location"])
def _on_db_select(event):
    global current_db
    global df_processes
    print(f"Database selected: {event.new}")
    current_db = event.new
    no_db_alert.visible = False
    select_db.loading = True
    filter_process.disabled = True
    filter_product.disabled = True
    filter_location.disabled = True
    filter_button.disabled = True
    df_processes = pd.DataFrame(
        [
            {
                "Product": p.get("reference product"),
                "Process": p.get("name"),
                "Location": p.get("location"),
            }
            for p in list_processes(current_db)
        ]
    )
    processes_tabulator.visible = True
    functional_unit.visible = True
    select_db.loading = False
    filter_process.disabled = False
    filter_product.disabled = False
    filter_location.disabled = False
    filter_button.disabled = False
    filters_container.visible = True
    
    processes_tabulator.value = df_processes


select_db.param.watch(_on_db_select, "value")

processes_tabulator = pn.widgets.Tabulator(
    df_processes,
    sizing_mode="stretch_width",
    layout="fit_data_stretch",
    name="Processes",
    pagination="remote",
    page_size=10,
    show_index=False,
    sorters=[{"field": "Product", "dir": "asc"}],
    disabled=True,
    selectable="toggle",
    stylesheets=[":host .tabulator {border-radius: var(--mui-shape-borderRadius);}"],
)

functional_unit = pn.widgets.Tabulator(
    pd.DataFrame(columns=["Amount", "Product", "Process", "Location"]),
    sizing_mode="stretch_width",
    layout="fit_data_stretch",
    name="Processes",
    show_index=False,
    sorters=[{"field": "Name", "dir": "asc"}],
    editors={
        "Product": None,
        "Process": None,
        "Location": None,
    },
    stylesheets=[":host .tabulator {border-radius: var(--mui-shape-borderRadius);}"],
)

def _on_process_click(event):
    df_sel = processes_tabulator.selected_dataframe
    df_sel.insert(0, "Amount", 1.0)
    functional_unit.value = df_sel

processes_tabulator.on_click(_on_process_click)

filter_product = pmu.widgets.TextInput(
    name="Filter Product",
)

filter_process = pmu.widgets.TextInput(
    name="Filter Process",
)

filter_location = pmu.widgets.TextInput(
    name="Filter Location",
)

def contains_filter(df, pattern, column):
    # Return unmodified DataFrame if no pattern or column missing
    if column not in df.columns:
        return df
    pat = str(pattern or "").strip()
    if not pat:
        return df

    # Parse quoted phrases and remaining words
    phrases = [q.strip().lower() for q in re.findall(r'"([^"]+)"', pat)]
    remainder = re.sub(r'"[^"]+"', " ", pat)
    words = [w.strip().lower() for w in remainder.split() if w.strip()]
    tokens = phrases + words

    if not tokens:
        return df

    s = df[column].fillna("").astype(str).str.lower()
    mask = pd.Series(True, index=df.index)
    for t in tokens:
        mask &= s.str.contains(t, regex=False, na=False)

    return df[mask]

processes_tabulator.add_filter(
    pn.bind(
        contains_filter,
        pattern=filter_product.param.value_input,
        column="Product",
    )
)
processes_tabulator.add_filter(pn.bind(contains_filter, pattern=filter_process.param.value_input, column="Process"))
processes_tabulator.add_filter(pn.bind(contains_filter, pattern=filter_location.param.value_input, column="Location"))

filter_button = pmu.widgets.Button(
    name="Apply Filters",
    button_type="primary",
    icon="filter_list",
    icon_size="2em",
    sizing_mode="stretch_width",
    variant="outlined"
)

def _apply_filters(event=None):
    # Apply current text filters to the processes table
    global df_processes
    try:
        df = df_processes
        df = contains_filter(df, filter_product.value, "Product")
        df = contains_filter(df, filter_process.value, "Process")
        df = contains_filter(df, filter_location.value, "Location")
        processes_tabulator.value = df
    except Exception as e:
        print(f"Apply Filters error: {e}")

filter_button.on_click(_apply_filters)

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
    global source_df
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


pn.state.add_periodic_callback(_poll_theme, period=200, start=True)

normalize.param.watch(_toggle_normalize, "value")
products_mc.param.watch(_recalc, "value")

# layout
header = pmu.pane.Markdown(
    "Stacked bar chart of carbon footprint by stage and product."
)

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
    margin=(0, 0, 20, 0), # space on bottom
    stylesheets=[
        ":host .MuiMenuItem-root.Mui-disabled {cursor: default !important; pointer-events: none;}"
    ]
)

# --- Setup page (main content) ---

# Processes section
_procs_header = pmu.pane.Markdown("""
## Browse Products & Processes

Please select the products and processes you want to include in the analysis.
""")

processes_section = pmu.Column(
    _procs_header,
    processes_tabulator,
    sizing_mode="stretch_width",
)

# Functional Unit section
_fu_header = pmu.pane.Markdown("""
## Functional Unit

Select products and processes to add to the functional unit by clicking on the corresponding row.
""")
fu_section = pmu.Column(
    _fu_header,
    functional_unit,
    sizing_mode="stretch_width",
)

processes_view = pmu.Column(
    processes_section,
    fu_section,
    sizing_mode="stretch_width",
)

# --- Results page (main content) ---
results_tabs = pn.Tabs(
    ("Stacked Bars", plotly_pane),
    ("Sankey", sankey_pane),
)
results_view = pmu.Column(header, results_tabs, sizing_mode="stretch_width")

# --- Sidebar content per page ---
filters_container = pmu.Column(
    pn.layout.Divider(
        stylesheets=[
            ":host hr {margin: 20px 10px; border: 0; border-top: 1px solid var(--mui-palette-divider); }"
        ],
    ),
    filter_product,
    filter_process,
    filter_location,
    filter_button,
    sizing_mode="stretch_width",
    visible=False
)

sidebar_process = pmu.Column(
    select_project,
    select_db,
    no_db_alert,
    filters_container,
    sizing_mode="stretch_width",
)

# --- Add Home page and make Results/Home dynamic ---
# Original Results sidebar content (kept for "Results" page)
_results_sidebar = pmu.Column(
    products_mc,
    normalize,
    sizing_mode="stretch_width",
)

# Home page (main) with dummy explanatory texts
home_view = pmu.Column(
    pmu.pane.Markdown("# Home"),
    pmu.pane.Markdown(
        "Welcome to a Demo.\n\n"
        "- Go to Setup to choose a project, database, and filter processes.\n"
        "- Open Results to explore stacked bars and Sankey diagrams.\n\n"
        "This is a placeholder home page with explanatory text."
    ),
    sizing_mode="stretch_width",
)

# Home sidebar (can be simple)
sidebar_home = pmu.Column(
    pmu.pane.Markdown("## About\nThis app demonstrates an LCA workflow.\nUse the menu to navigate."),
    sizing_mode="stretch_width",
)

def _label_of(v):
    return (v.get("label") if isinstance(v, dict) else getattr(v, "label", v))

# Simple mapping by menu label, no nested if/else or wrappers
_main_views = {
    "Home": home_view,
    "Calculation Setup": processes_view,
    "Impact Overview": results_view,
}
_sidebar_views = {
    "Home": sidebar_home,
    "Calculation Setup": sidebar_process,
    "Impact Overview": _results_sidebar,
}

# Set "Home" active initially
for it in menu.items:
    if _label_of(it) == "Home":
        menu.value = it
        break

main_switch = pn.bind(lambda v: _main_views.get(_label_of(v), home_view), menu.param.value)
sidebar_switch = pn.bind(lambda v: _sidebar_views.get(_label_of(v), sidebar_home), menu.param.value)

page = pmu.Page(
    main=[main_switch],
    sidebar=[menu, sidebar_switch],
    title="Demo App",
    theme_config=theme_config,
)
page.servable(title="Demo App")

if __name__ == "__main__":
    pn.serve(page, show=True)
