import panel as pn
import panel_material_ui as pmu
import pandas as pd
import re

from bw import list_projects, set_current_project, list_databases, list_processes


def create_calculation_setup_view():
    """Create the calculation setup page main content."""
    
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
    )

    current_db = None

    # Show an alert until a database is selected
    no_db_alert = pmu.Markdown("*To browse products & processes, please select a project and database first.*")

    df_processes = pd.DataFrame(columns=["Product", "Process", "Location"])
    
    def _on_db_select(event):
        nonlocal current_db, df_processes
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
        nonlocal df_processes
        try:
            df = df_processes
            df = contains_filter(df, filter_product.value, "Product")
            df = contains_filter(df, filter_process.value, "Process")
            df = contains_filter(df, filter_location.value, "Location")
            processes_tabulator.value = df
        except Exception as e:
            print(f"Apply Filters error: {e}")

    filter_button.on_click(_apply_filters)

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

    # Store references to widgets for sidebar access
    _calculation_setup_widgets = {
        'select_project': select_project,
        'select_db': select_db,
        'no_db_alert': no_db_alert,
        'filters_container': filters_container,
    }

    return pmu.Column(
        processes_section,
        fu_section,
        sizing_mode="stretch_width",
    ), _calculation_setup_widgets


def create_calculation_setup_sidebar(widgets):
    """Create the calculation setup page sidebar content."""
    return pmu.Column(
        widgets['select_project'],
        widgets['select_db'],
        widgets['no_db_alert'],
        widgets['filters_container'],
        sizing_mode="stretch_width",
    )