import yaml, requests, os
from datetime import datetime

os.makedirs("site", exist_ok=True)

tools = yaml.safe_load(open("data/tools.yaml"))
top_picks = yaml.safe_load(open("config/top_picks.yaml"))
top_pick_html = ""
if tool.get("top_pick"):
    top_pick_html = f"""
<div class="top-pick">
🏆 <strong>Top Pick:</strong> {tool["name"]}<br>
Recommended for most privacy-focused websites.
</div>
"""

def github_stats(repo_url):
    api = repo_url.replace("https://github.com/", "https://api.github.com/repos/")
    r = requests.get(api, timeout=20)
    if r.status_code != 200:
        return 0, ""
    j = r.json()
    return j.get("stargazers_count", 0), (j.get("updated_at", "") or "")[:10]

pages = []

for tool in tools:
    stars, updated = github_stats(tool["repo"])
    slug = tool["slug"]
    path = f"site/{slug}.md"
    pages.append(slug)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {tool['name']} Alternatives\n\n")
        f.write(f"{tool['description']}\n\n")
        if updated:
            f.write(f"⭐ {stars} GitHub stars • 🕒 Updated {updated}\n\n")
        else:
            f.write(f"⭐ {stars} GitHub stars\n\n")

        if tool['name'] in top_picks.get(tool['category'], []):
            f.write(f"## 🏆 Top Pick: {tool['name']}\n")
            f.write("> Recommended for most privacy-focused websites.\n\n")
            f.write("> 🔗 Managed hosting available → See providers below\n\n")
            f.write("---\n\n")

        f.write("## Comparison Table\n\n")
        f.write("| Tool | Stars | Self-Hosted | Privacy |\n")
        f.write("|------|-------|------------|---------|\n")
        f.write(f"| {tool['name']} | {stars} | ✅ | ✅ |\n\n")

        f.write("## Hosting & Services\n\n")
        f.write("Many open-source analytics tools require hosting and maintenance.\n\n")
        f.write("If you prefer a managed option, consider privacy-friendly VPS providers.\n\n")
        f.write("*Links may become affiliate links in the future. Recommendations are based on relevance, not payment.*\n")

# Index
with open("site/index.md", "w", encoding="utf-8") as f:
    f.write("# Open-Source Analytics Alternatives\n\n")
    for p in pages:
        f.write(f"- [{p.replace('-', ' ').title()}]({p}.html)\n")

# Sitemap
with open("site/sitemap.xml", "w", encoding="utf-8") as f:
    f.write("<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n")
    for p in pages:
        f.write(f"<url><loc>/{p}.html</loc></url>\n")
    f.write("</urlset>")

# RSS
with open("site/rss.xml", "w", encoding="utf-8") as f:
    f.write("<rss version='2.0'><channel>\n")
    f.write("<title>Open-Source Analytics Alternatives</title>\n")
    for p in pages:
        f.write(f"<item><title>{p}</title><link>/{p}.html</link></item>\n")
    f.write("</channel></rss>")

print("Site generated successfully")
