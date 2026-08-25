from scripts import creator


def test_extreu_el_desglossament_d_hores_i_l_estada() -> None:
    paragraphs = [
        {
            "index": 1,
            "style": None,
            "text": "Descripció dels mòduls professionals",
            "has_numbering": False,
        },
        {
            "index": 2,
            "style": "Ttol2MP",
            "text": "0227. Serveis de xarxa",
            "has_numbering": False,
        },
        {
            "index": 3,
            "style": None,
            "text": "Durada: 198 hores",
            "has_numbering": False,
        },
        {
            "index": 4,
            "style": None,
            "text": (
                "Hores a realitzar en el centre educatiu: "
                "132 hores"
            ),
            "has_numbering": False,
        },
        {
            "index": 5,
            "style": None,
            "text": "Hores d’estada a l’empresa: 66 hores",
            "has_numbering": False,
        },
    ]

    modules = creator.parse_modules(
        paragraphs,
        "curriculum.docx",
        "IC10",
    )

    assert len(modules) == 1
    assert modules[0]["hours"] == 198
    assert modules[0]["school_hours"] == 132
    assert modules[0]["company"] == {
        "enabled": True,
        "hours": 66,
    }
