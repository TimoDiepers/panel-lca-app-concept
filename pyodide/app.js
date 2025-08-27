importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.5/full/pyodide.js");

function sendPatch(patch, buffers, msg_id) {
  self.postMessage({
    type: 'patch',
    patch: patch,
    buffers: buffers
  })
}

async function startApplication() {
  console.log("Loading pyodide!");
  self.postMessage({type: 'status', msg: 'Loading pyodide'})
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
  const env_spec = ['https://cdn.holoviz.org/panel/wheels/bokeh-3.7.3-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.7.5/dist/wheels/panel-1.7.5-py3-none-any.whl', 'pyodide-http==0.2.1', 'panel_material_ui']
  for (const pkg of env_spec) {
    let pkg_name;
    if (pkg.endsWith('.whl')) {
      pkg_name = pkg.split('/').slice(-1)[0].split('-')[0]
    } else {
      pkg_name = pkg
    }
    self.postMessage({type: 'status', msg: `Installing ${pkg_name}`})
    try {
      await self.pyodide.runPythonAsync(`
        import micropip
        await micropip.install('${pkg}');
      `);
    } catch(e) {
      console.error('micropip install failed for base installs', pkg, e)
      self.postMessage({
  type: 'status',
  msg: `Error while installing ${pkg_name}`
      });
    }
  }
  console.log("Basic packages loaded!");
  try {
    await self.pyodide.runPythonAsync(`
      import micropip
      micropip.uninstall('typing-extensions')
      await micropip.install('panel-lca-app-concept');
      `);
  } catch(e) {
    console.error("panel lca app concept install failed", e)
    self.postMessage({
  type: 'status',
  msg: `Error while installing panel-lca-app-concept`
      });
  }
  console.log("All Packages loaded!");

  self.postMessage({type: 'status', msg: 'Executing code'})
  const code = `
  \nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport panel as pn\nimport panel_material_ui as pmu\n\nfrom panel_lca_app_concept.theming import theme_config\nfrom panel_lca_app_concept.demo_databases import add_chem_demo_project\nfrom panel_lca_app_concept.pages.home import create_home_view\nfrom panel_lca_app_concept.pages.calculation_setup import create_calculation_setup_view\nfrom panel_lca_app_concept.pages.impact_overview import create_impact_overview_view\n\n# Initialize Panel extensions\npn.extension("plotly", "tabulator", notifications=True)\npn.state.location.sync = True\npn.config.css_files.append("https://fonts.googleapis.com/icon?family=Material+Icons+Outlined")\n\n# Initialize demo data\nadd_chem_demo_project()\n\n# Route mapping for hash-based navigation\nROUTES = {\n    "home": create_home_view,\n    "modeling/calculation-setup": create_calculation_setup_view,\n    "results/impact-overview": create_impact_overview_view,\n}\n\nclass App:\n    def __init__(self):\n        # Create containers for main content\n        self.main_container = pn.Column(sizing_mode="stretch_width")\n        self._last_route = None\n\n        # Create nav buttons BEFORE any rendering so highlight logic works\n        self.home_button = pmu.Button(\n            icon="home_outlined",\n            icon_size="2em",\n            label="Home",\n            color="light",\n            variant="text",\n            width=170,\n            stylesheets=[\n                ":host .MuiButton-text {font-size: 14px;} .MuiIcon-root {margin-right: 8px; font-family: 'Material Icons Outlined' !important;}"\n            ],\n        )\n        self.modeling_button = pmu.Button(\n            icon="settings_outlined",\n            icon_size="2em",\n            label="Modeling",\n            color="light",\n            variant="text",\n            width=170,\n            stylesheets=[\n                ":host .MuiButton-text {font-size: 14px;} .MuiIcon-root {margin-right: 8px; font-family: 'Material Icons Outlined' !important;}"\n            ],\n        )\n        self.results_button = pmu.Button(\n            icon="insert_chart_outlined",\n            icon_size="2em",\n            label="Results",\n            color="light",\n            variant="text",\n            width=170,\n            stylesheets=[\n                ":host .MuiButton-text {font-size: 14px;} .MuiIcon-root {margin-right: 8px; font-family: 'Material Icons Outlined' !important;}"\n            ],\n        )\n\n        self.home_button.on_click(lambda event: self.set_route("home"))\n        self.modeling_button.on_click(lambda event: self.set_route("modeling/calculation-setup"))\n        self.results_button.on_click(lambda event: self.set_route("results/impact-overview"))\n\n        self.BUTTON_MAPPING = {\n            "home": self.home_button,\n            "modeling/calculation-setup": self.modeling_button,\n            "results/impact-overview": self.results_button,\n        }\n\n        nav = pn.Row(\n           self.home_button, self.modeling_button, self.results_button,\n            # width=600,\n            # sizing_mode="stretch_width",\n            styles={\n                "align-items": "center",\n                "justify-content": "space-around",\n                "margin-left": "auto",\n                "margin-right": "auto",\n            },\n        )\n        \n        logout_button = pmu.IconButton(\n            icon="logout",\n            size="2em",\n            color="light",\n        )\n        \n        logout_button.js_on_click(code="""window.location.href = './logout'""")\n\n        # self.page = pn.Column(\n        #     nav, self.main_container,\n        #     sizing_mode="stretch_width",\n        #     # theme_config=theme_config,\n        # )\n        # Create the page\n        self.page = pmu.Page(\n            header=[nav, logout_button],\n            main=[self.main_container],\n            # sidebar=[\n            #     self.menu,\n            #     pn.layout.Divider(\n            #         stylesheets=[\n            #             ":host hr {margin: 0px 10px 0 10px; border: 0; border-top: 1px solid var(--mui-palette-divider); }"\n            #         ],\n            #     ),\n            #     self.sidebar_container,\n            # ],\n            # sidebar_open=False,\n            # sidebar_variant="temporary",\n            title="PMI-LCA Tool",\n            theme_config=theme_config,\n        )\n\n        # Set up routing once the page is loaded (ensures hash is available on reload)\n        # after building self.page\n        initialized = {"done": False}\n        def _init(_=None):\n            if initialized["done"]: \n                return\n            initialized["done"] = True\n            self._setup_routing()\n\n        pn.state.onload(_init)\n        _init()  # also call once in case onload timing differs in Pyodide\n\n        # Fallback polling in Pyodide: detect hash changes even if events are missed\n        def _poll_hash():\n            try:\n                if pn.state.location:\n                    current = self.get_route()\n                    if current != self._last_route:\n                        self.render_from_location()\n            except Exception:\n                pass\n\n        # Poll every 300 ms (adjust if needed)\n        pn.state.add_periodic_callback(_poll_hash, period=300, start=True)\n\n    def _setup_routing(self):\n        """Set up hash-based routing when the app is loaded"""\n        loc = pn.state.location\n        if not loc:\n            # Fallback when not in a server context\n            self._render_route("home")\n            return\n\n        # Use current hash if present (supports deep-link reload)\n        path = (loc.hash or "").lstrip("#/").strip("/") or "home"\n        self._highlight_active_button(path)\n        self._render_route(path)\n\n        # Watch for future hash changes (back/forward, button clicks)\n        loc.param.watch(self.render_from_location, "hash")\n\n    def _highlight_active_button(self, path: str):\n        default_ss = [\n            ":host .MuiButton-text {font-size: 14px; font-weight: 400;} .MuiIcon-root {font-family: 'Material Icons Outlined' !important;}"\n        ]\n        highlighted_ss = [\n            ":host .MuiButton-root {background: rgba(255, 255, 255, 0.08);} .MuiButton-text {font-size: 14px; font-weight: 600;} .MuiIcon-root {font-family: 'Material Icons' !important;}"\n        ]\n\n        config = {\n            self.home_button: {\n                "default": (default_ss, "home_outlined"),\n                "highlighted": (highlighted_ss, "home"),\n            },\n            self.modeling_button: {\n                "default": (default_ss, "settings_outlined"),\n                "highlighted": (highlighted_ss, "settings"),\n            },\n            self.results_button: {\n                "default": (default_ss, "insert_chart_outlined"),\n                "highlighted": (highlighted_ss, "insert_chart"),\n            },\n        }\n\n        # Determine active button once\n        active_btn = self.BUTTON_MAPPING.get(path, self.home_button)\n\n        # Iterate once, only change if needed to avoid flicker\n        for btn in (self.home_button, self.modeling_button, self.results_button):\n            if btn is active_btn:\n                desired_ss, desired_icon = config[btn]["highlighted"]\n            else:\n                desired_ss, desired_icon = config[btn]["default"]\n\n            if btn.stylesheets != desired_ss:\n                btn.stylesheets = desired_ss\n\n            if btn.icon != desired_icon:\n                btn.icon = desired_icon\n\n    def set_route(self, path: str):\n        """Set the current route using hash"""\n        self._highlight_active_button(path)\n        if pn.state.location:\n            pn.state.location.hash = f"#{path}"\n            self.render_from_location()\n\n    def get_route(self) -> str:\n        if not pn.state.location:\n            return "home"\n        h = pn.state.location.hash or ""\n        h = h.lstrip("#/").strip("/")       # safe either way\n        return h or "home"\n\n    def resolve_view(self, path: str):\n        """Get the view function for a given path"""\n        return ROUTES.get(path, ROUTES["home"])\n\n    def render_from_location(self, _=None):\n        """Update view and menu selection based on current hash"""\n        path = self.get_route()\n        self._highlight_active_button(path)\n        self._render_route(path)\n\n    def _render_route(self, path: str):\n        """Render the given route path"""\n        try:\n            self._last_route = path\n\n            # Get view function for current path\n            main_func = self.resolve_view(path)\n\n            # Build the new view\n            main_view = main_func()\n\n            # \u2b07\ufe0f Force a full container replacement (more reliable in Pyodide)\n            new_container = pn.Column(main_view, sizing_mode="stretch_width")\n            self.main_container = new_container\n            try:\n                # Replace the page's main area content\n                self.page.main[:] = [new_container]\n            except Exception:\n                self.page.main = [new_container]\n\n        except Exception as e:\n            print(f"Error rendering route {path}: {e}")\n            if path != "home":\n                self._render_route("home")\n\n# Create and serve the app\napp = App()\napp.page.servable(title="PMI-LCA Tool")\n\nawait write_doc()
  `

  try {
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(code)
    self.postMessage({
      type: 'render',
      docs_json: docs_json,
      render_items: render_items,
      root_ids: root_ids
    })
  } catch(e) {
    const traceback = `${e}`
    const tblines = traceback.split('\n')
    self.postMessage({
      type: 'status',
      msg: tblines[tblines.length-2]
    });
    throw e
  }
}

self.onmessage = async (event) => {
  const msg = event.data
  if (msg.type === 'rendered') {
    self.pyodide.runPythonAsync(`
    from panel.io.state import state
    from panel.io.pyodide import _link_docs_worker

    _link_docs_worker(state.curdoc, sendPatch, setter='js')
    `)
  } else if (msg.type === 'patch') {
    self.pyodide.globals.set('patch', msg.patch)
    self.pyodide.runPythonAsync(`
    from panel.io.pyodide import _convert_json_patch
    state.curdoc.apply_json_patch(_convert_json_patch(patch), setter='js')
    `)
    self.postMessage({type: 'idle'})
  } else if (msg.type === 'location') {
    self.pyodide.globals.set('location', msg.location)
    self.pyodide.runPythonAsync(`
    import json
    from panel.io.state import state
    from panel.util import edit_readonly
    if state.location:
        loc_data = json.loads(location)
        with edit_readonly(state.location):
            state.location.param.update({
                k: v for k, v in loc_data.items() if k in state.location.param
            })
    `)
  }
}

startApplication()