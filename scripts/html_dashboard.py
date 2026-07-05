"""
Static HTML dashboard generation for the Daily AI Review project.
"""

from datetime import datetime
from html import escape
from pathlib import Path

AI_REPORT_PATH = Path("AI_REPORT.md")
HTML_DASHBOARD_PATH = Path("docs") / "dashboard.html"
REPORTS_DIR = Path("reports")
GENERATED_BY = "Daily AI Review"


def _read_text(path: Path) -> str:
    """
    Read UTF-8 text if a file exists.
    """

    if not path.exists():
        return ""

    return path.read_text(
        encoding="utf-8",
    )


def _section_lines(content: str, heading: str) -> list[str]:
    """
    Return the Markdown lines that belong to a second-level heading.
    """

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


def _bullet_value(content: str, label: str, default: str = "Pending") -> str:
    """
    Return the value for a Markdown bullet formatted as '- Label: value'.
    """

    prefix = f"- {label}:"

    for line in content.splitlines():
        if line.startswith(prefix):
            value = line.split(":", 1)[1].strip()
            return value or default

    return default


def _health_value(content: str, label: str) -> str:
    """
    Return repository health values from AI_REPORT.md when available.
    """

    return _bullet_value(
        content,
        label,
        default="Pending",
    )


def _markdown_list_items(content: str, heading: str) -> list[str]:
    """
    Return plain text items from a Markdown bullet list section.
    """

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
    """
    Return a field from an individual Markdown review report.
    """

    prefix = f"- {label}:"

    for line in content.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip() or default

    return default


def _recent_report_rows() -> list[dict[str, str]]:
    """
    Build table rows for the last 10 review report artifacts.
    """

    rows = []

    for report in sorted(
        REPORTS_DIR.glob("*_review.md"),
        reverse=True,
    )[:10]:
        content = _read_text(report)
        rows.append(
            {
                "path": report.as_posix(),
                "date": _report_field(content, "Date"),
                "mode": _report_field(content, "Review Mode"),
                "execution_time": _report_field(
                    content,
                    "Execution Time",
                ),
            }
        )

    return rows


def _commit_body_from_report(content: str) -> str:
    """
    Extract the latest commit body from the AI Commit section.
    """

    lines = _section_lines(content, "AI Commit")

    if not lines:
        return "No AI commit was generated."

    body_lines = []
    in_body = False

    for line in lines:
        if line.startswith("- Commit body:"):
            in_body = True
            continue

        if in_body:
            body_lines.append(line)

    body = "\n".join(body_lines).strip()

    return body or "No AI commit was generated."


def _list_html(items: list[str]) -> str:
    """
    Render a list of strings as HTML list items.
    """

    if not items:
        return "<li>None</li>"

    return "\n".join(
        f"<li>{escape(item)}</li>"
        for item in items[:10]
    )


def _review_rows_html(rows: list[dict[str, str]]) -> str:
    """
    Render review history rows for the dashboard table.
    """

    if not rows:
        return """
<tr>
  <td colspan="4">No review reports found.</td>
</tr>
""".strip()

    return "\n".join(
        "<tr>"
        f"<td><a href=\"../{escape(row['path'])}\">{escape(row['path'])}</a></td>"
        f"<td>{escape(row['date'])}</td>"
        f"<td>{escape(row['mode'])}</td>"
        f"<td>{escape(row['execution_time'])}</td>"
        "</tr>"
        for row in rows
    )


def _html_document(
    report_content: str,
    commit_title: str,
    commit_body: str,
) -> str:
    """
    Build the complete static HTML dashboard document.
    """

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    recent_files = _markdown_list_items(
        report_content,
        "Recent Modified Files",
    )
    report_rows = _recent_report_rows()
    commit_body = commit_body or _commit_body_from_report(report_content)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Repository Dashboard</title>
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

    .page {{
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 40px 0;
    }}

    .hero {{
      display: flex;
      justify-content: space-between;
      gap: 24px;
      align-items: flex-start;
      margin-bottom: 28px;
    }}

    h1, h2 {{ margin: 0; }}

    h1 {{
      font-size: clamp(2rem, 5vw, 3.6rem);
      letter-spacing: -0.04em;
    }}

    h2 {{
      font-size: 1.1rem;
      margin-bottom: 16px;
    }}

    .subtitle {{ color: var(--muted); margin-top: 8px; }}

    .badge {{
      background: var(--accent-soft);
      color: var(--accent);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 8px 14px;
      font-weight: 700;
      white-space: nowrap;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 18px;
    }}

    .card {{
      grid-column: span 6;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 22px;
      box-shadow: var(--shadow);
    }}

    .card.full {{ grid-column: 1 / -1; }}

    .stats {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}

    .metric {{
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px;
      background: color-mix(in srgb, var(--card) 90%, var(--accent-soft));
    }}

    .metric span, .label {{ color: var(--muted); font-size: 0.9rem; }}
    .metric strong {{ display: block; font-size: 1.35rem; margin-top: 4px; }}

    dl {{ display: grid; grid-template-columns: auto 1fr; gap: 10px 18px; margin: 0; }}
    dt {{ color: var(--muted); }}
    dd {{ margin: 0; font-weight: 700; }}

    ul {{ margin: 0; padding-left: 20px; }}

    table {{ width: 100%; border-collapse: collapse; overflow: hidden; }}
    th, td {{ border-bottom: 1px solid var(--border); padding: 12px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.04em; }}
    a {{ color: var(--accent); }}

    pre {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px;
      margin: 10px 0 0;
    }}

    footer {{
      color: var(--muted);
      margin-top: 24px;
      text-align: center;
    }}

    @media (max-width: 820px) {{
      .hero {{ flex-direction: column; }}
      .card {{ grid-column: 1 / -1; }}
      .stats {{ grid-template-columns: 1fr; }}
      table {{ display: block; overflow-x: auto; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <div>
        <h1>AI Repository Dashboard</h1>
        <p class="subtitle">Static review dashboard generated from Daily AI Review artifacts.</p>
      </div>
      <div class="badge">{escape(_bullet_value(report_content, 'Gemini model'))}</div>
    </section>

    <section class="grid">
      <article class="card">
        <h2>Repository Information</h2>
        <dl>
          <dt>Repository name</dt><dd>{escape(_bullet_value(report_content, 'Repository name'))}</dd>
          <dt>Current branch</dt><dd>{escape(_bullet_value(report_content, 'Current branch'))}</dd>
          <dt>Last review date</dt><dd>{escape(_bullet_value(report_content, 'Last review date'))}</dd>
          <dt>Last review time</dt><dd>{escape(_bullet_value(report_content, 'Last review time'))}</dd>
          <dt>Gemini model</dt><dd>{escape(_bullet_value(report_content, 'Gemini model'))}</dd>
        </dl>
      </article>

      <article class="card">
        <h2>Repository Statistics</h2>
        <div class="stats">
          <div class="metric"><span>Total tracked files</span><strong>{escape(_bullet_value(report_content, 'Total tracked files', '0'))}</strong></div>
          <div class="metric"><span>Supported files</span><strong>{escape(_bullet_value(report_content, 'Supported files', '0'))}</strong></div>
          <div class="metric"><span>Files reviewed</span><strong>{escape(_bullet_value(report_content, 'Files reviewed', '0'))}</strong></div>
          <div class="metric"><span>Files changed</span><strong>{escape(_bullet_value(report_content, 'Files changed', '0'))}</strong></div>
          <div class="metric"><span>Files skipped</span><strong>{escape(_bullet_value(report_content, 'Files skipped', '0'))}</strong></div>
          <div class="metric"><span>Files failed</span><strong>{escape(_bullet_value(report_content, 'Files failed', '0'))}</strong></div>
        </div>
      </article>

      <article class="card">
        <h2>Repository Health</h2>
        <dl>
          <dt>Overall Score</dt><dd>{escape(_health_value(report_content, 'Overall Score'))}</dd>
          <dt>Documentation</dt><dd>{escape(_health_value(report_content, 'Documentation'))}</dd>
          <dt>Code Quality</dt><dd>{escape(_health_value(report_content, 'Code Quality'))}</dd>
          <dt>Maintainability</dt><dd>{escape(_health_value(report_content, 'Maintainability'))}</dd>
          <dt>Architecture</dt><dd>{escape(_health_value(report_content, 'Architecture'))}</dd>
          <dt>Naming</dt><dd>{escape(_health_value(report_content, 'Naming'))}</dd>
        </dl>
      </article>

      <article class="card">
        <h2>Current Configuration</h2>
        <dl>
          <dt>Review cache</dt><dd>{escape(_bullet_value(report_content, 'Cache enabled'))}</dd>
          <dt>PromptManager</dt><dd>{escape(_bullet_value(report_content, 'PromptManager enabled'))}</dd>
          <dt>Automatic backups</dt><dd>{escape(_bullet_value(report_content, 'Automatic backups enabled'))}</dd>
          <dt>AI reports</dt><dd>True</dd>
          <dt>Dashboard generation</dt><dd>True</dd>
          <dt>Function review</dt><dd>True</dd>
        </dl>
      </article>

      <article class="card full">
        <h2>Review History</h2>
        <table>
          <thead>
            <tr><th>Report</th><th>Date</th><th>Review mode</th><th>Execution time</th></tr>
          </thead>
          <tbody>
            {_review_rows_html(report_rows)}
          </tbody>
        </table>
      </article>

      <article class="card">
        <h2>Recently Modified Files</h2>
        <ul>{_list_html(recent_files)}</ul>
      </article>

      <article class="card">
        <h2>Recent AI Commit</h2>
        <p><span class="label">Commit title</span><br><strong>{escape(commit_title or _bullet_value(report_content, 'Commit title', 'Not generated'))}</strong></p>
        <span class="label">Commit body</span>
        <pre>{escape(commit_body)}</pre>
      </article>
    </section>

    <footer>
      Generated by {GENERATED_BY} · <span id="generated-at">{generated_at}</span>
    </footer>
  </main>
  <script>
    document.documentElement.dataset.generatedAt = "{generated_at}";
  </script>
</body>
</html>
"""


def generate_html_dashboard(
    commit_title: str = "Not generated",
    commit_body: str = "No AI commit was generated.",
) -> Path:
    """
    Generate the static HTML dashboard from existing review artifacts.
    """

    report_content = _read_text(AI_REPORT_PATH)

    HTML_DASHBOARD_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    HTML_DASHBOARD_PATH.write_text(
        _html_document(
            report_content=report_content,
            commit_title=commit_title,
            commit_body=commit_body,
        ),
        encoding="utf-8",
    )

    return HTML_DASHBOARD_PATH
