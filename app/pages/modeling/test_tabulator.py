import panel as pn
import pandas as pd
import numpy as np
import panel_material_ui as pmu

np.random.seed(42)  # For reproducibility

df = pd.DataFrame({
    'One': np.random.randint(1, 4, size=72),
    'Two': np.round(np.random.uniform(1.0, 10.0, size=72), 2),
    'Three': np.random.choice(['A', 'B', 'C'], size=72)
})

tabulator = pn.widgets.Tabulator(
    pd.DataFrame(columns=["One", "Two", "Three"]),
    sizing_mode="stretch_both",
    pagination="remote",
    show_index=False,
    header_filters={
        "One": {"type": "input", "func": "like", "placeholder": "Filter One..."},
        "Two": {"type": "input", "func": "like", "placeholder": "Filter Two..."},
        "Three": {"type": "input", "func": "like", "placeholder": "Filter Three..."},
    },
    stylesheets=[
        ":host .tabulator {border-radius: var(--mui-shape-borderRadius);}"
    ],
    )

btn = pn.widgets.Button(name="Add Data")

def add_data(event):
    tabulator.value = df
    tabulator.page_size = None
    
pn.bind(add_data, btn, watch=True)

btn.on_click(add_data)
pmu.Page(main=[pn.widgets.Button(), pn.widgets.Button(), btn, tabulator]).servable()
