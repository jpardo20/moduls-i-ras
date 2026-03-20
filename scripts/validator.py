#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

# =========================
# PATHS
# =========================

BASE_DIR = Path(__file__).resolve().parent

json_path = (BASE_DIR / "../../ras/docs/smx.json").resolve()
docx_path = BASE_DIR / "smx/mp_IC10_sistemes_microinformatics_xarxes_20240424.docx"

# json_path = (BASE_DIR / "../../ras/docs/dam.json").resolve()
# docx_path = BASE_DIR / "dam/mp_ICB0_desenvolupament_aplicacions_multiplataforma_20240424.docx"




# =========================
# NORMALITZACIÓ
# =========================

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# =========================
# EXTREURE TEXT DOCX
# =========================

from zipfile import ZipFile
import xml.etree.ElementTree as ET

def extract_full_text_from_docx(docx_path: Path):
    with ZipFile(docx_path, "r") as docx:
        with docx.open("word/document.xml") as xml_file:
            tree = ET.parse(xml_file)
            root = tree.getroot()

    paragraphs = []
    current_text = []

    for elem in root.iter():
        if elem.tag.endswith("}p"):
            if current_text:
                paragraphs.append("".join(current_text))
                current_text = []

        elif elem.tag.endswith("}t"):
            if elem.text:
                current_text.append(elem.text)

    if current_text:
        paragraphs.append("".join(current_text))

    return " ".join(paragraphs)

# =========================
# CARREGAR JSON
# =========================

def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# =========================
# VALIDACIÓ
# =========================

def validate(dam_data, full_text):
    results = []

    full_text_norm = normalize(full_text)

    # format correcte: dict amb "modules"
    modules = dam_data.get("modules", [])

    for module in modules:
        mod_code = module.get("id")

        # 🔥 CLAU CORRECTA
        for ra in module.get("ra", []):
            code_full = ra.get("code_full")
            expected = ra.get("long_description", "")

            expected_norm = normalize(expected)

            if not expected_norm:
                results.append((code_full, "ERROR", "Descripció buida"))
                continue

            if expected_norm in full_text_norm:
                results.append((code_full, "OK", "Text trobat"))
            else:
                results.append((code_full, "ERROR", "No trobat"))
            
            if expected_norm not in full_text_norm:
                print("\n--- DEBUG ERROR ---")
                print("RA:", code_full)
                print("EXPECTED:")
                print(expected[:200])
                print("------------------")

    return results

# =========================
# PRINT
# =========================

def print_results(results):
    ok = 0
    error = 0

    print("\n==============================")
    print("VALIDACIÓ DAM vs DOCX")
    print("==============================\n")

    for code, status, msg in results:
        print(f"[{status}] {code} → {msg}")

        if status == "OK":
            ok += 1
        else:
            error += 1



    print("\n------------------------------")
    print(f"OK: {ok}")
    print(f"ERROR: {error}")
    print("------------------------------\n")

# =========================
# MAIN
# =========================

def main():
    

    print(f"[INFO] JSON: {json_path}")
    print(f"[INFO] DOCX XML: {docx_path}")

    dam_data = load_json(json_path)
    
    full_text = extract_full_text_from_docx(docx_path)


    print(f"[DEBUG] Longitud text DOCX: {len(full_text)} caràcters")

    results = validate(dam_data, full_text)

    print_results(results)

if __name__ == "__main__":
    main()