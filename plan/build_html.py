"""Builds plan/keep-30-day-reels.html from ideas.py.  Run: python3 -I plan/build_html.py"""
import html, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ideas import IDEAS, CLIPS, PILLARS

rows = []
for d in range(30):
    for p in PILLARS:
        hook, punch, clip, bg, cta = IDEAS[p][d]
        file, beat = CLIPS[clip]
        rows.append(dict(id=f"d{d+1:02d}-{p}", day=d + 1, pillar=p, hook=hook, punch=punch,
                         clip=clip.replace("NEW:", ""), new=clip.startswith("NEW:"),
                         file=file or "", beat=beat, bg=bg, cta=cta))

data = json.dumps(rows, ensure_ascii=False)
pillars = json.dumps(PILLARS)

page = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Keep Reels: 30 Days</title>
<style>
:root{
  --bg:#f6f5f2; --card:#ffffff; --ink:#1d1c1a; --muted:#6b6862; --line:#e4e1da;
  --accent:#e2524a; --done:#2f8f5b; --chip:#efece6;
  --travel:#2b7fd1; --storage:#d1492b; --funny:#c28a00; --fails:#8a4fd1; --life:#2f9e8f;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#151513; --card:#1f1f1c; --ink:#f1efe9; --muted:#a29f97; --line:#2f2e2a;
    --accent:#ff6b62; --done:#4fc184; --chip:#2a2926;
    --travel:#5aa5f0; --storage:#f07055; --funny:#e6b331; --fails:#b182f0; --life:#4fc6b5;
  }
}
:root[data-theme="dark"]{
  --bg:#151513; --card:#1f1f1c; --ink:#f1efe9; --muted:#a29f97; --line:#2f2e2a;
  --accent:#ff6b62; --done:#4fc184; --chip:#2a2926;
  --travel:#5aa5f0; --storage:#f07055; --funny:#e6b331; --fails:#b182f0; --life:#4fc6b5;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1100px;margin:0 auto;padding:24px 16px 80px}
header{position:sticky;top:0;z-index:5;background:var(--bg);padding:12px 0 10px;border-bottom:1px solid var(--line)}
h1{margin:0 0 2px;font-size:24px;letter-spacing:-.01em}
.sub{color:var(--muted);margin:0 0 12px;font-size:14px}
.bar{height:8px;background:var(--chip);border-radius:99px;overflow:hidden}
.bar i{display:block;height:100%;width:0;background:var(--done);transition:width .3s}
.stats{display:flex;gap:14px;flex-wrap:wrap;color:var(--muted);font-size:13px;margin:6px 0 10px}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:99px;padding:5px 11px;font-size:13px;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.chip .dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;vertical-align:1px}
.day{margin-top:28px}
.day h2{font-size:15px;margin:0 0 10px;display:flex;align-items:baseline;gap:10px}
.day h2 small{color:var(--muted);font-weight:400}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px}
.card{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--c);border-radius:10px;padding:12px 12px 12px 10px;display:flex;gap:10px}
.card.done{opacity:.5}
.card.done .hook{text-decoration:line-through}
.card input{width:20px;height:20px;margin:2px 0 0;accent-color:var(--done);flex:none;cursor:pointer}
.body{min-width:0;flex:1}
.top{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:6px}
.tag{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:var(--c)}
.new{font-size:11px;font-weight:700;background:var(--accent);color:#fff;border-radius:4px;padding:1px 6px}
.id{margin-left:auto;font-size:11px;color:var(--muted);font-family:ui-monospace,Menlo,monospace}
.hook{font-weight:700;font-size:15.5px}
.punch{margin-top:4px;font-weight:600}
.punch .at{font-weight:400;color:var(--muted);font-size:12px}
.meta{margin-top:8px;font-size:12.5px;color:var(--muted);display:grid;gap:2px}
.meta b{color:var(--ink);font-weight:600}
.cta{margin-top:8px;font-size:13px;background:var(--chip);border-radius:6px;padding:6px 8px}
.empty{color:var(--muted);padding:40px 0;text-align:center}
@media (max-width:420px){.grid{grid-template-columns:1fr}h1{font-size:21px}}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>Keep: 30 days of hamster reels</h1>
  <p class="sub">5 reels a day, one per pillar. The <b>hook</b> sits on top the whole time; the <b>punchline</b> pops in at the clip's beat. Ticks are saved in this browser.</p>
  <div class="bar"><i id="bar"></i></div>
  <div class="stats"><span id="count"></span><span id="newcount"></span></div>
  <div class="chips" id="chips"></div>
</header>
<main id="list"></main>
</div>
<script>
const ROWS = __DATA__;
const PILLARS = __PILLARS__;
const KEY = "keep-reels-30d";
let done = {};
try { done = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { done = {}; }
function save(){ try { localStorage.setItem(KEY, JSON.stringify(done)); } catch (e) {} }
let filter = "all";
const esc = s => s.replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c]));

function chips(){
  const opts = [["all","All"], ...Object.entries(PILLARS), ["new","Needs new clip"], ["todo","Not done"]];
  document.getElementById("chips").innerHTML = opts.map(([k,v]) =>
    `<button class="chip" data-k="${k}" aria-pressed="${filter===k}">${PILLARS[k]?`<span class="dot" style="background:var(--${k})"></span>`:""}${v}</button>`).join("");
  document.querySelectorAll(".chip").forEach(b => b.onclick = () => { filter = b.dataset.k; render(); });
}
function card(r){
  const beat = r.beat === "start" ? "whole clip" : "pops in at " + r.beat;
  return `<label class="card ${done[r.id]?"done":""}" style="--c:var(--${r.pillar})">
    <input type="checkbox" data-id="${r.id}" ${done[r.id]?"checked":""}>
    <div class="body">
      <div class="top"><span class="tag">${PILLARS[r.pillar]}</span>${r.new?'<span class="new">NEW CLIP</span>':""}<span class="id">${r.id}</span></div>
      <div class="hook">${esc(r.hook)}</div>
      ${r.punch?`<div class="punch">→ ${esc(r.punch)} <span class="at">(${beat})</span></div>`:""}
      <div class="meta">
        <span>Hamster: <b>${esc(r.clip)}</b>${r.file?` · ${esc(r.file)}`:" · needs to be generated"}</span>
        <span>Background: <b>${esc(r.bg)}</b></span>
      </div>
      <div class="cta">💬 ${esc(r.cta)}</div>
    </div></label>`;
}
function render(){
  chips();
  const show = r => filter==="all" || r.pillar===filter || (filter==="new" && r.new) || (filter==="todo" && !done[r.id]);
  let out = "";
  for (let d=1; d<=30; d++){
    const rs = ROWS.filter(r => r.day===d && show(r));
    if (!rs.length) continue;
    const n = ROWS.filter(r => r.day===d && done[r.id]).length;
    out += `<section class="day"><h2>Day ${d} <small>${n}/5 done</small></h2><div class="grid">${rs.map(card).join("")}</div></section>`;
  }
  document.getElementById("list").innerHTML = out || '<p class="empty">Nothing here.</p>';
  document.querySelectorAll("input[data-id]").forEach(cb => cb.onchange = () => {
    if (cb.checked) done[cb.dataset.id] = 1; else delete done[cb.dataset.id];
    save(); render();
  });
  const total = ROWS.length, n = ROWS.filter(r => done[r.id]).length;
  document.getElementById("bar").style.width = (100*n/total) + "%";
  document.getElementById("count").textContent = `${n} of ${total} reels done`;
  document.getElementById("newcount").textContent = `${ROWS.filter(r=>r.new).length} reels need a new hamster clip`;
}
render();
</script>
</body>
</html>
"""
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keep-30-day-reels.html")
open(out, "w").write(page.replace("__DATA__", data).replace("__PILLARS__", pillars))
print("wrote", out, len(rows), "reels")
