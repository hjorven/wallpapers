/* Renders wallpapers with the Python generators from tools/gen, running in Pyodide.
   Everything is served from this site: Pyodide, numpy and Pillow live in render/pyodide/. */
importScripts('pyodide/pyodide.js');
const GEN = new URL('../tools/gen/', self.location).href;
let ready = null;
async function boot(files) {
  const py = await loadPyodide({ indexURL: new URL('pyodide/', self.location).href });
  await py.loadPackage(['numpy', 'pillow']);
  py.FS.mkdirTree('/gen/fonts');
  await Promise.all(files.map(async f => {
    const r = await fetch(GEN + f);
    if (!r.ok) throw new Error(`${f}: ${r.status}`);
    py.FS.writeFile('/gen/' + f, new Uint8Array(await r.arrayBuffer()));
  }));
  py.runPython('import sys; sys.path.insert(0, "/gen"); import make');
  return py;
}
self.onmessage = async e => {
  const m = e.data;
  try {
    if (!ready) { self.postMessage({ kind: 'status', text: 'loading' }); ready = boot(m.files); }
    const py = await ready;
    const t = performance.now();
    py.globals.set('job', py.toPy({ style: m.style, slug: m.slug, w: m.w, h: m.h, budget: m.budget, q: m.quality || 92 }));
    const proxy = py.runPython('make.jpeg(job["style"], job["slug"], job["w"], job["h"], job["budget"], job["q"])');
    const bytes = proxy.toJs(); proxy.destroy();
    self.postMessage({ kind: 'done', id: m.id, bytes, ms: performance.now() - t }, [bytes.buffer]);
  } catch (err) {
    self.postMessage({ kind: 'error', id: m.id, text: String(err && err.message || err).slice(-400) });
  }
};
