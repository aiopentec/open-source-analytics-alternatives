import yaml
import requests
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SITE_DIR = BASE_DIR / "site"

TOOLS_FILE = DATA_DIR / "tools.yaml"

SITE_DIR.mkdir(exist_ok=True)

GITHUB_API = "https://api.github.com/repos/{}"


def fetch_github_data(repo):
    try:
        r = requests.get(GITHUB_API.format(repo), timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {
                "stars": data.get("stargazers_count", 0),
                "updated": data.get("updated_at", "")[:10],
                "url": data.get("html_url", "")
            }
    except Exception:
        pass
    return {"stars": 0, "updated": "Unknown", "url": ""}


def load_tools():
    with open(TOOLS_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_file(name, content):
    (SITE_DIR / name).write_text(content.strip(), encoding="utf-8")


def generate_homepage(tools):
    links = "\n".join(
        f"- [{t['name']}]({t['name'].lower().replace(' ', '-')}.html)"
        for t in tools
    )

    content = f"""
# Open-Source Analytics Alternatives

Compare the best **privacy-friendly, open-source alternatives** to proprietary analytics tools.

{links}
"""
    write_file("index.md", content)


def generate_tool_page(tool, all_tools):
    slug = tool["name"].lower().replace(" ", "-")

    gh = fetch_github_data(tool["github"])
    stars = gh["stars"]
    updated = gh["updated"]

    top_pick_html = ""
    if tool.get("top_pick"):
        top_pick_html = f"""
<div class="top-pick">
🏆 <strong>Top Pick:</strong> {tool["name"]}<br>
Recommended for most privacy-focused websites.
</div>
"""

    table_header = "| Tool | Stars | Self-Hosted | Privacy |\n|------|-------|-------------|---------|\n"
    table_rows = ""

    for t in all_tools:
        gh_t = fetch_github_data(t["github"])
        table_rows += (
            f"| {t['name']} | {gh_t['stars']} | "
            f"{'✅' if t.get('self_hosted') else '❌'} | "
            f"{t.get('privacy', 'unknown').title()} |\n"
        )

    content = f"""
# {tool['name']} Alternatives

{tool.get('description', '')}

⭐ **{stars} GitHub stars** • 🕒 **Updated {updated}**

{top_pick_html}

---

## Comparison Table

{table_header}{table_rows}

---

## Hosting & Services

Many open-source analytics tools require hosting and maintenance.

If you prefer a managed option, consider privacy-friendly VPS providers.

_Links may become affiliate links in the future. Recommendations are based on relevance, not payment._
"""
    write_file(f"{slug}.md", content)


def generate_sitemap(tools):
    base = "https://aiopentec.github.io/open-source-analytics-alternatives"
    urls = [f"{base}/"]
    urls += [f"{base}/{t['name'].lower().replace(' ', '-')}.html" for t in tools]

    xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    xml += "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"

    for url in urls:
        xml += f"  <url><loc>{url}</loc></url>\n"

    xml += "</urlset>"
    write_file("sitemap.xml", xml)


def generate_rss(tools):
    base = "https://aiopentec.github.io/open-source-analytics-alternatives"
    now = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

    items = ""
    for t in tools:
        slug = t["name"].lower().replace(" ", "-")
        items += f"""
        <item>
          <title>{t['name']} Alternatives</title>
          <link>{base}/{slug}.html</link>
          <pubDate>{now}</pubDate>
        </item>
        """

    rss = f"""<?xml version="1.0"?>
<rss version="2.0">
<channel>
<title>Open-Source Analytics Alternatives</title>
<link>{base}/</link>
<description>Automatically updated open-source analytics comparisons</description>
{items}
</channel>
</rss>
"""
    write_file("rss.xml", rss)


def main():
    tools = load_tools()

    generate_homepage(tools)

    for tool in tools:
        generate_tool_page(tool, tools)

    generate_sitemap(tools)
    generate_rss(tools)


if __name__ == "__main__":
    main()
