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
  const env_spec = ['https://cdn.holoviz.org/panel/wheels/bokeh-3.7.3-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.7.5/dist/wheels/panel-1.7.5-py3-none-any.whl', 'pyodide-http==0.2.1']
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
      console.log(e)
      self.postMessage({
	type: 'status',
	msg: `Error while installing ${pkg_name}`
      });
    }
  }
  console.log("Packages loaded!");
  self.postMessage({type: 'status', msg: 'Executing code'})
  const code = `
  \nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\n# mini_router.py (minimal, docs-style)\nimport panel as pn\npn.extension()\n\n# --- simple views ---\n\ndef home_view():\n    return pn.Column("# Home", "This is the home view.", sizing_mode="stretch_width")\n\n\ndef about_view():\n    return pn.Column("# About", "This is the about view.", sizing_mode="stretch_width")\n\n\nVIEWS = {"home": home_view, "about": about_view}\n\n# Main container\nmain = pn.Column(sizing_mode="stretch_width")\n\n# Hidden signal widget that we update from JS when the hash changes\nroute_sig = pn.widgets.TextInput(name="route_sig", value="", visible=False)\n\n\ndef _render(_=None):\n    name = (route_sig.value or "home").strip() or "home"\n    view = VIEWS.get(name, lambda: pn.Column("## 404", f"Unknown: {name}"))()\n    main.objects = [view]\n\n\n# Re-render whenever the signal changes (set from JS)\nroute_sig.param.watch(_render, "value")\n\n# Buttons that change the URL hash via JS (so the URL updates too)\nbtn_home = pn.widgets.Button(name="Go Home", button_type="primary")\nbtn_about = pn.widgets.Button(name="Go About")\nbtn_home.js_on_click(code="window.location.hash = '#home';")\nbtn_about.js_on_click(code="window.location.hash = '#about';")\n\n# JS snippet: mirror window.location.hash -> route_sig.value, run on load\nsetup_js = pn.pane.HTML(\n    """\n    <script>\n    (function() {\n      function current() {\n        var h = window.location.hash || '#home';\n        return h.startsWith('#') ? h.slice(1) : h;\n      }\n      function init() {\n        const doc = Bokeh.documents[0];\n        const sig = doc.get_model_by_name('route_sig');\n        if (!sig) { setTimeout(init, 50); return; }\n        // initialize from current hash\n        sig.value = current();\n        // update on hash changes\n        window.addEventListener('hashchange', function() {\n          sig.value = current();\n        });\n      }\n      init();\n    })();\n    </script>\n    """,\n    height=0,\n    sizing_mode="fixed",\n)\n\n# Include the hidden signal and setup pane so the JS runs\ntmpl = pn.template.FastListTemplate(\n    title="Hash Router (Pyodide-minimal)",\n    header=[pn.Row(btn_home, btn_about), route_sig, setup_js],\n    main=[main],\n)\n\n# Initial render (will be overwritten by JS once the page loads)\n_render()\n\n# Serve\ntmpl.servable()\n\nawait write_doc()
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