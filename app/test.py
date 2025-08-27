import panel as pn
import panel_material_ui as pmu
import panel_lca_app_concept as lcapp

test = pn.Column(
    pmu.Button(label="Button 1"),
    pmu.Button(label="Button 2"),
    pmu.Button(label="Button 3"),
    pmu.pane.Markdown(f"## This is a {lcapp.__version__} Markdown cell")
)

test.servable()