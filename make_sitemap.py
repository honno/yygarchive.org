#!/usr/bin/env python
import xml.etree.ElementTree as ET
from urllib.parse import quote

from app.models import Game

SITE_URL = "https://yygarchive.org"


def add_url(element: ET.Element, loc: str, **kw) -> None:
    url = ET.SubElement(element, "url")
    ET.SubElement(url, "loc").text = loc
    for k, v in kw.items():
        ET.SubElement(url, k).text = v


def make_tree() -> ET.ElementTree:
    urlset = ET.Element(
        "urlset", {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    )

    add_url(urlset, f"{SITE_URL}/", priority="1.0")
    add_url(urlset, f"{SITE_URL}/about")
    for game in Game.select(Game.id):
        add_url(urlset, f"{SITE_URL}/game/{game.id}")
    for row in Game.select(Game.developer).distinct():
        developer = quote(row.developer.strip())
        add_url(urlset, f"{SITE_URL}/developer/{developer}")

    ET.indent(urlset, space="  ", level=0)

    return ET.ElementTree(urlset)


def main():
    tree = make_tree()
    tree.write("sitemap.xml", encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    main()
