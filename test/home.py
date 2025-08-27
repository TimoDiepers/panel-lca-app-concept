import panel as pn
pn.extension()

# Buttons to navigate
btn_page1  = pn.widgets.Button(name="Go to Page 1")

btn_page1.js_on_click(code="window.location.href='page1.html'")

home_view = pn.Column(
    "# Home",
    "Welcome to the Home page.",
    pn.Row(btn_page1)
)

home_view.servable()