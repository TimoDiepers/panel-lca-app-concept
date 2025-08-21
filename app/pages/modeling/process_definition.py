import panel as pn
import panel_material_ui as pmu
import pandas as pd
from bw import list_projects, set_current_project, list_databases, list_processes, create_process, add_input, list_process_inputs

# Module-level shared state for process definition
_shared_state = {
    'current_project': None,
    'current_db': None,
    'current_process': None,
    'df_processes': pd.DataFrame(columns=["Product", "Process", "Location"]),
    'df_inputs': pd.DataFrame(columns=["Amount", "Input Product", "Input Process", "Input Location"]),
    'widgets': None,
}

def get_process_definition_widgets():
    """Get or create process definition widgets (singleton pattern)"""
    if _shared_state['widgets'] is not None:
        return _shared_state['widgets']
    
    _shared_state['widgets'] = create_process_definition_widgets()
    return _shared_state['widgets']

def create_process_definition_widgets():
    """Create all widgets for process definition page"""

    # Project & Database selection
    select_project = pmu.widgets.Select(
        label="Project",
        value=None,
        options=list_projects(),
        searchable=True,
    )

    select_db = pmu.widgets.Select(
        label="Database",
        searchable=True,
        options=["Select project first"],
        disabled=True,
    )

    no_db_alert = pmu.Markdown("*To define processes, please select a project and database first.*")

    # Process creation form
    process_name_input = pmu.widgets.TextInput(
        label="Process Name",
        placeholder="Enter process name",
        disabled=True,
    )
    
    process_product_input = pmu.widgets.TextInput(
        label="Reference Product",
        placeholder="Enter reference product",
        disabled=True,
    )
    
    process_location_input = pmu.widgets.TextInput(
        label="Location",
        placeholder="Enter location (e.g., GLO, US, etc.)",
        disabled=True,
    )
    
    process_unit_input = pmu.widgets.TextInput(
        label="Unit",
        placeholder="Enter unit (e.g., kg, MJ, etc.)",
        disabled=True,
    )
    
    process_amount_input = pmu.widgets.FloatInput(
        label="Production Amount",
        value=1.0,
        step=0.01,
        disabled=True,
    )

    create_process_button = pmu.widgets.Button(
        name="Create Process",
        button_type="primary",
        icon="add",
        icon_size="2em",
        sizing_mode="stretch_width",
        disabled=True,
    )

    # Tables
    processes_tabulator = pn.widgets.Tabulator(
        _shared_state['df_processes'],
        sizing_mode="stretch_width",
        widths={
            "Product": "25%",
            "Process": "65%",
            "Location": "10%",
        },
        name="Processes",
        pagination="remote",
        page_size=10,
        show_index=False,
        sorters=[{"field": "Process", "dir": "asc"}],
        disabled=True,
        selectable="checkboxes",
        stylesheets=[":host .tabulator {border-radius: var(--mui-shape-borderRadius);}"],
    )

    inputs_tabulator = pn.widgets.Tabulator(
        _shared_state['df_inputs'],
        buttons={
            "delete": "<span class='material-icons'>delete_forever</span>",
        },
        sizing_mode="stretch_width",
        widths={
            "Amount": "15%",
            "Input Product": "25%",
            "Input Process": "45%",
            "Input Location": "10%",
            "delete": "5%",
        },
        name="Process Inputs",
        show_index=False,
        sorters=[{"field": "Input Process", "dir": "asc"}],
        editors={
            "Amount": "number",
            "Input Product": None,
            "Input Process": None,
            "Input Location": None,
        },
        stylesheets=[
            ":host .tabulator {border-radius: var(--mui-shape-borderRadius);}"
        ],
        visible=False,
    )

    # Callbacks
    def _on_project_select(event):
        print(f"Project selected: {event.new}")
        _shared_state['current_project'] = event.new
        set_current_project(event.new)
        select_db.disabled = False
        select_db.options = list_databases()[::-1]

    def _on_db_select(event):
        print(f"Database selected: {event.new}")
        _shared_state['current_db'] = event.new
        no_db_alert.visible = False
        select_db.loading = True
        
        # Enable process creation form
        process_name_input.disabled = False
        process_product_input.disabled = False
        process_location_input.disabled = False
        process_unit_input.disabled = False
        process_amount_input.disabled = False
        create_process_button.disabled = False
        
        set_current_project(_shared_state['current_project'])
        _shared_state['df_processes'] = pd.DataFrame(
            [
                {
                    "Product": p.get("reference product"),
                    "Process": p.get("name"),
                    "Location": p.get("location"),
                }
                for p in list_processes(_shared_state['current_db'])
            ]
        )
        processes_tabulator.value = _shared_state['df_processes']
        select_db.loading = False
        processes_tabulator.visible = True
        processes_tabulator.disabled = False

    def _on_create_process_click(event):
        if not all([process_name_input.value, process_product_input.value, 
                   process_location_input.value, process_unit_input.value]):
            print("Please fill in all required fields")
            return
        
        try:
            create_process_button.loading = True
            new_process = create_process(
                db=_shared_state['current_db'],
                name=process_name_input.value,
                product=process_product_input.value,
                location=process_location_input.value,
                unit=process_unit_input.value,
                process_production_amount=process_amount_input.value
            )
            
            # Refresh the processes table
            _shared_state['df_processes'] = pd.DataFrame(
                [
                    {
                        "Product": p.get("reference product"),
                        "Process": p.get("name"),
                        "Location": p.get("location"),
                    }
                    for p in list_processes(_shared_state['current_db'])
                ]
            )
            processes_tabulator.value = _shared_state['df_processes']
            
            # Clear the form
            process_name_input.value = ""
            process_product_input.value = ""
            process_location_input.value = ""
            process_unit_input.value = ""
            process_amount_input.value = 1.0
            
            print(f"Process created successfully: {new_process}")
            
        except Exception as e:
            print(f"Error creating process: {e}")
        finally:
            create_process_button.loading = False

    def _on_process_select(event):
        if not event.new:
            return
            
        # Get selected process info
        selected_rows = processes_tabulator.selection
        if not selected_rows:
            inputs_tabulator.visible = False
            return
            
        selected_row = selected_rows[0]
        process_name = _shared_state['df_processes'].iloc[selected_row]["Process"]
        process_product = _shared_state['df_processes'].iloc[selected_row]["Product"]
        process_location = _shared_state['df_processes'].iloc[selected_row]["Location"]
        
        _shared_state['current_process'] = {
            'name': process_name,
            'product': process_product,
            'location': process_location,
            'db': _shared_state['current_db']
        }
        
        # Load existing inputs for this process
        try:
            inputs = list_process_inputs(
                _shared_state['current_db'],
                process_name,
                process_product,
                process_location
            )
            
            _shared_state['df_inputs'] = pd.DataFrame(
                [
                    {
                        "Amount": edge.amount,
                        "Input Product": edge.input.get("reference product", ""),
                        "Input Process": edge.input.get("name", ""),
                        "Input Location": edge.input.get("location", ""),
                    }
                    for edge in inputs
                ]
            )
            inputs_tabulator.value = _shared_state['df_inputs']
            inputs_tabulator.visible = True
            
        except Exception as e:
            print(f"Error loading process inputs: {e}")
            _shared_state['df_inputs'] = pd.DataFrame(columns=["Amount", "Input Product", "Input Process", "Input Location"])
            inputs_tabulator.value = _shared_state['df_inputs']
            inputs_tabulator.visible = True

    def _on_process_click(event):
        """Handle clicking on a process in the table to add as input"""
        if not _shared_state['current_process']:
            print("Please select a process first to add inputs to")
            return
            
        # Get the row index from the event and extract data from the dataframe
        row_index = event.row
        if row_index is None or row_index >= len(_shared_state['df_processes']):
            print("Invalid row clicked")
            return
            
        row_data = _shared_state['df_processes'].iloc[row_index]
        try:
            add_input(
                process_db=_shared_state['current_process']['db'],
                process_name=_shared_state['current_process']['name'],
                process_product=_shared_state['current_process']['product'],
                process_location=_shared_state['current_process']['location'],
                input_db=_shared_state['current_db'],
                input_name=row_data["Process"],
                input_product=row_data["Product"],
                input_location=row_data["Location"],
                amount=1.0  # Default amount, user can edit later
            )
            
            # Refresh inputs table
            inputs = list_process_inputs(
                _shared_state['current_process']['db'],
                _shared_state['current_process']['name'],
                _shared_state['current_process']['product'],
                _shared_state['current_process']['location']
            )
            
            _shared_state['df_inputs'] = pd.DataFrame(
                [
                    {
                        "Amount": edge.amount,
                        "Input Product": edge.input.get("reference product", ""),
                        "Input Process": edge.input.get("name", ""),
                        "Input Location": edge.input.get("location", ""),
                    }
                    for edge in inputs
                ]
            )
            inputs_tabulator.value = _shared_state['df_inputs']
            
            print(f"Added input: {row_data['Process']}")
            
        except Exception as e:
            print(f"Error adding input: {e}")
            import traceback
            traceback.print_exc()

    # Wire up callbacks
    select_project.param.watch(_on_project_select, "value")
    select_db.param.watch(_on_db_select, "value")
    create_process_button.on_click(_on_create_process_click)
    processes_tabulator.param.watch(_on_process_select, "selection")
    processes_tabulator.on_click(_on_process_click)

    # Create process form container
    process_form = pmu.Column(
        pn.layout.Divider(
            stylesheets=[
                ":host hr {margin: 20px 10px; border: 0; border-top: 1px solid var(--mui-palette-divider); }"
            ],
        ),
        pmu.pane.Markdown("### Create New Process"),
        process_name_input,
        process_product_input,
        process_location_input,
        process_unit_input,
        process_amount_input,
        create_process_button,
        sizing_mode="stretch_width",
    )

    return {
        'select_project': select_project,
        'select_db': select_db,
        'no_db_alert': no_db_alert,
        'process_form': process_form,
        'processes_tabulator': processes_tabulator,
        'inputs_tabulator': inputs_tabulator,
    }

def create_process_definition_view():
    """Create the process definition page view"""
    widgets = get_process_definition_widgets()
    
    # Processes section
    processes_header = pmu.pane.Markdown("""
## Available Processes

Select a process from the table below to view and edit its inputs. Click on any process to add it as an input to the currently selected process.
""")

    processes_section = pmu.Column(
        processes_header,
        widgets['processes_tabulator'],
        sizing_mode="stretch_width",
    )

    # Inputs section
    inputs_header = pmu.pane.Markdown("""
## Process Inputs

These are the inputs for the selected process. Amounts can be edited directly in the table.
""")
    
    inputs_section = pmu.Column(
        inputs_header,
        widgets['inputs_tabulator'],
        sizing_mode="stretch_width",
    )
    
    return pmu.Column(
        pmu.pane.Markdown("# Process Definition"),
        widgets['no_db_alert'],
        processes_section,
        inputs_section,
        sizing_mode="stretch_width",
    )

def create_process_definition_sidebar():
    """Create the process definition page sidebar"""
    widgets = get_process_definition_widgets()
    
    return pmu.Column(
        widgets['select_project'],
        widgets['select_db'],
        widgets['process_form'],
        sizing_mode="stretch_width",
    )