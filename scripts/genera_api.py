import json
from pathlib import Path
from datetime import datetime, timezone


DATA_DIR = Path("docs/data")
API_DIR = Path("docs/api/v1")

CICLES_FONT = [
    "smx",
    "dam"
]


def llegir_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def escriure_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def text_descripcio(element: dict) -> str:
    return (
        element.get("long_description")
        or element.get("description")
        or element.get("short_description")
        or element.get("text")
        or ""
    )


def normalitzar_criteris(criteria: list) -> dict:
    criteris = {}

    for index, criteri in enumerate(criteria, start=1):
        codi = (
            criteri.get("code")
            or criteri.get("id")
            or criteri.get("criterion")
            or f"CA{index}"
        )

        criteris[codi] = {
            "codi": codi,
            "codi_complet": criteri.get("code_full", ""),
            "descripcio": text_descripcio(criteri),
            "font": criteri.get("source", {}),
            "dades_originals": criteri
        }

    return criteris


def normalitzar_ra(ra_llista: list) -> dict:
    resultats = {}

    for index, ra in enumerate(ra_llista, start=1):
        codi = ra.get("code") or f"RA{index}"

        resultats[codi] = {
            "ordre": index,
            "codi": codi,
            "codi_complet": ra.get("code_full", ""),
            "descripcio": text_descripcio(ra),
            "descripcio_curta": ra.get("short_description", ""),
            "font": ra.get("source", {}),
            "criteris_avaluacio": normalitzar_criteris(
                ra.get("criteria", [])
            )
        }

    return resultats


def normalitzar_modul(modul: dict, cicle: dict, data_generacio: str) -> dict:
    ra = modul.get("ra", [])
    empresa = modul.get("company", {})

    return {
        "api_version": "1.0",
        "codi": modul.get("id", ""),
        "nom": modul.get("name", ""),
        "cicle": {
            "codi": cicle.get("cycle_code", ""),
            "nom": cicle.get("cycle", "")
        },
        "hores": {
            "total": modul.get("hours", 0)
        },
        "empresa": {
            "te_estada": bool(empresa.get("enabled", False))
        },
        "num_ra": len(ra),
        "resultats_aprenentatge": normalitzar_ra(ra),
        "metadata": {
            "font": "docs/data",
            "fitxer_origen": f"{cicle.get('cycle_code', '').lower()}.json",
            "estat": "generat",
            "data_generacio": data_generacio
        }
    }


def generar_api_cicle(nom_fitxer_cicle: str, data_generacio: str) -> tuple[dict, list[dict]]:
    path = DATA_DIR / f"{nom_fitxer_cicle}.json"

    if not path.exists():
        print(f"AVÍS: no existeix {path}. S'ignora.")
        return {}, []

    dades_cicle = llegir_json(path)

    codi_cicle = dades_cicle.get("cycle_code", nom_fitxer_cicle).lower()
    moduls_api = []

    for modul in dades_cicle.get("modules", []):
        modul_api = normalitzar_modul(modul, dades_cicle, data_generacio)
        codi_modul = modul_api["codi"]

        if not codi_modul:
            print("AVÍS: mòdul sense codi. S'ignora.")
            continue

        escriure_json(API_DIR / "moduls" / f"{codi_modul}.json", modul_api)

        moduls_api.append({
            "codi": codi_modul,
            "nom": modul_api["nom"],
            "hores_total": modul_api["hores"]["total"],
            "te_empresa": modul_api["empresa"]["te_estada"],
            "num_ra": modul_api["num_ra"],
            "url": f"../moduls/{codi_modul}.json"
        })

    cicle_api = {
        "api_version": "1.0",
        "codi": dades_cicle.get("cycle_code", ""),
        "nom": dades_cicle.get("cycle", ""),
        "num_moduls": len(moduls_api),
        "moduls": moduls_api,
        "metadata": {
            "font": f"docs/data/{nom_fitxer_cicle}.json",
            "estat": "generat",
            "data_generacio": data_generacio
        }
    }

    escriure_json(API_DIR / "cicles" / f"{codi_cicle}.json", cicle_api)

    return cicle_api, moduls_api


def generar_index(cicles_api: list[dict], moduls_index: list[dict], data_generacio: str) -> None:
    index = {
        "api_version": "1.0",
        "projecte": "moduls-i-ras",
        "descripcio": "API estàtica de consulta de mòduls professionals, resultats d'aprenentatge i criteris d'avaluació.",
        "base_path": "docs/api/v1",
        "cicles": {},
        "moduls": {},
        "metadata": {
            "estat": "generat",
            "data_generacio": data_generacio
        }
    }

    for cicle in cicles_api:
        codi = cicle.get("codi", "")
        if not codi:
            continue

        index["cicles"][codi] = {
            "nom": cicle.get("nom", ""),
            "num_moduls": cicle.get("num_moduls", 0),
            "url": f"cicles/{codi.lower()}.json"
        }

    for modul in moduls_index:
        codi = modul.get("codi", "")
        if not codi:
            continue

        index["moduls"][codi] = {
            "nom": modul.get("nom", ""),
            "hores_total": modul.get("hores_total", 0),
            "te_empresa": modul.get("te_empresa", False),
            "num_ra": modul.get("num_ra", 0),
            "url": f"moduls/{codi}.json"
        }

    escriure_json(API_DIR / "index.json", index)


def main() -> None:
    data_generacio = datetime.now(timezone.utc).isoformat()

    cicles_api = []
    moduls_index = []

    for nom_fitxer_cicle in CICLES_FONT:
        cicle_api, moduls_api = generar_api_cicle(
            nom_fitxer_cicle,
            data_generacio
        )

        if cicle_api:
            cicles_api.append(cicle_api)
            moduls_index.extend(moduls_api)

    generar_index(cicles_api, moduls_index, data_generacio)

    print("API estàtica generada correctament.")
    print(f"Directori: {API_DIR}")
    print(f"Cicles generats: {len(cicles_api)}")
    print(f"Mòduls generats: {len(moduls_index)}")


if __name__ == "__main__":
    main()