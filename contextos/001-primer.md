# ESCRIT DE CONTEXT — Sistema centralitzat de mòduls i Resultats d’Aprenentatge (RA) amb GitHub Pages

Aquest document descriu el context, objectiu i proposta d’implementació d’un sistema web basat en GitHub Pages per gestionar de forma centralitzada els mòduls i els seus Resultats d’Aprenentatge (RA).

Aquest escrit està pensat perquè es pugui reutilitzar en una nova conversa o per qualsevol persona que vulgui entendre i continuar el projecte sense context previ.

---

## 1. PROBLEMA A RESOLDRE

En el context docent (FP: SMX, DAM i ASIX), s’ha detectat un problema recurrent:

- Falta de claredat sobre:
  - quines RA té cada mòdul
  - quines són oficials vs interpretades
- Dificultat per:
  - justificar notes davant coordinació
  - mantenir coherència entre butlletins i avaluació real
  - tenir traçabilitat (d’on surt cada nota)
- Especialment crític en:
  - avaluació basada en projectes
  - mòduls optatius sense definició clara de RA

---

## 2. OBJECTIU DEL SISTEMA

Crear una eina web (GitHub Pages) que actuï com:

> FONT ÚNICA DE VERITAT dels mòduls i les seves RA

Que permeti:

- Consultar ràpidament:
  - mòduls
  - RA associades
- Diferenciar:
  - RA oficials
  - RA interpretades
  - RA pendents
- Donar suport a:
  - presa de decisions docents
  - coherència en l’avaluació
  - justificació davant coordinació
- Servir com a base per:
  - sistemes de correcció
  - informes
  - validació de notes

---

## 3. ORIGEN DE LES DADES (CRÍTIC)

Aquest sistema **NO es basa en memòria ni interpretació directa**, sinó en documents oficials.

Estructura de fonts:

```bash
.
├── asix
│   ├── DOGC_T_administracio_sistemes_informatics_xarxa.pdf
│   ├── mp_-ICA0_administracio_sistemes_informatics_xarxa_20240425.docx
│   ├── o_ICA0_administracio_sistemes_informatics_xarxa_20240425.docx
│   └── RD_TS_sistemes_informatics.pdf
├── dam
│   ├── BOE_GS_Aplic_Multiplataforma.pdf
│   ├── DOGC_TS_desenvolupament_aplicacions_multiplataforma.pdf
│   ├── mp_ICB0_desenvolupament_aplicacions_multiplataforma_20240424.docx
│   └── o_ICB0_desenvolupament_aplicacions_multiplataforma_20240322.docx
└── smx
    ├── DOGC_T_sistemes_microinformatics_xarxes.pdf
    ├── mp_IC10_sistemes_microinformatics_xarxes_20240424.docx
    ├── o_IC10_sistemes_microinformatics_xarxes_20240424.docx
    └── T_sist_microinformatics_i_xarxes.pdf
```

La URL a on es poden trobar TOTS aquests pdf és: `https://xtec.gencat.cat/ca/curriculum/professionals/fp/titolsloe/infcomunicacions`

---

### Tipus de documents

- **DOGC / BOE / RD**
  - Fonts oficials normatives
  - Defineixen estructura del cicle i RA

- **mp_*.docx**
  - Desenvolupament curricular del mòdul
  - Definició concreta de RA

- **o_*.docx**
  - Organització / adaptació del centre

---

### Principi clau

El JSON del sistema ha de derivar d’aquests documents  
No s’han d’inventar RA  

---

## 4. ENFOCAMENT TÈCNIC

### Tecnologia

- GitHub (repositori públic)
- GitHub Pages
- HTML + CSS + JavaScript
- JSON com a font de dades

---

## 5. ESTRUCTURA DEL PROJECTE

```bash
moduls-i-ras/
│
├── index.html
├── data/
│   ├── dam.json
│   ├── smx.json
│   ├── asix.json
│   └── optatives.json
│
├── docs/
│   ├── dam/
│   ├── smx/
│   └── asix/
│
├── js/
│   └── app.js
│
└── css/
    └── styles.css
```

IMPORTANT:
Pots incloure els PDFs al repo (`docs/`) per traçabilitat


---

## 6. MODEL DE DADES

### Exemple: dam.json

```json
{
  "0373": {
    "nom": "Llenguatges de marques",
    "ra": ["RA1","RA2","RA3","RA4","RA5","RA6","RA7"],
    "estat": "oficial",
    "font": "mp_ICB0_desenvolupament_aplicacions_multiplataforma_20240424.docx"
  }
}
```

---

### Exemple: smx.json

```json
{
  "0223": {
    "nom": "Aplicacions ofimàtiques",
    "ra": ["RA1","RA2","RA3","RA4","RA5","RA6","RA7","RA8","RA9"],
    "estat": "oficial",
    "font": "mp_IC10_sistemes_microinformatics_xarxes_20240424.docx"
  }
}
```

---

### Exemple: optatives.json

```json
{
  "MOPT1": {
    "nom": "Programació Python",
    "ra": ["RA1"],
    "estat": "pendent",
    "font": "no definit oficialment"
  }
}
```

---

## 7. CAMP CLAU: "estat"

Valors:

- "oficial" → definit per normativa
- "interpretat" → criteri docent
- "pendent" → no definit

Permet defensar decisions davant coordinació

---

## 8. FUNCIONALITAT WEB

- selector: DAM / SMX / ASIX / OPTATIVES
- llista de mòduls
- visualització de:
  - RA
  - estat
  - font (document origen)

---

## 9. PRINCIPI CLAU

No és una web decorativa  
És una eina de control i traçabilitat

---

## 10. BENEFICIS

- coherència entre:
  - notes
  - RA
  - butlletins
- justificació davant coordinació
- eliminació d’errors
- base per automatització

---

## 11. EVOLUCIÓ FUTURA

- validació de CSV de notes
- integració amb scripts Python
- dashboard docent
- traçabilitat RA → activitat → evidència

---

## 12. PRINCIPIS DE DISSENY

- simplicitat
- dades separades
- versionat
- traçabilitat documental
- reutilització

---

## 13. OBJECTIU FINAL

Passar de:

- improvisació  
- dubtes sobre RA  
- incoherències  

a:

- sistema  
- control  
- justificació  
- coherència  

---

## 14. ESTAT ACTUAL

- fonts documentals disponibles ✔
- estructura definida ✔
- model de dades definit ✔
- pendent implementació

---

## 15. PROPER PAS

1. crear repositori GitHub
2. pujar documents (docs/)
3. crear JSONs a partir dels documents
4. crear web mínima
5. activar GitHub Pages

---

## FINAL

Aquest sistema no és només tècnic.

És una eina per:

- treballar amb criteri  
- justificar decisions  
- evitar errors futurs  

