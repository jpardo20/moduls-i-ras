import json
import os
import shutil
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "docs" / "data"
API_DIR = BASE_DIR / "docs" / "api" / "v1"


CICLES_INFO = {
    "smx": {
        "fitxer": "smx.json",
        "fitxer_local": "moduls-locals-smx.json",
        "codi": "SMX",
        "codi_oficial": "IC10",
        "nom": "Sistemes Microinformàtics i Xarxes",
        "slug": "smx"
    },
    "dam": {
        "fitxer": "dam.json",
        "fitxer_local": "moduls-locals-dam.json",
        "codi": "DAM",
        "codi_oficial": "ICB0",
        "nom": "Desenvolupament d'Aplicacions Multiplataforma",
        "slug": "dam"
    }
}


def llegir_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def escriure_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def netejar_api() -> None:
    if API_DIR.exists():
        shutil.rmtree(API_DIR)

    (API_DIR / "cicles").mkdir(parents=True, exist_ok=True)
    (API_DIR / "moduls").mkdir(parents=True, exist_ok=True)
    (API_DIR / "schemas").mkdir(parents=True, exist_ok=True)


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
            or f"CA{index:02d}"
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


def normalitzar_modul(
    modul: dict,
    cicle_info: dict,
    data_generacio: str,
    fitxer_origen: str,
    tipus_curriculum: str,
) -> dict:
    ra = modul.get("ra", [])
    empresa = modul.get("company", {})
    hores_total = modul.get("hours", 0)
    hores_centre = modul.get("school_hours")
    hores_empresa = empresa.get("hours")

    te_desglossament = (
        hores_centre is not None
        or hores_empresa is not None
    )
    if te_desglossament:
        if hores_centre is None or hores_empresa is None:
            raise ValueError(
                f"Desglossament d'hores incomplet al mòdul "
                f"{modul.get('id', '')}"
            )
        if hores_centre + hores_empresa != hores_total:
            raise ValueError(
                f"Desglossament d'hores incoherent al mòdul "
                f"{modul.get('id', '')}: "
                f"{hores_centre} + {hores_empresa} != {hores_total}"
            )
        empresa_habilitada = empresa.get("enabled")
        if (
            empresa_habilitada is not None
            and bool(empresa_habilitada) != (hores_empresa > 0)
        ):
            raise ValueError(
                f"Indicador d'empresa incoherent al mòdul "
                f"{modul.get('id', '')}"
            )

    hores_api = {"total": hores_total}
    if te_desglossament:
        hores_api.update({
            "centre": hores_centre,
            "empresa": hores_empresa,
        })

    te_estada = (
        hores_empresa > 0
        if hores_empresa is not None
        else bool(empresa.get("enabled", False))
    )

    modul_api = {
        "api_version": "1.0",
        "codi": modul.get("id", ""),
        "nom": modul.get("name", ""),
        "cicle": {
            "codi": cicle_info["codi"],
            "codi_oficial": cicle_info["codi_oficial"],
            "nom": cicle_info["nom"],
            "slug": cicle_info["slug"]
        },
        "hores": hores_api,
        "empresa": {
            "te_estada": te_estada
        },
        "num_ra": len(ra),
        "resultats_aprenentatge": normalitzar_ra(ra),
        "metadata": {
            "font": "docs/data",
            "fitxer_origen": fitxer_origen,
            "estat": "generat",
            "data_generacio": data_generacio
        }
    }

    if tipus_curriculum == "local":
        modul_api["metadata"]["tipus_curriculum"] = "local"

    font_curricular = modul.get("source")
    if font_curricular:
        modul_api["font_curricular"] = font_curricular

    return modul_api


def carregar_fonts_moduls(
    cicle_info: dict,
) -> list[tuple[str, str, list[dict]]]:
    fonts = []

    for tipus_curriculum, clau_fitxer in (
        ("oficial", "fitxer"),
        ("local", "fitxer_local"),
    ):
        nom_fitxer = cicle_info.get(clau_fitxer, "")
        if not nom_fitxer:
            continue

        path = DATA_DIR / nom_fitxer
        if not path.exists():
            print(f"AVÍS: no existeix {path}. S'ignora.")
            continue

        dades = llegir_json(path)
        moduls = dades.get("modules", [])
        if tipus_curriculum == "local" and not moduls:
            continue

        fonts.append((
            tipus_curriculum,
            nom_fitxer,
            moduls,
        ))

    return fonts


def generar_api_cicle(cicle_info: dict, data_generacio: str) -> tuple[dict, list[dict]]:
    fonts_moduls = carregar_fonts_moduls(cicle_info)
    if not fonts_moduls:
        return {}, []

    moduls_api = []
    codis_modul = set()

    for tipus_curriculum, nom_fitxer, moduls in fonts_moduls:
        for modul in moduls:
            modul_api = normalitzar_modul(
                modul,
                cicle_info,
                data_generacio,
                nom_fitxer,
                tipus_curriculum,
            )
            codi_modul = modul_api["codi"]

            if not codi_modul:
                print("AVÍS: mòdul sense codi. S'ignora.")
                continue

            if codi_modul in codis_modul:
                raise ValueError(
                    f"Codi de mòdul duplicat al cicle "
                    f"{cicle_info['slug']}: {codi_modul}"
                )

            codis_modul.add(codi_modul)
            escriure_json(
                API_DIR / "moduls" / f"{codi_modul}.json",
                modul_api,
            )

            moduls_api.append({
                "codi": codi_modul,
                "nom": modul_api["nom"],
                "hores_total": modul_api["hores"]["total"],
                "te_empresa": modul_api["empresa"]["te_estada"],
                "num_ra": modul_api["num_ra"],
                "url": f"../moduls/{codi_modul}.json"
            })

    metadata = {
        "font": f"docs/data/{cicle_info['fitxer']}",
        "estat": "generat",
        "data_generacio": data_generacio
    }
    if len(fonts_moduls) > 1:
        metadata["fonts"] = [
            f"docs/data/{nom_fitxer}"
            for _, nom_fitxer, _ in fonts_moduls
        ]

    cicle_api = {
        "api_version": "1.0",
        "codi": cicle_info["codi"],
        "codi_oficial": cicle_info["codi_oficial"],
        "nom": cicle_info["nom"],
        "slug": cicle_info["slug"],
        "num_moduls": len(moduls_api),
        "moduls": moduls_api,
        "metadata": metadata
    }

    escriure_json(API_DIR / "cicles" / f"{cicle_info['slug']}.json", cicle_api)

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
        slug = cicle.get("slug", "")

        if not codi or not slug:
            continue

        index["cicles"][codi] = {
            "codi_oficial": cicle.get("codi_oficial", ""),
            "nom": cicle.get("nom", ""),
            "slug": slug,
            "num_moduls": cicle.get("num_moduls", 0),
            "url": f"cicles/{slug}.json"
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
    data_generacio = os.getenv(
        "API_GENERATION_TIMESTAMP"
    ) or datetime.now(timezone.utc).isoformat()

    netejar_api()

    cicles_api = []
    moduls_index = []

    for cicle_info in CICLES_INFO.values():
        cicle_api, moduls_api = generar_api_cicle(
            cicle_info,
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
