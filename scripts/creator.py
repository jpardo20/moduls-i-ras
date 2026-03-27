import zipfile
import xml.etree.ElementTree as ET
import json
import re
from pathlib import Path

# Namespace Word
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def extract_cycle_code(filename):
    match = re.search(r"mp_([A-Z0-9]+)_", filename)
    return match.group(1) if match else "UNKNOWN"


def extract_paragraphs(docx_path):
    """Extreu paràgrafs amb estil + text + info de numeració"""
    with zipfile.ZipFile(docx_path) as z:
        xml_content = z.read("word/document.xml")

    root = ET.fromstring(xml_content)

    paragraphs = []

    for i, p in enumerate(root.findall(".//w:p", NS)):
        # Estil
        style_el = p.find(".//w:pStyle", NS)
        style = style_el.get(f"{{{NS['w']}}}val") if style_el is not None else None

        # Text
        texts = []
        for t in p.findall(".//w:t", NS):
            if t.text:
                texts.append(t.text)

        full_text = "".join(texts).strip()

        # Numeració (criteris)
        num_pr = p.find(".//w:numPr", NS)
        has_numbering = num_pr is not None

        if full_text:
            paragraphs.append({
                "index": i,
                "style": style,
                "text": full_text,
                "has_numbering": has_numbering
            })

    return paragraphs


def parse_modules(paragraphs, source_file, cycle_code):
    modules_dict = {}
    current_module = None
    current_ra = None

    ra_counter = 0
    ca_counter = 0

    inside_description = False
    inside_ra_section = False
    inside_criteria_section = False

    for p in paragraphs:
        text = p["text"]
        style = p["style"]
        has_numbering = p["has_numbering"]

        # ---------- ACTIVAR SECCIÓ BONA ----------
        if "Descripció dels mòduls" in text:
            inside_description = True
            continue

        if not inside_description:
            continue

        # ---------- MÒDUL ----------
        if style == "Ttol2MP":
            match = re.match(r"(\d{4})\.\s*(.+)", text)
            if match:
                module_id = match.group(1)
                module_name = match.group(2)

                if module_id not in modules_dict:
                    modules_dict[module_id] = {
                        "id": module_id,
                        "name": module_name,
                        "hours": None,
                        "ra": []
                    }

                current_module = modules_dict[module_id]

                # Reset estat
                current_ra = None
                ra_counter = 0
                inside_ra_section = False
                inside_criteria_section = False

            continue

        if not current_module:
            continue

        # ---------- HORES ----------
        if "Durada:" in text:
            match = re.search(r"Durada:\s*(\d+)", text)
            if match:
                current_module["hours"] = int(match.group(1))

        # ---------- INICI RA ----------
        if "Resultats d’aprenentatge" in text:
            inside_ra_section = True
            continue

        # ---------- RA ----------
        if inside_ra_section and style == "Ttol3UF":
            ra_counter += 1
            ca_counter = 0
            inside_criteria_section = False

            current_ra = {
                "code": f"RA{ra_counter}",
                "code_full": f"{cycle_code}_{current_module['id']}_RA{ra_counter}",
                "short_description": text[:80],
                "long_description": text,
                "criteria": [],
                "source": {
                    "file": source_file,
                    "paragraph_index": p["index"],
                    "confidence": "docx_style_ttol3uf"
                }
            }

            current_module["ra"].append(current_ra)
            continue

        # ---------- INICI CRITERIS ----------
        if "Criteris d'avaluació" in text:
            inside_criteria_section = True
            continue

        # ---------- CRITERIS ----------
        if (
            inside_criteria_section
            and current_ra
            and style == "TextdeldocumentMP"
            and has_numbering
        ):
            ca_counter += 1

            criterion = {
                "code": f"CA{ca_counter:02d}",
                "code_full": f"{cycle_code}_{current_module['id']}_RA{ra_counter}_CA{ca_counter:02d}",
                "description": text,
                "source": {
                    "file": source_file,
                    "paragraph_index": p["index"],
                    "confidence": "docx_numbered_text"
                }
            }

            current_ra["criteria"].append(criterion)

    return list(modules_dict.values())


def build_json(docx_path):
    filename = Path(docx_path).name
    cycle_code = extract_cycle_code(filename)

    paragraphs = extract_paragraphs(docx_path)
    modules = parse_modules(paragraphs, filename, cycle_code)

    return {
        "cycle": "smx",
        "cycle_code": cycle_code,
        "modules": modules
    }


if __name__ == "__main__":
    DOCX_PATH = "docs/amagats/smx/mp_IC10_sistemes_microinformatics_xarxes_20240424.docx"
    OUTPUT_PATH = "tmp/smx.generated.json"

    Path("tmp").mkdir(exist_ok=True)

    data = build_json(DOCX_PATH)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✔ JSON generat a: {OUTPUT_PATH}")