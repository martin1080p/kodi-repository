#!/usr/bin/env python3
"""Generate addons.xml and addons.xml.md5 for the Kodi repository.

Scans the ``zips/`` tree for ``<addon.id>/<addon.id>-<version>.zip`` files,
reads the ``addon.xml`` embedded in each zip, and concatenates those
``<addon>`` elements into a single ``zips/addons.xml`` manifest plus its MD5
checksum. Metadata is taken verbatim from inside each zip, so this repo never
needs to know an add-on's dependencies or version.

Standard library only. Run from the repo root: ``python _generate.py``.
"""

import hashlib
import os
import sys
import zipfile
from xml.etree import ElementTree as ET

ZIPS_DIR = "zips"
ADDONS_XML = os.path.join(ZIPS_DIR, "addons.xml")
ADDONS_XML_MD5 = os.path.join(ZIPS_DIR, "addons.xml.md5")


def find_addon_xml_in_zip(zip_path):
    """Return the raw bytes of the addon.xml inside ``zip_path``, or None.

    Kodi zips store addon.xml at ``<addon.id>/addon.xml``; we accept any
    path ending in ``/addon.xml`` (or a top-level ``addon.xml``) and pick the
    shallowest match.
    """
    try:
        with zipfile.ZipFile(zip_path) as zf:
            candidates = [
                n for n in zf.namelist()
                if n == "addon.xml" or n.endswith("/addon.xml")
            ]
            if not candidates:
                return None
            candidates.sort(key=lambda n: n.count("/"))
            return zf.read(candidates[0])
    except (zipfile.BadZipFile, OSError) as exc:
        print(f"WARNING: cannot read {zip_path}: {exc}", file=sys.stderr)
        return None


def collect_addon_elements():
    """Return a list of parsed <addon> Elements, one per newest zip found."""
    elements = []
    if not os.path.isdir(ZIPS_DIR):
        print(f"WARNING: '{ZIPS_DIR}/' does not exist; nothing to generate.",
              file=sys.stderr)
        return elements

    for addon_id in sorted(os.listdir(ZIPS_DIR)):
        addon_dir = os.path.join(ZIPS_DIR, addon_id)
        if not os.path.isdir(addon_dir):
            continue

        zips = sorted(
            f for f in os.listdir(addon_dir)
            if f.endswith(".zip") and f.startswith(addon_id + "-")
        )
        if not zips:
            continue

        # Kodi reads all listed versions, but the manifest only needs the
        # metadata block; use the last (highest-sorted) zip's addon.xml.
        zip_path = os.path.join(addon_dir, zips[-1])
        raw = find_addon_xml_in_zip(zip_path)
        if raw is None:
            print(f"WARNING: no addon.xml in {zip_path}; skipping.",
                  file=sys.stderr)
            continue

        try:
            element = ET.fromstring(raw)
        except ET.ParseError as exc:
            print(f"WARNING: bad addon.xml in {zip_path}: {exc}; skipping.",
                  file=sys.stderr)
            continue

        elements.append(element)
        print(f"included {element.get('id')} "
              f"{element.get('version')} from {zips[-1]}")

    return elements


def build_addons_xml(elements):
    """Serialize the <addons> document as UTF-8 bytes (no BOM)."""
    root = ET.Element("addons")
    for el in elements:
        root.append(el)
    ET.indent(root, space="    ")
    body = ET.tostring(root, encoding="unicode")
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            + body + "\n").encode("utf-8")


def main():
    elements = collect_addon_elements()
    if not elements:
        print("ERROR: no add-ons found under zips/; refusing to write an "
              "empty manifest.", file=sys.stderr)
        return 1

    data = build_addons_xml(elements)
    with open(ADDONS_XML, "wb") as fh:
        fh.write(data)

    digest = hashlib.md5(data).hexdigest()
    with open(ADDONS_XML_MD5, "w", encoding="utf-8") as fh:
        fh.write(digest + "\n")

    print(f"wrote {ADDONS_XML} ({len(elements)} add-on(s)) "
          f"and {ADDONS_XML_MD5} ({digest})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
