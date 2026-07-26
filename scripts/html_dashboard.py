"""Static HTML dashboard generation for the Daily AI Review project."""
import json
from datetime import datetime
from html import escape
from pathlib import Path

AI_REPORT_PATH = Path("AI_REPORT.md")
HTML_DASHBOARD_PATH = Path("docs") / "dashboard.html"
REPORTS_DIR = Path("reports")
GENERATED_BY = "Daily AI Review"

def _read_text(path: Path) -> str:
    """Read UTF-8 text if a file exists."""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")

def _section_lines(content: str, heading: str) -> list[str]:
    """Return the Markdown lines that belong to a second-level heading."""
    lines = content.splitlines()
    section = []
    in_section = False
    for line in lines:
        if line == f"## {heading}":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            section.append(line)
    return section

def _find_value(content: str, label: str, default: str = "Pending") -> str:
    """Find a value for a label, handling both '- Label: val' and 'Label : val'."""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith(f"- {label}:"):
            return line.split(":", 1)[1].strip() or default
        if line.startswith(f"{label} :"):
            return line.split(":", 1)[1].strip() or default
    return default

def _bullet_value(content: str, label: str, default: str = "Pending") -> str:
    return _find_value(content, label, default)

def _health_value(content: str, label: str) -> str:
    return _find_value(content, label, default="Pending")

def _markdown_list_items(content: str, heading: str) -> list[str]:
    """Return plain text items from a Markdown bullet list section."""
    items = []
    for line in _section_lines(content, heading):
        line = line.strip()
        if not line.startswith("- "):
            continue
        value = line[2:].strip()
        if value and value != "None":
            items.append(value)
    return items

def _report_field(content: str, label: str, default: str = "Pending") -> str:
    return _find_value(content, label, default)

def _recent_report_rows() -> list[dict[str, any]]:
    """Build table rows for the last 15 review report artifacts."""
    rows = []
    reports = sorted(REPORTS_DIR.glob("*_review.md"), reverse=False)
    
    recent_reports = reports[-15:]
    
    for report in recent_reports:
        content = _read_text(report)
        health = _health_value(content, "Overall Score")
        
        def to_int(v):
            try: return int(v.split()[0]) if isinstance(v, str) else int(v)
            except: return 0

        # Extract failed reasons
        failed_section = _section_lines(content, "Failed Files")
        reasons = []
        for line in failed_section:
            line = line.strip()
            if line.startswith("- ") and ":" in line:
                reasons.append(line[2:].strip())

        date_val = _report_field(content, "Date")
        time_val = _report_field(content, "Time", "")
        display_date = f"{date_val} {time_val}".strip()
        try:
            dt = datetime.strptime(display_date, "%Y-%m-%d %H:%M:%S")
            display_date = dt.strftime("%b %d, %Y %I:%M:%S %p")
        except Exception:
            pass

        success_rate_val = float(_report_field(content, "Success rate", "100").replace("%", ""))
        status = "Success" if success_rate_val == 100.0 else "Failed"

        rows.append({
            "path": report.as_posix(),
            "date": date_val,
            "display_date": display_date,
            "status": status,
            "mode": _report_field(content, "Review Mode"),
            "model": _bullet_value(content, "Gemini model", "Unknown"),
            "execution_time": _report_field(content, "Execution Time").replace(" seconds", ""),
            "health": health,
            "health_int": to_int(health),
            "doc": to_int(_health_value(content, "Documentation")),
            "quality": to_int(_health_value(content, "Code Quality")),
            "maintain": to_int(_health_value(content, "Maintainability")),
            "success_rate": success_rate_val,
            "fail_reasons": ", ".join(reasons) if reasons else "None"
        })
    
    return list(reversed(rows))

def _list_html(items: list[str]) -> str:
    if not items:
        return "<li>None</li>"
    return "\n".join(f"<li>{escape(i)}</li>" for i in items)

def _review_rows_html(rows: list[dict[str, any]]) -> str:
    html = []
    for r in rows:
        html.append(f"""
        <tr>
          <td><a href="/reports/view/{Path(r['path']).name}">{escape(Path(r['path']).name)}</a></td>
          <td>{escape(r['display_date'])}</td>
          <td><span class="badge-model">{escape(r['model'])}</span></td>
          <td><strong>{escape(r['health'])}</strong></td>
          <td>
            <span class="badge-status {escape(r['status'].lower())}">{escape(r['status'])}</span>
            <div style="font-size: 0.8rem; color: var(--muted); margin-top: 2px;">{escape(str(r['success_rate']))}% success</div>
          </td>
          <td>
            {f'<span class="reason-text" title="{escape(r["fail_reasons"])}">{escape(r["fail_reasons"])}</span>' if r['fail_reasons'] != 'None' else '<span class="text-muted">-</span>'}
          </td>
        </tr>
        """)
    return "".join(html)

def _parse_detailed_file_changes(report_content: str) -> list[dict[str, str]]:
    changes = []
    stats_file = Path(".cache") / "dashboard_stats.json"
    if stats_file.exists():
        try:
            data = json.loads(stats_file.read_text(encoding="utf-8"))
            if "recent_file_changes" in data and isinstance(data["recent_file_changes"], list):
                if data["recent_file_changes"]:
                    return data["recent_file_changes"]
        except Exception:
            pass

    if "## Detailed File Changes" in report_content:
        section = report_content.split("## Detailed File Changes", 1)[1]
        if "## " in section:
            section = section.split("## ", 1)[0]
        current_item = None
        for line in section.splitlines():
            line_s = line.strip()
            if line_s.startswith("- **`") and "`**" in line_s:
                if current_item:
                    changes.append(current_item)
                f_name = line_s.split("- **`")[1].split("`**")[0]
                current_item = {"file": f_name, "what": "N/A", "why": "N/A"}
            elif current_item and "**What Changed**:" in line_s:
                current_item["what"] = line_s.split("**What Changed**:", 1)[1].strip()
            elif current_item and "**Why Changed**:" in line_s:
                current_item["why"] = line_s.split("**Why Changed**:", 1)[1].strip()
        if current_item:
            changes.append(current_item)
    return changes


def _file_changes_rows_html(changes: list[dict[str, str]]) -> str:
    if not changes:
        return "<tr><td colspan='3' class='text-muted'>No file change details recorded yet.</td></tr>"
    rows = []
    for fc in changes:
        f_file = escape(str(fc.get("file", "")))
        f_what = escape(str(fc.get("what", "")))
        f_why = escape(str(fc.get("why", "")))
        rows.append(f"""
        <tr>
          <td><code style="background: var(--accent-soft); color: var(--accent); padding: 2px 6px; border-radius: 4px;">{f_file}</code></td>
          <td>{f_what}</td>
          <td>{f_why}</td>
        </tr>
        """)
    return "\n".join(rows)


def _recent_history_cards_html(report_rows: list[dict[str, any]]) -> str:
    recent = report_rows[:5]
    if not recent:
        return "<p class='text-muted'>No review execution history recorded yet.</p>"
    items = []
    for r in recent:
        dt = escape(str(r.get("display_date", "N/A")))
        h = escape(str(r.get("health", "N/A")))
        report_name = escape(Path(r.get("path", "")).name)
        items.append(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: color-mix(in srgb, var(--card) 95%, var(--accent-soft)); border: 1px solid var(--border); border-radius: 10px; margin-bottom: 10px;">
          <div style="display: flex; flex-direction: column;">
            <strong style="font-size: 0.95rem;">{dt}</strong>
            <span style="font-size: 0.8rem; color: var(--muted);">{report_name}</span>
          </div>
          <span class="badge" style="background: var(--accent-soft); color: var(--accent); font-weight: 700; padding: 6px 14px; border-radius: 20px;">Health: {h}</span>
        </div>
        """)
    return "\n".join(items)


def _html_document(report_content: str, commit_title: str, commit_body: str) -> str:

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    recent_files = _markdown_list_items(report_content, "Recent Modified Files")
    report_rows = _recent_report_rows()
    
    trend_data = list(reversed(report_rows))
    trend_json = json.dumps(trend_data)
    
    # Model breakdown and detailed stats
    model_stats = {}
    for r in report_rows:
        m = r['model']
        if m not in model_stats:
            model_stats[m] = {
                "count": 0,
                "total_time": 0.0,
                "total_health": 0,
                "health_count": 0,
                "success_sum": 0.0
            }
        stats_entry = model_stats[m]
        stats_entry["count"] += 1
        try:
            stats_entry["total_time"] += float(r["execution_time"])
        except ValueError:
            pass
        if r["health_int"] > 0:
            stats_entry["total_health"] += r["health_int"]
            stats_entry["health_count"] += 1
        stats_entry["success_sum"] += r["success_rate"]
        
    model_stats_html = []
    for m, s in model_stats.items():
        avg_time = s["total_time"] / s["count"] if s["count"] > 0 else 0.0
        avg_health = s["total_health"] / s["health_count"] if s["health_count"] > 0 else 0.0
        avg_success = s["success_sum"] / s["count"] if s["count"] > 0 else 0.0
        model_stats_html.append(f"""
        <div class="model-stat-card" style="margin-bottom: 14px; border: 1px solid var(--border); border-radius: 12px; padding: 12px; background: color-mix(in srgb, var(--card) 95%, var(--accent-soft));">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span class="badge-model" style="margin: 0;">{escape(m)}</span>
            <strong style="font-size: 1.1rem; color: var(--accent);">{s['count']} {'reviews' if s['count'] > 1 else 'review'}</strong>
          </div>
          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center; font-size: 0.8rem; color: var(--muted);">
            <div>
              <span style="display: block;">Avg Time</span>
              <strong style="color: var(--text); font-size: 0.9rem;">{avg_time:.2f}s</strong>
            </div>
            <div>
              <span style="display: block;">Avg Health</span>
              <strong style="color: var(--text); font-size: 0.9rem;">{avg_health:.1f}</strong>
            </div>
            <div>
              <span style="display: block;">Success %</span>
              <strong style="color: var(--text); font-size: 0.9rem;">{avg_success:.1f}%</strong>
            </div>
          </div>
        </div>
        """)
    model_stats_html_str = "\n".join(model_stats_html) if model_stats_html else "<p class='text-muted'>No model usage data yet.</p>"

    # Simple insights
    insights = []
    if len(trend_data) >= 2:
        diff = trend_data[-1]['health_int'] - trend_data[-2]['health_int']
        if diff > 0: insights.append(f"Health score improved by {diff} points since last run.")
        elif diff < 0: insights.append(f"Health score dropped by {abs(diff)} points. Check recent changes.")
        
        avg_success = sum(d['success_rate'] for d in trend_data) / len(trend_data)
        insights.append(f"Average success rate is {avg_success:.1f}%.")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Repository Dashboard</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #f6f8fb;
      --card: #ffffff;
      --text: #172033;
      --muted: #667085;
      --border: #d9e2ec;
      --accent: #2563eb;
      --accent-soft: #e8f0ff;
      --shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
      --green: #10b981;
      --orange: #f59e0b;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #0f172a;
        --card: #111827;
        --text: #e5e7eb;
        --muted: #9ca3af;
        --border: #263244;
        --accent: #60a5fa;
        --accent-soft: #172554;
        --shadow: 0 16px 40px rgba(0, 0, 0, 0.35);
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }}
    .page {{ width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 40px 0; }}
    .hero {{ display: flex; justify-content: space-between; gap: 24px; align-items: flex-start; margin-bottom: 28px; }}
    h1, h2 {{ margin: 0; }}
    h1 {{ font-size: clamp(2rem, 5vw, 3.6rem); letter-spacing: -0.04em; }}
    h2 {{ font-size: 1.1rem; margin-bottom: 16px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
    .subtitle {{ color: var(--muted); margin-top: 8px; }}
    .badge {{ background: var(--accent-soft); color: var(--accent); border: 1px solid var(--border); border-radius: 999px; padding: 8px 14px; font-weight: 700; }}
    .grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 18px; }}
    .card {{ grid-column: span 6; background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 22px; box-shadow: var(--shadow); }}
    .card.full {{ grid-column: 1 / -1; }}
    .card.third {{ grid-column: span 4; }}
    .stats {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }}
    .metric {{ border: 1px solid var(--border); border-radius: 14px; padding: 14px; background: color-mix(in srgb, var(--card) 90%, var(--accent-soft)); }}
    .metric span {{ color: var(--muted); font-size: 0.85rem; }}
    .metric strong {{ display: block; font-size: 1.25rem; margin-top: 4px; }}
    dl {{ display: grid; grid-template-columns: auto 1fr; gap: 8px 16px; margin: 0; }}
    dt {{ color: var(--muted); }}
    dd {{ margin: 0; font-weight: 700; }}
    ul {{ margin: 0; padding-left: 18px; }}
    li {{ margin-bottom: 4px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid var(--border); padding: 10px; text-align: left; font-size: 0.9rem; }}
    th {{ color: var(--muted); font-size: 0.8rem; text-transform: uppercase; }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    footer {{ color: var(--muted); margin-top: 32px; text-align: center; font-size: 0.9rem; }}
    .chart-container {{ width: 100%; height: 220px; }}
    .line {{ fill: none; stroke-width: 3; }}
    .axis-label {{ font-size: 10px; fill: var(--muted); }}
    .legend {{ display: flex; gap: 16px; font-size: 0.8rem; margin-bottom: 12px; }}
    .legend-item {{ display: flex; align-items: center; gap: 6px; }}
    .legend-box {{ width: 12px; height: 12px; border-radius: 3px; }}
    @media (max-width: 900px) {{ .card, .card.third {{ grid-column: 1 / -1; }} }}
    
    /* New styles for statuses and badges */
    .badge-status {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .badge-status.success {{
      background: rgba(16, 185, 129, 0.15);
      color: #10b981;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    .badge-status.failed {{
      background: rgba(239, 68, 68, 0.15);
      color: #ef4444;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }}
    .badge-model {{
      display: inline-block;
      background: var(--accent-soft);
      color: var(--accent);
      padding: 4px 8px;
      border-radius: 6px;
      font-family: monospace;
      font-size: 0.85rem;
      border: 1px solid var(--border);
    }}
    .reason-text {{
      color: #ef4444;
      font-size: 0.85rem;
      display: inline-block;
      max-width: 250px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      cursor: help;
      border-bottom: 1px dashed rgba(239, 68, 68, 0.5);
    }}
    .text-muted {{
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <div>
        <h1>AI Repository Dashboard</h1>
        <p class="subtitle">Detailed analysis of repository health and AI model performance.</p>
      </div>
      <div class="badge">{escape(_bullet_value(report_content, 'Gemini model'))}</div>
    </section>
    
    <section class="grid">
      <article class="card full">
        <h2>Health & Success Trends</h2>
        <div class="legend">
          <div class="legend-item"><div class="legend-box" style="background: var(--accent);"></div> Overall Health</div>
          <div class="legend-item"><div class="legend-box" style="background: var(--green);"></div> Success Rate %</div>
        </div>
        <div id="main-chart" class="chart-container"></div>
      </article>

      <article class="card third">
        <h2>Model Usage</h2>
        {model_stats_html_str}
      </article>

      <article class="card third">
        <h2>Automated Insights</h2>
        <ul>
          {_list_html(insights or ["Data collection in progress..."])}
        </ul>
      </article>

      <article class="card third">
        <h2>Review Statistics</h2>
        <div class="stats">
          <div class="metric"><span>Discovered</span><strong>{escape(_bullet_value(report_content, 'Files discovered', '0'))}</strong></div>
          <div class="metric"><span>Latest Model</span><strong>{escape(_bullet_value(report_content, 'Gemini model', 'N/A'))}</strong></div>
        </div>
      </article>

      <article class="card full">
        <h2>📁 Detailed File Changes (Which, What & Why)</h2>
        <table>
          <thead>
            <tr><th>Which File</th><th>What Changed</th><th>Why Changed</th></tr>
          </thead>
          <tbody>
            {_file_changes_rows_html(_parse_detailed_file_changes(report_content))}
          </tbody>
        </table>
      </article>

      <article class="card full">
        <h2>🕒 Review History</h2>
        <p style="color: var(--muted); margin-top: -8px; margin-bottom: 16px; font-size: 0.9rem;">
          5 most recent review execution timestamps and health scores.
        </p>
        {_recent_history_cards_html(report_rows)}
      </article>

      <article class="card full">
        <h2>History Detail</h2>

        <table>
          <thead>
            <tr><th>Report</th><th>Date & Time</th><th>Model</th><th>Health</th><th>Status</th><th>Fail Reasons</th></tr>
          </thead>
          <tbody>
            {_review_rows_html(report_rows)}
          </tbody>
        </table>
      </article>
    </section>
    <footer>
      Generated by {GENERATED_BY} · {generated_at}
    </footer>
  </main>

  <script>
    const data = {trend_json};
    
    function drawCharts() {{
      if (!data.length) return;
      
      const container = d3.select("#main-chart");
      const width = container.node().clientWidth;
      const height = container.node().clientHeight;
      const margin = {{top: 10, right: 30, bottom: 40, left: 40}};
      
      const svg = container.append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${{margin.left}}, ${{margin.top}})`);

      const x = d3.scalePoint()
        .domain(data.map(d => d.date))
        .range([0, width - margin.left - margin.right]);

      const y = d3.scaleLinear()
        .domain([0, 100])
        .range([height - margin.top - margin.bottom, 0]);

      svg.append("g")
        .attr("transform", `translate(0, ${{height - margin.top - margin.bottom}})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("class", "axis-label")
        .attr("transform", "rotate(-35)")
        .style("text-anchor", "end");

      svg.append("g").call(d3.axisLeft(y).ticks(5)).attr("class", "axis-label");

      // Line for Health
      const lineHealth = d3.line()
        .x(d => x(d.date))
        .y(d => y(d.health_int))
        .curve(d3.curveMonotoneX);

      svg.append("path")
        .datum(data)
        .attr("class", "line")
        .attr("stroke", "var(--accent)")
        .attr("d", lineHealth);

      // Line for Success Rate
      const lineSuccess = d3.line()
        .x(d => x(d.date))
        .y(d => y(d.success_rate))
        .curve(d3.curveMonotoneX);

      svg.append("path")
        .datum(data)
        .attr("class", "line")
        .attr("stroke", "var(--green)")
        .attr("stroke-dasharray", "4,4")
        .attr("d", lineSuccess);

      // Dots
      svg.selectAll(".dot")
        .data(data)
        .enter().append("circle")
        .attr("cx", d => x(d.date))
        .attr("cy", d => y(d.health_int))
        .attr("r", 4)
        .attr("fill", "var(--accent)");
    }}

    drawCharts();
    window.addEventListener('resize', () => {{
      d3.select("#main-chart svg").remove();
      drawCharts();
    }});
  </script>
</body>
</html>"""

def generate_html_dashboard(commit_title: str = "Not generated", commit_body: str = "No AI commit was generated.") -> Path:
    report_content = _read_text(AI_REPORT_PATH)
    HTML_DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc_content = _html_document(report_content=report_content, commit_title=commit_title, commit_body=commit_body)
    HTML_DASHBOARD_PATH.write_text(doc_content, encoding="utf-8")
    
    reports_dashboard = Path("reports") / "dashboard.html"
    reports_dashboard.parent.mkdir(parents=True, exist_ok=True)
    reports_dashboard.write_text(doc_content, encoding="utf-8")
    return HTML_DASHBOARD_PATH

if __name__ == "__main__":
    generate_html_dashboard()
