# Cykelfrämjandet Malmö

En svensk skrivbordsapp med PySide6, Qt WebEngine, Leaflet och OpenStreetMap. Grön skandinavisk formgivning, Malmö som startvy och en egen cykelikon. Projektet använder inte organisationens officiella logotyp och gör inte anspråk på officiellt godkännande.

## Starta på Windows 10/11

Installera Python 3.12 (64 bit). Kör i projektmappen:

```bat
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
start_windows.bat
```

På Linux med grafiskt skrivbord:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python main.py
```

## Användning

1. Klicka **Uppdatera cykelkartan**. Första hämtningen av Malmö kommuns cykelvägnät kan ta flera minuter. Internet behövs. En misslyckad hämtning lämnar den tidigare grafen intakt.
2. Högerklicka på kartan för start, mål och mellanstopp. Alternativt sök en adress med Sök eller skriv `55.605, 13.0038`. Adressökning sker endast på uttrycklig begäran, inte som automatisk komplettering.
3. Välj ruttläge och hastighet, sedan **Beräkna cykelrutt**. Dra markörerna för att ändra punkter. Klicka på ett vägavsnitt i listan för att markera det.
4. Spara och öppna namngivna rutter. Exportera GPX/GeoJSON, ta PNG av kartvyn eller kopiera sammanfattningen.

Ruttmotorn använder riktade nätverkskanter med verklig geometri, filtrerar cykelförbud och erbjuder fem grundmodeller. Säkrare är en modellprioritering, ingen trafiksäkerhetsgaranti. Trevligaste använder än så länge vägtyp, inte avstånd till parker eller vatten. Maximera cykelbana använder en viktad kandidat och faller tillbaka till kortaste rutten om omvägsgränsen överskrids; det är ingen matematisk garanti för maximal andel. Vägbeskrivningar anger faktiska vägavsnitt och deras längder, ännu inga svängmanövrer.

## Lagring, nätverk och licenser

SQLite lagrar hastighet, tema, kartposition och sparade rutter under Qt:s lokala appdatamapp. GraphML och HTTP-cache lagras i dess `map`-mapp. Efter hämtning kan rutter beräknas utan internet. Bakgrundskartan kräver fortfarande internet; inga offlinekartplattor ingår och ingen massnedladdning görs.

- `tile.openstreetmap.org`: bakgrundskarta, © OpenStreetMap-bidragsgivare, ODbL. [Användningspolicy](https://operations.osmfoundation.org/policies/tiles/).
- `nominatim.openstreetmap.org`: uttrycklig adressökning och kommungräns via OSMnx, med dess cache och hastighetsbegränsning. [Policy](https://operations.osmfoundation.org/policies/nominatim/).
- `overpass-api.de`: OSM-vägnät via OSMnx. Använd uppdateringen sparsamt.
- Leaflet 1.9.4 ligger lokalt, licens i `app/maps/LEAFLET-LICENSE`.

Internetåtkomst till dessa tre domäner behöver tillåtas i molnmiljön för integrationstest. Kartan har attribution. Fullständighet och tillträdesregler beror på OSM-data; lokala skyltar gäller alltid.

## Testa och bygga Windows

```bat
.venv\Scripts\python -m pytest -q
build_windows.bat
```

Bygget skapar `dist\CykelframjandetMalmo\CykelframjandetMalmo.exe` med Qt WebEngine, lokal Leaflet och ikon. Behåll hela distributionsmappen. För installationsprogram med genvägar: installera Inno Setup 6 och kompilera `installer/windows.iss`. GitHub Actions-flödet **Windows** bygger och laddar upp distributionsmapp och installationsprogram som artefakt.

Windows-bygge och installation är inte verifierade från Linux-miljön. Hämta artefakten först efter ett lyckat Windows-flöde och testa den på Windows 10/11.

## Verifierad omfattning och återstående arbete

Grundversionen har körts i Qt:s headless-läge med fungerande WebChannel-brygga. Automatiska tester använder uttryckliga syntetiska graffixturer för ruttregler, alla ruttlägen, export, lagring och skydd av tidigare data vid misslyckad uppdatering. 13 automatiska tester passerar. Verklig kartdatahämtning är blockerad av molnmiljöns nätverkspolicy och har därför inte verifierats här. Qt WebEngine rapporterar dessutom att proxyns certifikat inte är betrott i dess NSS-lager i denna Linux-miljö. TLS-kontroll har inte stängts av; även detta behöver lösas innan bakgrundskartan kan integrationstestas här.

Den fullständiga [kravspecifikationen](docs/kravspecifikation.md) kvarstår. Följande ingår ännu inte: alternativrutter, fullständig cykelspecifik enkelriktningshantering, svänginstruktioner, park-/vattenanalys, parkerings- och pumplager, favoritplatser, sökhistorik, radering av rutter i UI, fullständigt inställningsfönster, satellitlager, offlinebakgrundskartor, startskärm och verifiering av Windows-skalning. Detta är en körbar grundversion, inte en färdig implementering av samtliga krav.
