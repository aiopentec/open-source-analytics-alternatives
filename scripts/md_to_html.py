from pathlib import Path
from markdown import markdown

SITE_DIR = Path("site")

for md in SITE_DIR.glob("*.md"):
    html_body = markdown(md.read_text(encoding="utf-8"))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{md.stem.replace('-', ' ').title()}</title>
</head>
<body>
{html_body}
</body>
</html>
"""

    md.with_suffix(".html").write_text(html, encoding="utf-8")
