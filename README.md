# Mòduls i Resultats d'Aprenentatge de FP

>  **Web pública:** https://jpardo20.github.io/moduls-i-ras/

Portal web de consulta de mòduls professionals, Resultats d'Aprenentatge (RA) i dades curriculars dels cicles formatius d'informàtica.


## Objectiu

Centralitzar informació útil per a la planificació docent, l'avaluació per RA i la consulta ràpida de mòduls de DAM, DAW i SMX.

## Contingut

- Dades estructurades de cicles i mòduls en format JSON.
- Resultats d'Aprenentatge (RA) i ponderacions.
- Informació de DAM, DAW i SMX.
- Scripts de generació i validació de dades.
- Web estàtica publicada amb GitHub Pages.

## Estructura

- `docs/` — web estàtica de consulta.
- `docs/data/` — dades en format JSON, inclosos els mòduls locals.
- `scripts/` — scripts de creació i validació.
- `contextos/` — documents de treball i context curricular.

## Generació de l’API

L’API combina el currículum oficial de cada cicle amb els mòduls locals definits a `docs/data/moduls-locals-<cicle>.json`. Els mòduls locals han d’indicar explícitament la procedència curricular i no poden repetir el codi d’un mòdul oficial.

Quan la font curricular proporciona el desglossament, l’API publica
`hores.total`, `hores.centre` i `hores.empresa`. El generador comprova que
les hores de centre i d’empresa sumin la durada total del mòdul.

```bash
python scripts/genera_api.py
```

## Tecnologies

- HTML, CSS i JavaScript
- JSON
- Python
- GitHub Pages

## Estat del projecte

Projecte docent actiu, utilitzat com a eina de suport per a la planificació, la docència i l'avaluació basada en Resultats d'Aprenentatge (RA) en Formació Professional.

