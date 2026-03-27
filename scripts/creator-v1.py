import zipfile
import xml.etree.ElementTree as ET
import json
import re
from pathlib import Path

# Namespace Word
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def extract_paragraphs(docx_path):
    """Extreu tots els paràgrafs amb estil + text concatenat"""
    with zipfile.ZipFile(docx_path) as z:
        xml_content = z.read("word/document.xml")

    root = ET.fromstring(xml_content)

    paragraphs = []

    for i, p in enumerate(root.findall(".//w:p", NS)):
        # Estil
        style_el = p.find(".//w:pStyle", NS)
        style = style_el.get(f"{{{NS['w']}}}val") if style_el is not None else None

        # Text (concatenar tots els w:t)
        texts = []
        for t in p.findall(".//w:t", NS):
            if t.text:
                texts.append(t.text)

        full_text = "".join(texts).strip()

        if full_text:
            paragraphs.append({
                "index": i,
                "style": style,
                "text": full_text
            })

    return paragraphs


def parse_modules(paragraphs, source_file):
    modules = []
    current_module = None
    ra_counter = 0
    inside_ra_section = False

    for p in paragraphs:
        text = p["text"]
        style = p["style"]

        # ---------- MÒDUL ----------
        if style == "Ttol2MP":
            # Guardar l'anterior
            if current_module:
                modules.append(current_module)

            match = re.match(r"(\d{4})\.\s*(.+)", text)
            if match:
                module_id = match.group(1)
                module_name = match.group(2)

                current_module = {
                    "id": module_id,
                    "name": module_name,
                    "hours": None,
                    "ra": []
                }

                ra_counter = 0
                inside_ra_section = False

            continue

        if not current_module:
            continue

        # ---------- HORES ----------
        if "Durada:" in text:
            match = re.search(r"Durada:\s*(\d+)", text)
            if match:
                current_module["hours"] = int(match.group(1))

        # ---------- INICI SECCIÓ RA ----------
        if "Resultats d’aprenentatge" in text:
            inside_ra_section = True
            continue

        # ---------- RA ----------
        if inside_ra_section and style == "Ttol3UF":
            ra_counter += 1

            ra = {
                "code": f"RA{ra_counter}",
                "code_full": f"{current_module['id']}_RA{ra_counter}",
                "short_description": text[:80],
                "long_description": text,
                "source": {
                    "file": source_file,
                    "paragraph_index": p["index"],
                    "confidence": "docx_style_ttol3uf"
                }
            }

            current_module["ra"].append(ra)

    # Afegir l'últim mòdul
    if current_module:
        modules.append(current_module)

    return modules


def build_json(docx_path):
    paragraphs = extract_paragraphs(docx_path)
    modules = parse_modules(paragraphs, Path(docx_path).name)

    return {
        "cycle": "smx",
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