# Flyt medarbejder i Nexus

Automatiserer flytning og administration af medarbejdere i KMD Nexus ved at læse opgaver fra en Excel-fil og tilføje eller fjerne medarbejdere fra organisationer og roller.

## Hvad gør robotten?

1. Leder efter en Excel-fil (`.xlsx`/`.xlsm`) i en undermappe af den angivne opgavemappe og springer over hvis en tekstfil allerede findes (indikerer igangværende eller afsluttet opgave).
2. Parser Excel-filen med faner svarende til opgavetyper: **Tilføjelse**, **Fjernelse**, **Tilføjelse rolle** og **Fjernelse rolle** — hver fane med kolonnerne `Medarbejdere` og `Organisation`/`Rolle`.
3. Opretter ét workqueue-element per medarbejder og gemmer en `Indlæst.txt`-markørfil i opgavemappen.
4. Henter medarbejderen i Nexus via initialer og udfører den angivne opgave: tilføj organisation, fjern organisation, tilføj rolle eller fjern rolle.
5. Rapporterer fejl via `odk-tools`-rapportfunktionen, hvis en operation ikke kan gennemføres (f.eks. organisation ikke fundet, rolle kan ikke tilføjes).
6. Omdøber `Indlæst.txt` til `Kørsel Gennemført.txt` og skriver en afslutningsrapport når hele kørslen er gennemført.

## Forudsætninger

- Python ≥ 3.13
- [`uv`](https://docs.astral.sh/uv/) til pakkehåndtering
- Adgang til **Automation Server** (arbejdskø)
- Adgang til **KMD Nexus** (produktion)
- Adgang til **Odense SQL Server**

## Installation

```sh
uv sync
```

## Konfiguration

Credentials registreres i Automation Server:

- `KMD Nexus - produktion`
- `Odense SQL Server`

| Miljøvariabel | Beskrivelse |
|---|---|
| `ATS_URL` | URL til Automation Server API (f.eks. `http://localhost/api`) |
| `ATS_TOKEN` | Bearer token til autentificering mod Automation Server |
| `ATS_WORKQUEUE_OVERRIDE` | Overstyring af workqueue-ID til testformål |

## Kørsel

```sh
uv run python main.py --queue   # Læs Excel-fil og fyld arbejdskøen
uv run python main.py           # Behandl arbejdskøen
```

Excel-filen placeres i en undermappe af opgavemappen og skal have faner navngivet præcis som opgavetyperne (`Tilføjelse`, `Fjernelse`, `Tilføjelse rolle`, `Fjernelse rolle`).

## Afhængigheder

| Pakke | Formål |
|---|---|
| `automation-server-client` | Kommunikation med Automation Server, workqueue-håndtering og credential-opslag |
| `kmd-nexus-client` | Klient til KMD Nexus — opslag og opdatering af brugere, organisationer og roller |
| `odk-tools` | Tracking af opgavegennemførelse og rapportering af fejl og kørselsresultater |
| `openpyxl` | Læsning af Excel-filer med medarbejderopgaver |

## GDPR og sikkerhed

Processen behandler medarbejderinitialer, som er CPR-relaterede personoplysninger. Initialer sendes til KMD Nexus som en del af opslags- og opdateringsoperationerne. Oplysningerne hentes fra den anviste Excel-fil og gemmes ikke lokalt ud over workqueue-elementerne i Automation Server. Fejlrapporter genereret via `odk-tools` kan indeholde initialer og bør behandles i overensstemmelse med gældende retningslinjer for personoplysninger.
