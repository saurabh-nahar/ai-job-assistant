#!/usr/bin/env python3
"""Build the daily Job Matches page (LinkedIn, HiringCafe, Indeed) from run.json + rendered resumes.
Usage: python3 build_page.py RUN_DIR  -> writes RUN_DIR/job-matches-YYYY-MM-DD.html"""
import base64, html, json, os, sys

d = sys.argv[1]
run = json.load(open(os.path.join(d, "run.json")))
E = lambda s: html.escape(str(s), quote=True)


def badge(score):
    if score >= 75: return "strong", "Strong"
    if score >= 65: return "good", "Good"
    if score >= 60: return "look", "Worth a look"
    return "stretch", "Below 60%"


files_js = {}
cards = []
for i, j in enumerate(run["jobs"]):
    base = f"{run.get('file_prefix', '')}Resume_{j['slug']}"
    for ext in ("docx", "pdf"):
        p = os.path.join(d, f"{base}.{ext}")
        if os.path.exists(p):
            files_js[f"{base}.{ext}"] = base64.b64encode(open(p, "rb").read()).decode()
    cls, label = badge(j["score"])
    gold = j.get("golden_bonus", 0) > 0
    gtag = f'<span class="gtag">Golden +{j["golden_bonus"]}</span>' if gold else ''
    scoreline = f'{j.get("base_score", j["score"])} base + {j["golden_bonus"]} golden = {j["score"]}' if gold else str(j["score"])
    goldnote = f'<p class="goldnote"><strong>Golden:</strong> {E(j.get("golden_reason", ""))}</p>' if gold else ''
    rv = j.get("review") or {}
    review = (f'<div class="review"><strong>Recruiter-eye review' + (f' · {E(rv["coverage"])}% of must-haves covered' if rv.get("coverage") is not None else '') + f'</strong><span>{E(rv.get("notes", ""))}</span></div>') if rv else ''

    why = "".join(f"<li>{E(w)}</li>" for w in j["why"])
    aud = []
    for key, name, search in (("recruiter", "Recruiter", "search_rec"),
                              ("hiring_manager", "Hiring manager", "search_hm"),
                              ("referral", "Internal referral", "search_ref")):
        m = j["messages"][key]
        nid, mid = f"n{i}{key}", f"m{i}{key}"
        aud.append(f"""
      <details class="aud"{' open' if key == 'recruiter' else ''}>
        <summary><span>{name}</span><span class="who">{E(j['people'][key])}</span></summary>
        <a class="find" href="{E(j[search])}" target="_blank" rel="noopener">Find them on LinkedIn ↗</a>
        <div class="msg">
          <div class="msghead"><span class="lbl">{E(m.get('note_label','Connection note'))}</span><span class="count">{len(m["note"])}/300</span>
            <button type="button" class="copy" data-target="{nid}">Copy</button></div>
          <p id="{nid}" class="txt">{E(m['note'])}</p>
        </div>
        <div class="msg">
          <div class="msghead"><span class="lbl">{E(m.get('message_label','Full message, after they accept'))}</span><span class="count">{len(m["message"].split())} words</span>
            <button type="button" class="copy" data-target="{mid}">Copy</button></div>
          <p id="{mid}" class="txt">{E(m['message'])}</p>
        </div>
      </details>""")
    cards.append(f"""
  <article class="job{' golden' if gold else ''}" id="job{i+1}">
    <header class="jobhead">
      <div class="score {cls}"><span class="num">{j['score']}</span><span class="pct">%</span><span class="tag">{label}</span></div>
      <div class="ident">
        <h2><a href="{E(j['url'])}" target="_blank" rel="noopener">{E(j['title'])}</a> {gtag}</h2>
        <p class="co">{E(j['company'])} · {E(j['location'])}</p>
        <p class="meta">{E(j['company_meta'])} · {E(j['workmode'])}</p>
      </div>
    </header>
    <dl class="facts">
      <div><dt>Salary</dt><dd>{E(j['salary'])}</dd></div>
      <div><dt>Posted</dt><dd>{E(j['posted'])} · {E(j['applicants'])}</dd></div>
      <div><dt>Score</dt><dd>{E(scoreline)}</dd></div>
      <div class="wide"><dt>Scope</dt><dd>{E(j['scope'])}</dd></div>
    </dl>
    {goldnote}{review}
    <section class="assess">
      <h3>Why you have a shot</h3><ul>{why}</ul>
      <h3>What's thin</h3><p>{E(j['thin'])}</p>
      <h3>Lead with</h3><p class="angle">{E(j['angle'])}</p>
    </section>
    <div class="actions">
      <a class="btn primary" href="{E(j['url'])}" target="_blank" rel="noopener">Open posting ↗</a>
      <button type="button" class="btn dl" data-file="{base}.docx">Resume .docx</button>
      <button type="button" class="btn dl" data-file="{base}.pdf">Resume .pdf</button>
    </div>
    <section class="outreach"><h3>LinkedIn outreach</h3>{''.join(aud)}</section>
  </article>""")

filtered = "".join(f"<li><strong>{E(f['role'])}</strong><span>{E(f['reason'])}</span></li>" for f in run["filtered"])
s = run["stats"]
strip = "".join(f"<span><b>{E(a)}</b> {E(b)}</span>" for a, b in s["items"]) if "items" in s else f"<span><b>{len(run['jobs'])}</b> roles at 60%+</span><span><b>{s['pooled']}</b> results pooled</span><span><b>{s['reviewed']}</b> read in full</span><span><b>{s['searches']}</b> searches</span>"
index = "".join(
    f'<li><a href="#job{i+1}"><span class="mono">{j["score"]}%</span> {E(j["title"])} <em>· {E(j["company"])}</em>{" <span class=\'gtag\'>Golden</span>" if j.get("golden_bonus", 0) > 0 else ""}</a></li>'
    for i, j in enumerate(run["jobs"]))
empty = "" if run["jobs"] else '<p class="empty">No role cleared the 60% bar today. The near-misses are listed below.</p>'

page = f"""<title>{E(run.get('title', 'Job Matches · ' + run['date']))}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap">
<style>
/* Layout: one reading column of job dossiers, summary strip on top, near-misses at the foot */
:root {{
  --bg:#F3F5F8; --surface:#FFFFFF; --ink:#16202E; --muted:#5A6576; --line:#DAE0E8;
  --accent:#1F5FBF; --accent-ink:#FFFFFF; --soft:#E8EFFB;
  --good:#1D7A4C; --ok:#7A5F00; --look:#9A4A1A;
  --gold:#9A6A00; --gold-soft:#FBF1D6; --gold-line:#E5C66E;
  --body:'Public Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
  --mono:'IBM Plex Mono', ui-monospace, 'SFMono-Regular', Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#0E131A; --surface:#161D27; --ink:#E5EAF1; --muted:#97A2B3; --line:#273243;
  --accent:#86ABF0; --accent-ink:#0E131A; --soft:#1C2940; --good:#5DC58F; --ok:#E0BD4D; --look:#F0905F; --gold:#E8C25A; --gold-soft:#2E2715; --gold-line:#6E5A22; color-scheme:dark }} }}
:root[data-theme="dark"] {{
  --bg:#0E131A; --surface:#161D27; --ink:#E5EAF1; --muted:#97A2B3; --line:#273243;
  --accent:#86ABF0; --accent-ink:#0E131A; --soft:#1C2940; --good:#5DC58F; --ok:#E0BD4D; --look:#F0905F; --gold:#E8C25A; --gold-soft:#2E2715; --gold-line:#6E5A22; color-scheme:dark }}
* {{ box-sizing:border-box }}
body {{ background:var(--bg); color:var(--ink); font:15px/1.55 var(--body); margin:0 }}
.wrap {{ max-width:880px; margin:0 auto; padding-inline:16px; padding-block:28px 56px; display:grid; gap:22px }}
h1,h2,h3 {{ text-wrap:balance; margin:0 }}
a {{ color:var(--accent) }}
.mono {{ font-family:var(--mono); font-variant-numeric:tabular-nums }}
.top {{ display:grid; gap:10px }}
.eyebrow {{ font:600 12px/1 var(--mono); letter-spacing:.08em; text-transform:uppercase; color:var(--muted) }}
.top h1 {{ font-size:clamp(24px,4vw,32px); font-weight:700; letter-spacing:-.01em }}
.strip {{ display:flex; flex-wrap:wrap; gap:8px 18px; color:var(--muted); font-size:14px }}
.strip b {{ font-family:var(--mono); color:var(--ink) }}
.note {{ color:var(--muted); font-size:14px; max-width:70ch; margin:0 }}
.index {{ list-style:none; margin:0; padding:0; display:grid; gap:4px }}
.index a {{ text-decoration:none; color:var(--ink) }} .index em {{ color:var(--muted); font-style:normal }}
.index .mono {{ display:inline-block; min-width:3.2em; color:var(--accent) }}
.job {{ background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:20px; display:grid; gap:16px; min-width:0 }}
.jobhead {{ display:flex; gap:16px; align-items:flex-start }}
.ident {{ min-width:0 }}
.ident h2 {{ font-size:19px; line-height:1.3 }} .ident h2 a {{ color:var(--ink); text-decoration:none }}
.ident h2 a:hover {{ text-decoration:underline }}
.co {{ margin:4px 0 0; font-weight:600 }} .meta {{ margin:2px 0 0; color:var(--muted); font-size:13.5px }}
.score {{ flex:none; width:84px; padding:8px 0 7px; border-radius:8px; text-align:center; border:1.5px solid currentColor; display:grid; grid-template-columns:auto auto; justify-content:center; align-items:baseline }}
.score .num {{ font:600 28px/1 var(--mono) }} .score .pct {{ font:600 14px var(--mono) }}
.score .tag {{ grid-column:1/-1; font:600 10.5px/1.2 var(--body); letter-spacing:.06em; text-transform:uppercase; margin-top:4px }}
.score.strong {{ color:var(--good) }} .score.good {{ color:var(--ok) }} .score.look {{ color:var(--look) }} .score.stretch {{ color:var(--muted) }}
.facts {{ display:grid; grid-template-columns:1fr 1fr; gap:10px 18px; margin:0 }}
.facts .wide {{ grid-column:1/-1 }}
.facts dt {{ font:600 11px/1.4 var(--mono); letter-spacing:.07em; text-transform:uppercase; color:var(--muted) }}
.facts dd {{ margin:2px 0 0 }}
.assess {{ display:grid; gap:6px; max-width:72ch }}
.assess h3, .outreach > h3 {{ font-size:13px; font-weight:700; letter-spacing:.04em; text-transform:uppercase; color:var(--muted); margin-top:6px }}
.assess ul {{ margin:0; padding-left:18px; display:grid; gap:4px }} .assess p {{ margin:0 }}
.angle {{ background:var(--soft); border-radius:6px; padding:8px 12px }}
.actions {{ display:flex; flex-wrap:wrap; gap:8px }}
.btn {{ font:600 14px var(--body); padding:9px 14px; border-radius:7px; border:1px solid var(--line); background:var(--surface); color:var(--ink); cursor:pointer; text-decoration:none }}
.btn.primary {{ background:var(--accent); border-color:var(--accent); color:var(--accent-ink) }}
.btn:hover {{ border-color:var(--accent) }} .btn:focus-visible, .copy:focus-visible, summary:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px }}
.dlnote {{ font-size:13px; color:var(--muted); margin:0 }}
.outreach {{ display:grid; gap:8px; min-width:0 }}
.aud {{ border:1px solid var(--line); border-radius:8px; padding:10px 14px; min-width:0 }}
.aud summary {{ cursor:pointer; display:flex; flex-wrap:wrap; gap:4px 12px; align-items:baseline; font-weight:600 }}
.aud summary .who {{ font-weight:400; color:var(--muted); font-size:13.5px }}
.find {{ display:inline-block; margin:8px 0 4px; font-size:13.5px }}
.msg {{ margin-top:10px; display:grid; gap:6px }}
.msghead {{ display:flex; align-items:center; gap:10px }}
.lbl {{ font:600 11px var(--mono); letter-spacing:.07em; text-transform:uppercase; color:var(--muted) }}
.count {{ font:500 11px var(--mono); color:var(--muted) }}
.copy {{ margin-left:auto; font:600 12.5px var(--body); padding:4px 10px; border-radius:6px; border:1px solid var(--line); background:var(--bg); color:var(--ink); cursor:pointer }}
.txt {{ margin:0; white-space:pre-wrap; background:var(--bg); border-radius:6px; padding:10px 12px; font-size:14px; overflow-wrap:anywhere }}
.filtered {{ display:grid; gap:10px }}
.filtered h2 {{ font-size:17px }}
.filtered ul {{ list-style:none; margin:0; padding:0; display:grid; gap:8px }}
.filtered li {{ display:grid; gap:2px; padding-bottom:8px; border-bottom:1px solid var(--line) }}
.filtered li span {{ color:var(--muted); font-size:14px }}
.empty {{ padding:16px; border:1px dashed var(--line); border-radius:8px }}
.job.golden {{ border-color:var(--gold-line); box-shadow:inset 3px 0 0 var(--gold) }}
.gtag {{ display:inline-block; vertical-align:middle; font:600 10.5px/1.2 var(--body); letter-spacing:.05em; text-transform:uppercase; color:var(--gold); background:var(--gold-soft); border:1px solid var(--gold-line); border-radius:4px; padding:2px 6px; margin-left:4px }}
.goldnote {{ margin:0; background:var(--gold-soft); border:1px solid var(--gold-line); border-radius:6px; padding:8px 12px; font-size:14px }}
.review {{ display:grid; gap:4px; background:var(--soft); border-radius:6px; padding:8px 12px; font-size:14px }}
@media (max-width:520px) {{ .facts {{ grid-template-columns:1fr }} .jobhead {{ flex-direction:column }} }}
@media (prefers-reduced-motion:reduce) {{ * {{ transition:none!important }} }}
</style>
<main class="wrap">
  <header class="top">
    <span class="eyebrow">{E(run.get('eyebrow','Daily job matches'))}</span>
    <h1>{E(run['date_label'])}</h1>
    <div class="strip">{strip}</div>
    <p class="note">{E(s.get('note',''))} Scores estimate your odds of being shortlisted, based on how many of the posting's must-haves your resume can prove.</p>
    <ul class="index">{index}</ul>
    {f'<p class="note"><a href="{E(run["tracker_url"])}" target="_blank" rel="noopener">Open your Job Application Tracker ↗</a> to mark roles applied, see replies and download everything as Excel.</p>' if run.get("tracker_url") else ''}
    <p class="dlnote" id="dlnote" hidden>Resume downloads need the Claude app or claude.ai. They aren't available in this view.</p>
  </header>
  {empty}
  {''.join(cards)}
  <section class="filtered"><h2>{E(run.get('filtered_title','Filtered out this run'))}</h2><ul>{filtered}</ul></section>
</main>
<script>
const FILES = {json.dumps(files_js)};
function b64(s) {{ const b = atob(s), u = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return u; }}
document.querySelectorAll('.copy').forEach(btn => btn.addEventListener('click', () => {{
  const el = document.getElementById(btn.dataset.target);
  const done = () => {{ btn.textContent = 'Copied'; setTimeout(() => btn.textContent = 'Copy', 1600); }};
  const select = () => {{ const r = document.createRange(); r.selectNodeContents(el); const s = getSelection(); s.removeAllRanges(); s.addRange(r); btn.textContent = 'Selected'; setTimeout(() => btn.textContent = 'Copy', 1600); }};
  try {{ navigator.clipboard.writeText(el.innerText).then(done, select); }} catch (e) {{ select(); }}
}}));
const dlButtons = document.querySelectorAll('.dl');
let downloads = null;
(async () => {{
  try {{ downloads = window.claude && window.claude.use ? await window.claude.use('downloads') : null; }} catch (e) {{ downloads = null; }}
  if (!downloads) {{ dlButtons.forEach(b => b.disabled = true); document.getElementById('dlnote').hidden = false; }}
}})();
dlButtons.forEach(btn => btn.addEventListener('click', async () => {{
  if (!downloads) return;
  const name = btn.dataset.file, label = btn.textContent;
  try {{ await downloads.save({{ filename: name, data: b64(FILES[name]) }}); btn.textContent = 'Saved'; }}
  catch (e) {{ btn.textContent = (e && e.code === 'declined') ? 'Cancelled' : 'Try again'; }}
  setTimeout(() => btn.textContent = label, 2000);
}}));
</script>
"""
out = os.path.join(d, f"job-matches-{run.get('file_slug', run['date'])}.html")
open(out, "w").write(page)
print(out, f"{len(page)/1024:.0f} KB")
WORDS = {"recruiter": (120, 180), "hiring_manager": (120, 180), "referral": (80, 120)}
for j in run["jobs"]:
    for k, m in j["messages"].items():
        if len(m["note"]) > 300: print("NOTE TOO LONG:", j["slug"], k, len(m["note"]), "> 300")
        lo, hi = WORDS.get(k, (0, 10**6)); n = len(m["message"].split())
        if not lo <= n <= hi: print("MESSAGE LENGTH:", j["slug"], k, n, f"words (want {lo}-{hi})")
