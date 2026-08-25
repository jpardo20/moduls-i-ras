from __future__ import annotations

import json
from pathlib import Path

from scripts import genera_api


ARREL = Path(__file__).resolve().parents[1]
DATA_DIR = ARREL / "docs" / "data"


def _llegir_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_mopt1_te_nou_ra_i_cinquanta_quatre_ca() -> None:
    dades = _llegir_json(
        DATA_DIR / "moduls-locals-smx.json"
    )
    modul = dades["modules"][0]

    assert modul["id"] == "MOPT1"
    assert modul["hours"] == 99
    assert modul["company"]["enabled"] is False
    assert len(modul["ra"]) == 9
    assert sum(
        len(ra["criteria"])
        for ra in modul["ra"]
    ) == 54


def test_ponderacions_mopt1_sumen_cent() -> None:
    ponderacions = _llegir_json(
        DATA_DIR / "ponderacions.json"
    )["IC10"]["MOPT1"]

    assert ponderacions == {
        "RA1": 14,
        "RA2": 14,
        "RA3": 14,
        "RA4": 10,
        "RA5": 14,
        "RA6": 10,
        "RA7": 10,
        "RA8": 9,
        "RA9": 5,
    }
    assert sum(ponderacions.values()) == 100


def test_0227_te_el_desglossament_oficial_d_hores() -> None:
    dades = _llegir_json(DATA_DIR / "smx.json")
    modul = next(
        modul
        for modul in dades["modules"]
        if modul["id"] == "0227"
    )

    assert modul["hours"] == 198
    assert modul["school_hours"] == 132
    assert modul["company"] == {
        "enabled": True,
        "hours": 66,
    }


def test_generador_rebutja_un_desglossament_incoherent() -> None:
    modul = {
        "id": "PROVA",
        "name": "Mòdul de prova",
        "hours": 198,
        "school_hours": 132,
        "company": {
            "enabled": True,
            "hours": 60,
        },
        "ra": [],
    }

    try:
        genera_api.normalitzar_modul(
            modul,
            genera_api.CICLES_INFO["smx"],
            "2026-07-24T00:00:00+00:00",
            "prova.json",
            "oficial",
        )
    except ValueError as error:
        assert "132 + 60 != 198" in str(error)
    else:
        raise AssertionError(
            "El generador ha acceptat hores incoherents"
        )


def test_generador_publica_mopt1_a_l_api(
    tmp_path: Path,
    monkeypatch,
) -> None:
    api_dir = tmp_path / "api" / "v1"
    monkeypatch.setattr(
        genera_api,
        "API_DIR",
        api_dir,
    )

    data_generacio = "2026-07-24T00:00:00+00:00"
    genera_api.netejar_api()

    cicles = []
    moduls = []
    for cicle_info in genera_api.CICLES_INFO.values():
        cicle, moduls_cicle = (
            genera_api.generar_api_cicle(
                cicle_info,
                data_generacio,
            )
        )
        cicles.append(cicle)
        moduls.extend(moduls_cicle)

    genera_api.generar_index(
        cicles,
        moduls,
        data_generacio,
    )

    index = _llegir_json(api_dir / "index.json")
    smx = _llegir_json(
        api_dir / "cicles" / "smx.json"
    )
    mopt1 = _llegir_json(
        api_dir / "moduls" / "MOPT1.json"
    )
    modul_0227 = _llegir_json(
        api_dir / "moduls" / "0227.json"
    )

    assert "MOPT1" in index["moduls"]
    assert any(
        modul["codi"] == "MOPT1"
        for modul in smx["moduls"]
    )
    assert mopt1["hores"]["total"] == 99
    assert mopt1["empresa"]["te_estada"] is False
    assert mopt1["num_ra"] == 9
    assert sum(
        len(ra["criteris_avaluacio"])
        for ra in mopt1[
            "resultats_aprenentatge"
        ].values()
    ) == 54
    assert (
        mopt1["metadata"]["tipus_curriculum"]
        == "local"
    )
    assert modul_0227["hores"] == {
        "total": 198,
        "centre": 132,
        "empresa": 66,
    }
    assert modul_0227["empresa"]["te_estada"] is True


def test_rutes_del_generador_no_depenen_del_cwd(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    assert genera_api.DATA_DIR == DATA_DIR
    assert genera_api.DATA_DIR.exists()
