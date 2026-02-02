import yaml
import requests
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SITE_DIR = BASE_DIR / "site"

TOOLS_FILE = DATA_DIR / "tools.yaml"
SITE_DIR.mkdir(exist_ok=True)

BASE_URL = "https://aiopentec.github.io/open-source-analytics-alternatives"
GITHUB_API = "https://api.github.com/repos/{}"


def fetch_github(repo):
    try:
        r = requests.get(GITHUB_API.format(repo), timeout=10)
        if r.status_code == 200:
            j = r.json()
            return {
                "stars": j.get("stargazers_count", 0),
                "updated": j.get("updated_at", "")[:10],
            }
    except Exception:
        pass
    return {"stars": 0, "updated": "Unknown"}


def load_tools():
    with open(TOOLS_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write(name, content):
    (SITE_DIR / name).write_text(content.strip(), encoding="utf-8")


def generate_home(tools):
    links = "\n".join(
        f"- [{t['name']}]({t['slug']}.html)" for t in tools
    )

    write(
        "index.md",
        f"""
# Open-Source Analytics Alternatives

Compare the best **privacy-friendly, open-source alternatives** to proprietary analytics platforms.

{links}
""",
    )


def generate_tool_page(tool, tools):
    top_pick = ""
    if tool.get("top_pick"):
        top_pick = f"""
<div class="top-pick">
🏆 <strong>Top Pick:</strong> {tool['name']}<br>
Recommended for most privacy-focused websites.
</div>
"""

    table = "| Tool | Stars | Self-Hosted | Privacy |\n"
    table += "|------|-------|-------------|---------|\n"

    for t in tools:
        table += (
            f"| {t['name']} | {t['stars']} | "
            f"{'✅' if t.get('self_hosted') else '❌'} | "
            f"{t.get('privacy', 'unknown').title()} |\n"
        )

    write(
        f"{tool['slug']}.md",
        f"""
# {tool['name']} Alternatives

{tool.get('description', '')}

⭐ **{tool['stars']} GitHub stars** • 🕒 **Updated {tool['updated']}**

{top_pick}

---

## Comparison Table

{table}

---

## Hosting & Services

Many open-source analytics tools require hosting and maintenance.

If you prefer a managed option, consider privacy-friendly VPS providers.

_Links may become affiliate links in the future. Recommendations are based on relevance, not payment._
""",
    )


def generate_sitemap(tools):
    urls = [f"{BASE_URL}/"] + [
        f"{BASE_URL}/{t['slug']}.html" for t in tools
    ]

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        xml += f"  <url><loc>{u}</loc></url>\n"
    xml += "</urlset>"

    write("sitemap.xml", xml)


def generate_rss(tools):
    now = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    items = ""

    for t in tools:
        items += f"""
<item>
  <title>{t['name']} Alternatives</title>
  <link>{BASE_URL}/{t['slug']}.html</link>
  <pubDate>{now}</pubDate>
</item>
"""

    write(
        "rss.xml",
        f"""<?xml version="1.0"?>
<rss version="2.0">
<channel>
<title>Open-Source Analytics Alternatives</title>
<link>{BASE_URL}/</link>
<description>Automatically updated open-source comparisons</description>
{items}
</channel>
</rss>
""",
    )


def main():
    tools = load_tools()

    for t in tools:
        t["slug"] = t["name"].lower().replace(" ", "-")
        gh = fetch_github(t["github"])
        t.update(gh)

    generate_home(tools)

    for t in tools:
        generate_tool_page(t, tools)

    generate_sitemap(tools)
    generate_rss(tools)


if __name__ == "__main__":
    main()
