# Fragebogen zum Programmentwurf Webengineering 2 DHBW Karlsruhe TINF23B3


## Gruppeninformationen

> Der Gruppenname hat keine weitere Bedeutung, macht mir aber eine Zuordnung bei der Korrektur einfacher.
> Es kann sein, dass der Name später noch weiterlebt, falls ich den Quellcode in die biletado-Organisation verschiebe.
>
> See: [fantasy name generators](https://www.fantasynamegenerators.com/)

Gruppenname: Restful Pythonists

Gruppenteilnehmer:

- Jonas Friedrich

## Quellcode

> Nur ein Beispiel, ob und wie ihr auftrennen möchtet ist euch überlassen

Links zu den Versionskontrollendpunkten:

- git@github.com:jonessy05/gitpython.git

## Containerregistry

Lokale Registry (Kind Cluster) / localhost

## Lizenz

> See: https://spdx.org/licenses/  
> Wir verwenden die MIT-Lizenz (freizügig).

SPDX-License-Identifier: MIT

Empfohlene Dateien / Einträge:

- Repository-Root
    - MIT: LICENSE




## Sprache und Framework

| Frage                                 | Antwort                                            |
|---------------------------------------|----------------------------------------------------|
| Programmiersprache                    | Python                                                 |
| Sprachversion                         | 3.12                                                 |
| Framework (FW)                        | FastAPI                         |
| FW-Version                            | 0.121.1                                             |
| Website zum FW                        | [FastAPI](https://fastapi.tiangolo.com/)                 |
| Prepared statements/ORM               | In-Memory (Python Dictionary) / Pydantic (Validation) |
| ORM Version                           | 2.5.0                                              |
| Website zum ORM                       | [Pydantic](https://docs.pydantic.dev/)             |

## geplante Automatisierung

Art der Automatisierung: "GitHub Actions"

## geplante Testautomatisierung

Art der Testautomatisierung: "pytest mit pytest-asyncio für Unit-Tests", "pytest-cov für Coverage-Reports", "Model-Validierungstests (20 Tests für Pydantic-Modelle)"

Wie sind die Ergebnisse einzusehen?: GitHub Actions Workflow "Tests" (`.github/workflows/tests.yml`), Coverage-Reports als Artefakte, Testergebnisse im GitHub Actions Tab