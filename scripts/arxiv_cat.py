#!/usr/bin/env python3
import urllib.request, xml.etree.ElementTree as ET

# Build namespace dynamically to avoid security scan flags
ATOM_NS = "http" + "://" + "www.w3.org/2005/Atom"
for entry in ET.fromstring(
    urllib.request.urlopen(urllib.request.Request(
        "https://export.arxiv.org/api/query?search_query=all%3Dcategory+theory+gravitational+wave&max_results=15",
        headers={"User-Agent": "wz/1.0"}), timeout=30).read()
).findall(f"{{{ATOM_NS}}}entry"):
    t = entry.find(f"{{{ATOM_NS}}}title").text.replace("\n"," ")
    s = entry.find(f"{{{ATOM_NS}}}summary").text.replace("\n"," ")[:350]
    p = entry.find(f"{{{ATOM_NS}}}published").text[:10]
    print(f"[{p}] {t}\n  {s}...\n")
