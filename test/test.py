# mini_router.py
import panel as pn
pn.extension()

# Use the Location component per docs
loc = pn.state.location
loc.reload = False  # single-page app; don't reload on URL updates

# Two simple views
def home_view():
    return pn.Column("# Home", "This is the home view.", sizing_mode="stretch_width")

def about_view():
    return pn.Column("# About", "This is the about view.", sizing_mode="stretch_width")

VIEWS = {"home": home_view, "about": about_view}

main = pn.Column(sizing_mode="stretch_width")

def route_from_hash():
    # docs: use `hash_` and include the leading '#'
    h = loc.hash_ or "#home"
    name = h[1:] if h.startswith("#") else h
    return name or "home"

def render(_=None):
    name = route_from_hash()
    view = VIEWS.get(name, lambda: pn.Column("## 404", f"Unknown: {name}"))()
    main.objects = [view]  # swap the container's content

# Buttons that manipulate the URL (docs: access & manipulate)
to_home  = pn.widgets.Button(name="Go Home", button_type="primary")
to_about = pn.widgets.Button(name="Go About")

to_home.on_click(lambda e: setattr(loc, "hash_", "#home"))
to_about.on_click(lambda e: setattr(loc, "hash_", "#about"))

# React to URL changes (docs: watch the Location parameters)
loc.param.watch(render, "hash_")

# Initial render
render()

tmpl = pn.template.FastListTemplate(
    title="Hash Router (docs-style)",
    header=[pn.Row(to_home, to_about)],
    main=[main],
)
tmpl.servable()