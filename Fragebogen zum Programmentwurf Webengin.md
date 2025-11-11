# Fragebogen zum Programmentwurf Webengineering 2 DHBW Karlsruhe TINF23B3


## Gruppeninformationen

> Der Gruppenname hat keine weitere Bedeutung, macht mir aber eine Zuordnung bei der Korrektur einfacher.
> Es kann sein, dass der Name später noch weiterlebt, falls ich den Quellcode in die biletado-Organisation verschiebe.
>
> See: [fantasy name generators](https://www.fantasynamegenerators.com/)

Gruppenname: Covfefe

Gruppenteilnehmer:

- Jonas Friedrich
- Random 123

## Quellcode

> Nur ein Beispiel, ob und wie ihr auftrennen möchtet ist euch überlassen

Links zu den Versionskontrollendpunkten:

- git@github.com:jonessy05/gitpython.git

## Containerregistry

z.B. "Verwenden die registry des gitlab-repositories", "ghcr.io" oder  BRAUCHE ICH GLAUBE ICH NICHT

## Lizenz

> See: https://spdx.org/licenses/  
> Wir verwenden die MIT-Lizenz (freizügig).

SPDX-License-Identifier: MIT

Empfohlene Dateien / Einträge:

- Repository-Root
    - MIT: LICENSE
- kustomization
    - MIT: kustomization/LICENSE




## Sprache und Framework

| Frage                                 | Antwort                                            |
|---------------------------------------|----------------------------------------------------|
| Programmiersprache                    | python                                                 |
| Sprachversion                         | 3.12                                                 |
| Framework (FW)                        | FastAPI                         |
| FW-Version                            | v 0.121.1                                             |
| Website zum FW                        | [FastAPI](https://fastapi.tiangolo.com/release-notes/)                 |
| Prepared statements/ORM               | "Pydantic", "Datenvalidierung", "In-Memory DB"     |
| ORM Version                           | 2.5.0                                              |
| Website zum ORM                       | [Pydantic](https://docs.pydantic.dev/)             |

## geplante Automatisierung

Art der Automatisierung: "GitHub Actions"

## geplante Testautomatisierung

Art der Testautomatisierung: "pytest mit pytest-asyncio", "pytest-cov für Coverage", "pylint für Code-Qualität", "black für Code-Formatting"

Wie sind die Ergebnisse einzusehen?: pytest.ini Konfiguration, Coverage-Reports über pytest-cov, Linting durch pylint    