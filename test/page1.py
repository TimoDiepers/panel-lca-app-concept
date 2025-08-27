import panel as pn
pn.extension()

btn_home    = pn.widgets.Button(name="Go to Home")

btn_home.js_on_click(code="window.location.href='home.html'")

modeling_view = pn.Column(
    "# Modeling",
    "This is the modeling setup page.",
    pn.Row(btn_home)
)

modeling_view.servable()