# Cykelfrämjandet Malmö

En planerad Windows-applikation för cykelkarta och cykelnavigation i Malmö, med modern skandinavisk formgivning och gröna accentfärger.

## Projektstatus

Repositoriet innehåller kravspecifikation och grundläggande identitetsresurser. Själva applikationen är ännu inte implementerad. Det finns inget verifierat Windows-program eller installationsprogram.

- [Fullständig kravspecifikation](docs/kravspecifikation.md)
- Gemensamt programnamn: `app/identity.py`
- Egen cykelikon: `assets/icons/cykel.svg` och `assets/icons/cykel.ico`

## Namn och paketering

Använd **Cykelfrämjandet Malmö** i titelrad, huvudfönster, startskärm, sidopanel, inställningar, Windows-genvägar, installationsprogram och dokumentation. Den färdiga programfilen ska heta **CykelframjandetMalmo.exe**. PyInstaller ska använda `CykelframjandetMalmo` som byggnamn och `assets/icons/cykel.ico` som ikon.

Ikonen är en egen geometrisk cykelsymbol och använder inte organisationens officiella logotyp. Namnet innebär inte att appen är officiellt godkänd av organisationen.

Alla funktioner och tekniska krav i kravspecifikationen kvarstår.
