---
context:
  id: sistema_ra_fp
  versio: v2
  data: 2026-03-20
  estat: en_desenvolupament
  autor: jpardo20
  descripcio: Sistema centralitzat de mòduls i Resultats d’Aprenentatge (RA) amb traçabilitat documental oficial
  tags:
    - fp
    - ra
    - xtec
    - traçabilitat
    - avaluacio
    - github-pages
---

# ESCRIT DE CONTEXT — Sistema centralitzat de mòduls i Resultats d’Aprenentatge (RA)

Aquest document defineix el **context funcional, tècnic i normatiu** d’un sistema per gestionar de forma centralitzada els mòduls i els seus Resultats d’Aprenentatge (RA).

 Aquest document és un **contracte de sistema**.
No és només descriptiu: estableix com han de funcionar les dades i el projecte.

---

## 1. PROBLEMA A RESOLDRE

En el context docent de FP (SMX, DAM i ASIX), existeixen problemes estructurals:

- Falta de claredat sobre:
  - quines RA té cada mòdul
  - quines són oficials vs interpretades
  - quin és el document origen real de cada dada

- Dificultat per:
  - justificar notes davant coordinació
  - mantenir coherència entre butlletins i avaluació real
  - garantir traçabilitat (RA  activitat  evidència  nota)

- Situacions crítiques:
  - avaluació basada en projectes
  - mòduls optatius sense definició clara
  - discrepàncies en el nombre o descripció de RA

---

## 2. OBJECTIU DEL SISTEMA

Construir una eina (GitHub Pages  JSON) que actuï com:

  FONT ÚNICA DE VERITAT dels mòduls i les seves RA

El sistema ha de permetre:

- Consultar:
  - cicles (SMX, DAM, ASIX)
  - mòduls
  - RA associades

- Diferenciar:
  - RA oficials
  - RA interpretades
  - RA pendents

- Donar suport a:
  - decisions docents
  - coherència d’avaluació
  - justificació davant coordinació

- Servir de base per:
  - sistemes automàtics de correcció
  - validació de notes
  - informes
  - traçabilitat completa

---

## 3. PRINCIPIS CLAU (MODE BLINDAT)

- No inventar RA
- No deduir sense font
- Cada dada ha de tenir origen documental
- Cada document ha de tenir enllaç oficial si existeix
- Separació clara entre:
  - dades oficials
  - interpretacions docents

---

## 4. ORIGEN DE LES DADES (OBLIGATORI)

Les dades provenen exclusivament de:

- DOGC / BOE / RD  normativa oficial
- mp_*.docx  font principal de RA
- o_*.docx  orientacions

Estructura base:

```bash
asix/
dam/
smx/
```

---

## 5. ENLLAÇOS OFICIALS (REQUISIT CRÍTIC)

Cada document ha de tenir:

```json
{
  "official_url": "...",
  "verified": true  false
}
```

Regles:

- Si existeix URL XTEC  obligatori usar-la
- Si no està verificat  verified: false
- No marcar com oficial sense verificació

Base:
**`https://xtec.gencat.cat/ca/curriculum/professionals/fp/titolsloe/infcomunicacions`**

---

## 6. MODEL DE DADES (CONTRACTE OBLIGATORI)

## 6.1 Mòdul

Cada mòdul HA de tenir:

- id (codi mòdul)
- nom
- estat
- family
- sources (mínim 1 amb typemp)
- ra (mínim 1)

## 6.2 Sources

Cada source HA de tenir:

- type (mp, o, dogc, boe)
- filename
- official_url
- verified

## 6.3 RA

Cada RA HA de tenir:

- code
- short_description
- long_description

---

## 7. ESTAT DEL MÒDUL

Valors possibles:

- oficial
- interpretat
- pendent

Aquest camp és obligatori per traçabilitat.

---

## 8. ESTRUCTURA DEL PROJECTE

```bash
moduls-i-ras/

 index.html
 data/
    dam.json
    smx.json
    asix.json
    optatives.json

 docs/ (opcional)
 js/
 css/
```

---

## 9. INTEGRACIÓ AMB SISTEMES

Aquest sistema està dissenyat per alimentar:

- scripts Python
- motors de correcció
- validadors de notes
- dashboards docents

Els JSON han de ser compatibles amb JSON Schema.

---

## 10. FUNCIONALITAT WEB

- selector de cicle
- llista de mòduls
- vista detallada:
  - estat
  - sources
  - official_url
  - RA

---

## 11. NIVELL DE FIABILITAT

- verified: true  validat amb font oficial
- verified: false  pendent

 Cap dada crítica pot considerar-se definitiva sense verificació.

---

## 12. BENEFICIS

- coherència docent
- justificació davant coordinació
- eliminació d’errors
- base per automatització

---

## 13. EVOLUCIÓ FUTURA

- validació de CSV de notes
- integració amb motors Python
- dashboard docent
- extractor automàtic de RA

---

## 14. OBJECTIU FINAL

Passar de:

 caos, memòria i incoherència
a:

 sistema
 control
 traçabilitat
 justificació

---

## 15. ESTAT ACTUAL

- model definit
- fonts identificades
- sistema dissenyat
- pendent implementació

---

## 16. PROPER PAS

1. crear repo
2. crear JSON base
3. extreure RA reals
4. validar amb schema
5. crear web mínima
6. desplegar

---

## FINAL

Aquest sistema no és només tècnic.

És una infraestructura per treballar amb rigor, coherència i base documental real en FP.
