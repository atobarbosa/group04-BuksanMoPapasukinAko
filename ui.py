# ui.py — BuksanMoPapasukinAko (Monochrome Beach Redesign)
import gradio as gr
import requests

API_BASE = "http://127.0.0.1:8000"

# ── Palette ────────────────────────────────────────────────────────────────
# 284b63  deep navy      — panels, borders, structure
# 3c6e71  muted teal     — primary accent, safe state
# d9d9d9  light sand     — secondary text, dividers
# ffffff  white          — primary text
# 353535  charcoal       — base background
# b06a56  muted terracotta (added) — danger/alert state, kept warm+muted to fit the palette

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

* { box-sizing: border-box; }

body, .gradio-container {
    background-color: #2b2b2b !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    color: #d9d9d9 !important;
}

.gradio-container {
    max-width: 780px !important;
    margin: 0 auto !important;
    padding: 1.75rem 1.25rem 3rem !important;
}

footer { display: none !important; }

/* ── Upload zone ── */
#upload-zone {
    border: 1.5px dashed rgba(60, 110, 113, 0.45) !important;
    border-radius: 12px !important;
    background: rgba(60, 110, 113, 0.04) !important;
    transition: border-color 0.2s ease, background 0.2s ease !important;
}
#upload-zone:hover {
    border-color: rgba(60, 110, 113, 0.8) !important;
    background: rgba(60, 110, 113, 0.08) !important;
}

/* ── Scan button ── */
#scan-btn {
    background: #3c6e71 !important;
    border: 1px solid #4d8386 !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    width: 100% !important;
    padding: 0.8rem !important;
    cursor: pointer !important;
    transition: background 0.2s ease, transform 0.15s ease !important;
    margin-top: 0.6rem !important;
}
#scan-btn:hover {
    background: #457a7d !important;
    transform: translateY(-1px) !important;
}
#scan-btn:active {
    transform: translateY(0) !important;
}

#output-area > .wrap { padding: 0 !important; border: none !important; background: transparent !important; }
#history-area > .wrap { padding: 0 !important; border: none !important; background: transparent !important; }
"""

# ── Header ─────────────────────────────────────────────────────────────────
HEADER_HTML = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');
.bmpa-header {
    position: relative;
    background: #284b63;
    border: 1px solid rgba(217, 217, 217, 0.08);
    border-radius: 16px;
    padding: 2.25rem 2rem 2rem;
    text-align: center;
    margin-bottom: 1rem;
    overflow: hidden;
}
.bmpa-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(60,110,113,0.9), transparent);
}
.bmpa-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(60, 110, 113, 0.22);
    border: 1px solid rgba(60, 110, 113, 0.5);
    border-radius: 999px;
    padding: 0.28rem 0.85rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.13em;
    color: #d9d9d9;
    text-transform: uppercase;
    margin-bottom: 1.1rem;
}
.bmpa-badge-dot {
    width: 6px; height: 6px;
    background: #3c6e71;
    border-radius: 50%;
    animation: bmpa-pulse 2.2s ease-in-out infinite;
}
@keyframes bmpa-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.3; transform: scale(0.8); }
}
.bmpa-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.65rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 0.4rem;
    letter-spacing: -0.02em;
}
.bmpa-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    color: #a9b7c0;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin: 0 0 0.9rem;
}
.bmpa-desc {
    font-family: 'Inter', sans-serif;
    font-size: 0.855rem;
    color: #c3ccd1;
    max-width: 420px;
    margin: 0 auto;
    line-height: 1.65;
}
.bmpa-desc code {
    font-family: 'JetBrains Mono', monospace;
    background: rgba(60, 110, 113, 0.28);
    color: #d9d9d9;
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    font-size: 0.8rem;
}
</style>
<div class="bmpa-header">
    <div class="bmpa-badge">
        <span class="bmpa-badge-dot"></span>
        Live System
    </div>
    <h1 class="bmpa-title">BuksanMoPapasukinAko</h1>
    <p class="bmpa-subtitle">Network Intrusion Anomaly Detector</p>
    <p class="bmpa-desc">
        Upload a <code>.parquet</code> network log to classify each traffic event as
        normal or a cyberattack using a trained Random Forest model.
    </p>
</div>
"""

# ── Shared result styles ─────────────────────────────────────────────────────
_RESULT_STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

.res, .hist { font-family: 'Inter', system-ui, sans-serif; }

.res-status {
    border-radius: 12px;
    padding: 1.15rem 1.4rem;
    margin-bottom: 0.875rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.res-status.safe   { background: rgba(60,110,113,0.14); border: 1px solid rgba(60,110,113,0.4); }
.res-status.danger { background: rgba(176,106,86,0.14); border: 1px solid rgba(176,106,86,0.4); }

.res-status-icon {
    width: 34px; height: 34px;
    flex-shrink: 0;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 1rem;
}
.res-status-icon.safe   { background: rgba(60,110,113,0.3);  color: #7fb0b2; }
.res-status-icon.danger { background: rgba(176,106,86,0.3); color: #d4a08e; }

.res-status-label { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.2rem; }
.res-status-label.safe   { color: #7fb0b2; }
.res-status-label.danger { color: #d4a08e; }
.res-status-desc  { color: #a9a9a9; font-size: 0.82rem; line-height: 1.45; }

.res-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.7rem;
    margin-bottom: 0.875rem;
}
.res-card {
    background: #284b63;
    border-radius: 10px;
    padding: 1.05rem 0.9rem;
    text-align: center;
    border: 1px solid rgba(217,217,217,0.06);
}

.res-card-label {
    font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.11em; text-transform: uppercase;
    margin-bottom: 0.45rem;
    color: #9db4c2;
}
.res-card-label.teal        { color: #7fb0b2; }
.res-card-label.terracotta  { color: #d4a08e; }

.res-card-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.7rem; font-weight: 700;
    color: #ffffff; line-height: 1;
    margin-bottom: 0.3rem;
}
.res-card-sub { font-size: 0.72rem; color: #7d8b93; }

.res-bar-wrap {
    background: #284b63;
    border: 1px solid rgba(217,217,217,0.06);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.875rem;
}
.res-bar-header {
    display: flex; justify-content: space-between;
    font-size: 0.77rem; color: #9db4c2;
    margin-bottom: 0.65rem;
}
.res-bar-track {
    background: rgba(60,110,113,0.25);
    border-radius: 999px; height: 5px;
    overflow: hidden; margin-bottom: 0.55rem;
}
.res-bar-fill {
    height: 100%; border-radius: 999px;
    background: #b06a56;
}
.res-bar-legend { display: flex; gap: 1.1rem; font-size: 0.7rem; color: #9db4c2; }
.res-dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; margin-right: 0.3rem; vertical-align: middle; }

/* Attack category breakdown */
.res-cat-wrap {
    background: #284b63;
    border: 1px solid rgba(217,217,217,0.06);
    border-radius: 10px;
    padding: 1rem 1.2rem;
}
.res-cat-title {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.11em;
    text-transform: uppercase; color: #9db4c2; margin-bottom: 0.7rem;
}
.res-cat-row {
    display: flex; align-items: center; gap: 0.7rem;
    margin-bottom: 0.5rem; font-size: 0.78rem;
}
.res-cat-row:last-child { margin-bottom: 0; }
.res-cat-name { flex: 0 0 130px; color: #d9d9d9; }
.res-cat-track { flex: 1; background: rgba(176,106,86,0.15); border-radius: 999px; height: 6px; overflow: hidden; }
.res-cat-fill { height: 100%; border-radius: 999px; background: #b06a56; }
.res-cat-count { flex: 0 0 44px; text-align: right; font-family: 'JetBrains Mono', monospace; color: #d4a08e; }

/* History table */
.hist-wrap {
    background: #284b63;
    border: 1px solid rgba(217,217,217,0.06);
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
}
.hist-title {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.11em;
    text-transform: uppercase; color: #9db4c2; margin-bottom: 0.9rem;
}
.hist-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
.hist-table th {
    text-align: left; font-weight: 600; color: #7d8b93;
    font-size: 0.65rem; letter-spacing: 0.07em; text-transform: uppercase;
    padding-bottom: 0.5rem; border-bottom: 1px solid rgba(217,217,217,0.08);
}
.hist-table td {
    padding: 0.55rem 0; color: #d9d9d9;
    border-bottom: 1px solid rgba(217,217,217,0.05);
}
.hist-table tr:last-child td { border-bottom: none; }
.hist-empty { color: #7d8b93; font-size: 0.82rem; text-align: center; padding: 1rem 0; }
.hist-tag {
    display: inline-block; padding: 0.15rem 0.55rem; border-radius: 999px;
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.03em;
}
.hist-tag.safe   { background: rgba(60,110,113,0.25); color: #7fb0b2; }
.hist-tag.danger { background: rgba(176,106,86,0.25); color: #d4a08e; }
</style>
"""

# ── Idle state ────────────────────────────────────────────────────────────
IDLE_HTML = f"""{_RESULT_STYLES}
<div style="
    background: #284b63;
    border: 1px dashed rgba(217, 217, 217, 0.15);
    border-radius: 14px;
    padding: 3rem 2rem;
    text-align: center;
    font-family: 'Inter', sans-serif;
">
    <div style="
        width: 40px; height: 40px; margin: 0 auto 1rem;
        border: 1.5px solid rgba(217,217,217,0.2);
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        color: #9db4c2; font-family: 'JetBrains Mono', monospace; font-size: 1.1rem;
    ">·</div>
    <p style="color: #9db4c2; font-size: 0.875rem; margin: 0; line-height: 1.6;">
        No scan results yet.<br>
        Upload a <span style="font-family: 'JetBrains Mono', monospace; color: #d9d9d9; font-size: 0.82rem;">.parquet</span> log above and select <strong style="color: #ffffff; font-weight: 600;">Initiate Scan</strong>.
    </p>
</div>
"""


def _error_html(message: str) -> str:
    return f"""{_RESULT_STYLES}
    <div style="
        background: rgba(176,106,86,0.12);
        border: 1px solid rgba(176,106,86,0.35);
        border-radius: 12px; padding: 1.2rem 1.4rem;
        font-family: 'Inter', sans-serif;
        display: flex; align-items: flex-start; gap: 0.9rem;
    ">
        <div style="
            width: 30px; height: 30px; flex-shrink: 0; margin-top: 0.1rem;
            border-radius: 50%; background: rgba(176,106,86,0.3);
            display: flex; align-items: center; justify-content: center;
            color: #d4a08e; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 0.85rem;
        ">!</div>
        <div>
            <div style="color: #d4a08e; font-weight: 600; font-size: 0.82rem; letter-spacing: 0.03em; margin-bottom: 0.3rem;">
                System Error
            </div>
            <div style="color: #b8c2c7; font-size: 0.83rem; line-height: 1.55;">{message}</div>
        </div>
    </div>
    """


def _render_category_breakdown(breakdown: dict) -> str:
    if not breakdown:
        return ""
    max_count = max(breakdown.values())
    rows = ""
    for name, count in sorted(breakdown.items(), key=lambda kv: kv[1], reverse=True):
        width_pct = (count / max_count * 100) if max_count > 0 else 0
        rows += f"""
        <div class="res-cat-row">
            <span class="res-cat-name">{name}</span>
            <div class="res-cat-track"><div class="res-cat-fill" style="width:{width_pct:.1f}%;"></div></div>
            <span class="res-cat-count">{count:,}</span>
        </div>"""
    return f"""
    <div class="res-cat-wrap">
        <div class="res-cat-title">Attack Category Breakdown</div>
        {rows}
    </div>
    """


def _render_history(history: list) -> str:
    if not history:
        return f"""{_RESULT_STYLES}
        <div class="hist-wrap">
            <div class="hist-title">Scan History</div>
            <div class="hist-empty">No scans logged yet this session.</div>
        </div>
        """

    rows = ""
    for row in history:
        safe = str(row.get("is_network_safe", "")).lower() == "true"
        tag_class = "safe" if safe else "danger"
        tag_label = "Secure" if safe else "Flagged"
        ts = row.get("timestamp", "")
        display_ts = ts.replace("T", "  ").split("+")[0] if ts else ""
        rows += f"""
        <tr>
            <td>{display_ts}</td>
            <td>{row.get('filename', '')}</td>
            <td>{int(row.get('total_scanned', 0)):,}</td>
            <td>{int(row.get('anomalies_detected', 0)):,}</td>
            <td><span class="hist-tag {tag_class}">{tag_label}</span></td>
        </tr>"""

    return f"""{_RESULT_STYLES}
    <div class="hist-wrap">
        <div class="hist-title">Scan History</div>
        <table class="hist-table">
            <thead>
                <tr><th>Time (UTC)</th><th>File</th><th>Scanned</th><th>Flagged</th><th>Status</th></tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    """


def fetch_history_html():
    try:
        resp = requests.get(f"{API_BASE}/history", params={"limit": 10})
        data = resp.json()
        if data.get("status") != "Success":
            return _render_history([])
        return _render_history(data.get("history", []))
    except Exception:
        return _render_history([])


# ── Core scan logic ──────────────────────────────────────────────────────
def upload_and_scan(file_path):
    if file_path is None:
        return IDLE_HTML, fetch_history_html()

    try:
        with open(file_path, "rb") as f:
            response = requests.post(f"{API_BASE}/scan", files={"file": f})

        try:
            result = response.json()
        except ValueError:
            return _error_html("The API returned invalid data. Check the api.py terminal for errors."), fetch_history_html()

        if result.get("status") == "Error":
            return _error_html(result.get("message", "Unknown server error.")), fetch_history_html()

        total     = result["total_events_scanned"]
        attacks   = result["anomalies_detected"]
        normal    = total - attacks
        pct       = (attacks / total * 100) if total > 0 else 0
        safe      = result.get("is_network_safe")
        cat_breakdown = result.get("attack_category_breakdown")

        sc          = "safe" if safe else "danger"
        icon_char   = "OK" if safe else "!!"
        label       = "Network Secure" if safe else "Threats Detected"
        desc        = "All traffic events classified as normal. No anomalies found." if safe \
                      else f"{attacks:,} events flagged as anomalous. Immediate review recommended."

        category_html = _render_category_breakdown(cat_breakdown) if cat_breakdown else ""

        result_html = f"""{_RESULT_STYLES}
        <div class="res">
            <div class="res-status {sc}">
                <span class="res-status-icon {sc}">{icon_char}</span>
                <div>
                    <div class="res-status-label {sc}">{label}</div>
                    <div class="res-status-desc">{desc}</div>
                </div>
            </div>

            <div class="res-grid">
                <div class="res-card">
                    <div class="res-card-label">Total Scanned</div>
                    <div class="res-card-value">{total:,}</div>
                    <div class="res-card-sub">events analyzed</div>
                </div>
                <div class="res-card">
                    <div class="res-card-label teal">Normal Traffic</div>
                    <div class="res-card-value">{normal:,}</div>
                    <div class="res-card-sub">{100 - pct:.1f}% of log</div>
                </div>
                <div class="res-card">
                    <div class="res-card-label terracotta">Anomalies</div>
                    <div class="res-card-value">{attacks:,}</div>
                    <div class="res-card-sub">{pct:.1f}% of log</div>
                </div>
            </div>

            <div class="res-bar-wrap">
                <div class="res-bar-header">
                    <span>Threat Composition</span>
                    <span>{pct:.1f}% flagged as malicious</span>
                </div>
                <div class="res-bar-track">
                    <div class="res-bar-fill" style="width: {min(pct, 100):.2f}%;"></div>
                </div>
                <div class="res-bar-legend">
                    <span><span class="res-dot" style="background:#3c6e71;"></span>Normal</span>
                    <span><span class="res-dot" style="background:#b06a56;"></span>Anomaly</span>
                </div>
            </div>

            {category_html}
        </div>
        """

        return result_html, fetch_history_html()

    except requests.exceptions.ConnectionError:
        return _error_html(
            "Could not reach the FastAPI backend. Make sure api.py is running on port 8000."
        ), fetch_history_html()
    except Exception as e:
        return _error_html(str(e)), fetch_history_html()


# ── Gradio layout ─────────────────────────────────────────────────────────
with gr.Blocks(css=CUSTOM_CSS, theme=gr.themes.Base()) as app:

    gr.HTML(HEADER_HTML)

    file_input = gr.File(
        label="Upload Network Log (.parquet)",
        file_types=[".parquet"],
        elem_id="upload-zone",
    )

    scan_button = gr.Button(
        "Initiate Scan",
        variant="primary",
        elem_id="scan-btn",
    )

    output_display = gr.HTML(
        value=IDLE_HTML,
        elem_id="output-area",
    )

    history_display = gr.HTML(
        value=f"{_RESULT_STYLES}",  # populated on load
        elem_id="history-area",
    )

    scan_button.click(
        fn=upload_and_scan,
        inputs=file_input,
        outputs=[output_display, history_display],
    )

    app.load(fn=fetch_history_html, inputs=None, outputs=history_display)

if __name__ == "__main__":
    app.launch(server_name="127.0.0.1", server_port=7860)