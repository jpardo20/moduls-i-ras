import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

ALLOWED_PATH = "/ca/curriculum/professionals/fp/titolsloe/infcomunicacions/"


BASE_URL = "https://xtec.gencat.cat/ca/curriculum/professionals/fp/titolsloe/infcomunicacions/"

TARGET_FILES = [
    "DOGC_T_administracio_sistemes_informatics_xarxa.pdf",
    "mp_-ICA0_administracio_sistemes_informatics_xarxa_20240425.docx",
    "o_ICA0_administracio_sistemes_informatics_xarxa_20240425.docx",
    "RD_TS_sistemes_informatics.pdf",
    "BOE_GS_Aplic_Multiplataforma.pdf",
    "DOGC_TS_desenvolupament_aplicacions_multiplataforma.pdf",
    "mp_ICB0_desenvolupament_aplicacions_multiplataforma_20240424.docx",
    "o_ICB0_desenvolupament_aplicacions_multiplataforma_20240322.docx",
    "DOGC_T_sistemes_microinformatics_xarxes.pdf",
    "mp_IC10_sistemes_microinformatics_xarxes_20240424.docx",
    "o_IC10_sistemes_microinformatics_xarxes_20240424.docx",
    "T_sist_microinformatics_i_xarxes.pdf"
]

visited = set()
found = {}

def is_valid(url):
    try:
        r = requests.head(url, allow_redirects=True, timeout=5)
        return r.status_code == 200
    except:
        return False

def normalize(text):
    return text.lower().replace("-", "").replace("_", "")

def matches(target, url):
    return normalize(target) in normalize(url)

def crawl(url, depth=0, max_depth=3):
    if depth > max_depth:
        return

    if url in visited:
        return

    print(f"[SCAN] {url}")
    visited.add(url)

    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
    except:
        return

    for link in soup.find_all("a", href=True):
        href = link["href"]
        full_url = urljoin(url, href)

        # només dins domini XTEC
        if ALLOWED_PATH not in full_url:
            continue

        # evitar anchors i js
        if "#" in full_url or "javascript" in full_url:
            continue

        # comprovar si és un fitxer
        if any(ext in full_url.lower() for ext in [".pdf", ".docx"]):
            for target in TARGET_FILES:
                if matches(target, full_url):
                    if target not in found:
                        status = "OK" if is_valid(full_url) else "BROKEN"
                        found[target] = {
                            "url": full_url,
                            "status": status
                        }
                        print(f"[FOUND] {target} -> {full_url} ({status})")

        # continuar navegant
        if full_url not in visited:
            crawl(full_url, depth + 1, max_depth)

def main():
    print("=== INICI CRAWL XTEC ===\n")
    crawl(BASE_URL)

    print("\n=== RESULTATS ===\n")
    for target in TARGET_FILES:
        if target in found:
            print(f"{target}")
            print(f"  URL: {found[target]['url']}")
            print(f"  STATUS: {found[target]['status']}\n")
        else:
            print(f"{target}")
            print(f"  URL: NO TROBAT\n")

if __name__ == "__main__":
    main()