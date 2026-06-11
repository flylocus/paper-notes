#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify paper metadata from arXiv API and optionally enrich from PDF first page.

Usage:
  python3 verify_metadata.py --arxiv-id 2604.09285 --out fused/2604.09285_metadata.json
"""

import argparse
import json
import os
import re
import subprocess
import tempfile
import urllib.request
import xml.etree.ElementTree as ET

NS = {"atom": "http://www.w3.org/2005/Atom"}


def fetch_arxiv_metadata(arxiv_id: str):
    url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
    root = ET.fromstring(urllib.request.urlopen(url, timeout=20).read())
    entry = root.find("atom:entry", NS)
    if entry is None:
        raise RuntimeError(f"No arXiv entry found for {arxiv_id}")
    title = entry.find("atom:title", NS).text.strip().replace("\n", " ")
    summary = entry.find("atom:summary", NS).text.strip().replace("\n", " ")
    published = entry.find("atom:published", NS).text.strip()
    authors = [a.find("atom:name", NS).text.strip() for a in entry.findall("atom:author", NS)]
    categories = [c.attrib.get("term") for c in entry.findall("atom:category", NS)]
    return {
        "arxiv_id": arxiv_id,
        "title": title,
        "summary": summary,
        "published": published,
        "authors": authors,
        "categories": categories,
        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        "abs_url": f"https://arxiv.org/abs/{arxiv_id}",
    }


def download_pdf(pdf_url: str, out_path: str):
    urllib.request.urlretrieve(pdf_url, out_path)
    return out_path


def extract_first_page_text(pdf_path: str):
    try:
        out = subprocess.check_output([
            "pdftotext", "-f", "1", "-l", "1", pdf_path, "-"
        ], stderr=subprocess.STDOUT, timeout=30)
        return out.decode("utf-8", "ignore")
    except Exception:
        return ""


def parse_affiliations_from_first_page(text: str):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    affils = []
    affiliation_markers = [
        "University",
        "Institute",
        "Researcher",
        "Laboratory",
        "College",
        "Telecommunications",
        "Hong Kong",
        "China",
        "Google",
        "DeepMind",
    ]
    for ln in lines:
        if "©" in ln or "rights reserved" in ln.lower():
            continue
        if any(k in ln for k in affiliation_markers):
            if ln not in affils:
                affils.append(ln)
    return affils[:12]


def overrides_path_for(out_path: str) -> str:
    return os.path.splitext(out_path)[0] + "_overrides.json"


def load_json_if_exists(path: str):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def apply_affiliation_protection(meta: dict, out_path: str) -> dict:
    """Manual corrections must survive produce re-runs.

    Priority: overrides file > previous non-empty value (when new extraction
    is empty) > fresh PDF extraction.
    """
    overrides = load_json_if_exists(overrides_path_for(out_path)) or {}
    previous = load_json_if_exists(out_path) or {}

    applied_keys = []
    for key, value in overrides.items():
        meta[key] = value
        applied_keys.append(key)
    if applied_keys:
        meta["override_applied_keys"] = applied_keys

    if "affiliations" in overrides and overrides["affiliations"]:
        meta["affiliations_source"] = "override"
    elif not meta.get("affiliations") and previous.get("affiliations"):
        meta["affiliations"] = previous["affiliations"]
        meta["affiliations_source"] = "preserved_previous"
    elif meta.get("affiliations"):
        meta["affiliations_source"] = "pdf_extraction"
    else:
        meta["affiliations_source"] = "empty"
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arxiv-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--keep-pdf", action="store_true")
    args = ap.parse_args()

    meta = fetch_arxiv_metadata(args.arxiv_id)

    with tempfile.TemporaryDirectory() as td:
        pdf_path = os.path.join(td, f"{args.arxiv_id}.pdf")
        try:
            download_pdf(meta["pdf_url"], pdf_path)
            text = extract_first_page_text(pdf_path)
            affils = parse_affiliations_from_first_page(text)
            meta["pdf_first_page_extracted"] = bool(text.strip())
            meta["affiliations"] = affils
            if args.keep_pdf:
                keep_path = os.path.splitext(args.out)[0] + ".pdf"
                os.makedirs(os.path.dirname(keep_path), exist_ok=True)
                with open(pdf_path, "rb") as rf, open(keep_path, "wb") as wf:
                    wf.write(rf.read())
                meta["saved_pdf"] = keep_path
        except Exception as e:
            meta["pdf_first_page_extracted"] = False
            meta["affiliations"] = []
            meta["pdf_error"] = str(e)

    meta = apply_affiliation_protection(meta, args.out)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(args.out)
    print(json.dumps({
        "arxiv_id": meta["arxiv_id"],
        "title": meta["title"],
        "authors": len(meta["authors"]),
        "affiliations": len(meta.get("affiliations", [])),
        "affiliations_source": meta.get("affiliations_source", ""),
        "pdf_first_page_extracted": meta.get("pdf_first_page_extracted", False)
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
