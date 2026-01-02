# Fragebogen zum Programmentwurf Webengineering 2 DHBW Karlsruhe TINF23B3


## Gruppeninformationen

> Der Gruppenname hat keine weitere Bedeutung, macht mir aber eine Zuordnung bei der Korrektur einfacher.
> Es kann sein, dass der Name später noch weiterlebt, falls ich den Quellcode in die biletado-Organisation verschiebe.
>
> See: [fantasy name generators](https://www.fantasynamegenerators.com/)

Gruppenname: restful pythonists

Gruppenteilnehmer:

- Jonas Friedrich
- Tuluhan Engin

## Quellcode

> Nur ein Beispiel, ob und wie ihr auftrennen möchtet ist euch überlassen

Links zu den Versionskontrollendpunkten:

- https://github.com/jonessy05/gitpython

## Containerregistry

ghcr.io (GitHub Container Registry) + lokale Registry (Kind Cluster / localhost)

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
| Prepared statements/ORM               | SQLAlchemy 2.0.23 + Pydantic 2.5.0 (PostgreSQL-Datenbank) |
| ORM Version                           | SQLAlchemy 2.0.23, Pydantic 2.5.0                  |
| Website zum ORM                       | [SQLAlchemy](https://www.sqlalchemy.org/) / [Pydantic](https://docs.pydantic.dev/) |

## geplante Automatisierung

Art der Automatisierung: "GitHub Actions"

## geplante Testautomatisierung

Art der Testautomatisierung: "pytest mit pytest-asyncio für Unit-Tests", "pytest-cov für Coverage-Reports", "Model-Validierungstests (~10 Tests für Pydantic-Modelle, siehe `reservations-backend/tests`)"

Wie sind die Ergebnisse einzusehen?: GitHub Actions Workflow `.github/workflows/ci-cd.yml` (Job `test`).
Testergebnisse und Coverage-Ausgabe sind in den Logs des GitHub Actions Runs sichtbar. Pytest erzeugt eine `coverage.xml` in der die Ergebnisse gespeichert werden.