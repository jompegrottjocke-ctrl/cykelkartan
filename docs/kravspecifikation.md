# MASTERPROMPT – CYKELFRÄMJANDET MALMÖ
## Bygg en komplett, professionell cykelkarta och cykelnavigator för Windows

Du är en erfaren senior mjukvaruarkitekt, Pythonutvecklare, GIS-specialist och UI/UX-designer.

Ditt uppdrag är att från grunden utveckla en komplett, modern, mycket vacker och fullt fungerande Windows-applikation med namnet **Cykelfrämjandet Malmö**.

Detta ska vara en riktig skrivbordsapplikation för Windows 10 och Windows 11, inte en vanlig webbplats.

Programmet ska kombinera en detaljerad cykelkarta över Malmö med avancerad cykelnavigation, ruttplanering, hastighetsberäkningar, kartlager och användarvänliga funktioner.

**Det övergripande målet är att skapa ett program som känns lika professionellt och genomarbetat som en kommersiell navigationsapplikation.**

All text i programmet ska vara på svenska.

---

# 1. TEKNISK ARKITEKTUR

Använd följande tekniker:

- Python 3.12 eller senare.
- PySide6 för Windows-applikationen.
- Qt WebEngine för att bädda in kartan.
- Leaflet för interaktiv kartvisning.
- OpenStreetMap för kart- och vägnätsdata.
- Overpass API för cykelinfrastruktur.
- OSMnx och NetworkX för vägnätsanalys och ruttberäkning.
- GeoPandas och Shapely där geografisk bearbetning behövs.
- SQLite för lokal datalagring.
- PyInstaller för att skapa en körbar Windows .exe-fil.

Använd en modulär, underhållbar arkitektur med tydlig separation mellan gränssnitt, kartdata, ruttberäkning och datalagring.

Välj stabila biblioteksversioner som fungerar tillsammans.

Låt inte nätverksanrop eller tunga beräkningar blockera programmets gränssnitt.

---

# 2. DESIGN – MYCKET VIKTIGT

Jag vill att programmet ska vara exceptionellt snyggt.

Designen ska inspireras av:

- Apple Maps.
- Moderna navigationsappar.
- Skandinavisk minimalism.
- Professionella premiumapplikationer för Windows.

Programmet ska kännas elegant, exklusivt, snabbt och modernt.

Undvik gammaldags standardutseende från Python och Qt.

## Färgpalett – ljust tema

- Bakgrund: #F6F8F7
- Sidopaneler: #FFFFFF
- Primärgrön: #16856A
- Mörkgrön: #105C4A
- Huvudtext: #182724
- Sekundär text: #73817C
- Kantlinjer: #E3EAE6
- Markerad rutt: #16856A

## Färgpalett – mörkt tema

- Bakgrund: #111B19
- Paneler: #1B2925
- Accentgrön: #45C69B
- Huvudtext: #F3F7F5
- Sekundär text: #A6B8B0

## Designprinciper

- Rundade hörn.
- Mjuka, diskreta skuggor.
- Modern typografi, gärna Segoe UI Variable.
- Snygga vektorikoner.
- Harmoniska avstånd mellan element.
- Mjuka animationer.
- Tydliga visuella hierarkier.
- Välbalanserade färger.
- Professionella knappar och inmatningsfält.
- Snygga hover-effekter.
- Responsiv layout.
- Stöd för högupplösta skärmar.
- Stöd för Windows-skalning 100–200 %.

Skapa återanvändbara UI-komponenter och ett konsekvent designsystem.

---

# 3. HUVUDFÖNSTRETS LAYOUT

Programmet ska bestå av tre huvudsakliga delar.

## Vänsterpanel

En elegant sidopanel med ungefär 350–400 pixlars bredd.

Panelen ska innehålla:

1. Programmets logotyp och namn.
2. Sökfält för startpunkt.
3. Sökfält för destination.
4. Knapp för att byta start och destination.
5. Val av ruttalternativ.
6. Inställning för cykelhastighet.
7. Stor grön knapp med texten "Beräkna cykelrutt".
8. Resultatkort med avstånd och restid.
9. Lista med vägbeskrivningar.
10. Favoriter och sparade rutter.

Panelen ska kunna fällas ihop så att kartan får mer plats.

## Huvudkarta

Kartan ska uppta största delen av programfönstret.

Den ska ha:

- Flytande zoomkontroller.
- Lagerknapp.
- Helskärmsknapp.
- Knapp för att centrera kartan.
- Snygga markörer.
- Färgkodade cykelvägar.
- Tydlig markerad rutt.
- Informationsrutor.

## Statusfält

Visa:

- Aktuell kartstatus.
- Senaste datauppdatering.
- Internetanslutning eller offlineläge.
- Muspekarens koordinater vid behov.

---

# 4. CYKELKARTA ÖVER MALMÖ

När programmet startar ska Malmö automatiskt visas.

Använd Malmö kommun som geografiskt huvudområde.

Visa alla tillgängliga och kartlagda cykelvägar från OpenStreetMap.

Inkludera:

- Separata cykelbanor.
- Dubbelriktade cykelbanor.
- Enkelriktade cykelbanor.
- Cykelfält på vägar.
- Gemensamma gång- och cykelvägar.
- Cykelgator.
- Cykelöverfarter och passager där data finns.
- Cykelbara lokalgator.
- Cykelparkeringar.
- Cykelpumpar.
- Andra relevanta cykelanläggningar.

Visa också vanliga vägar, parker, byggnader, vatten och geografiska detaljer som bakgrund.

## Färgkodning

- Grönt: Separata cykelbanor.
- Blått: Gemensamma gång- och cykelvägar.
- Orange: Cykelfält.
- Lila: Cykelgator.
- Grått: Övriga cykelbara vägar.

Skapa en snygg teckenförklaring.

Klassificeringen ska bygga på riktiga OSM-taggar, inte antaganden.

Hantera bland annat highway=cycleway, cycleway:lane, cycleway:track, bicycle=designated och relevanta kombinationer.

Skilj på separata cykelvägar, cykelfält och cykeltillåtna bilvägar.

Undvik att rita samma fysiska cykelbana dubbelt.

Visa tydligt när datatäckningen är ofullständig.

---

# 5. STARTPUNKT OCH DESTINATION

Användaren ska kunna välja startpunkt och destination på flera sätt.

## Alternativ A – klicka på kartan

Högerklicka på kartan och visa:

- Ange som startpunkt.
- Ange som destination.
- Lägg till mellanstopp.
- Visa koordinater.

## Alternativ B – söka adress

Skapa två sökfält:

**Från:** Ange startpunkt.

**Till:** Ange destination.

Sökningen ska stödja:

- Gatuadresser.
- Gatunamn.
- Torg.
- Parker.
- Kända platser.
- Platser inom Malmö.

Använd en lämplig geokodningstjänst med korrekt hantering av dess användningsvillkor och begränsningar.

Visa sökförslag när tjänsten stöder detta.

## Kartmarkörer

- Startpunkt: Grön markör.
- Destination: Röd markör.
- Mellanstopp: Blå markörer.

Markörerna ska kunna flyttas med musen.

När markörerna flyttas ska rutten kunna räknas om.

Skapa en knapp för att byta startpunkt och destination.

---

# 6. AVANCERAD CYKELRUTTPLANERING

Programmet ska beräkna verkliga cykelrutter på ett sammanhängande vägnät.

Använd OSMnx och NetworkX eller motsvarande robust teknik.

Rutter får aldrig bara bestå av raka linjer mellan punkter.

Ta hänsyn till:

- Cykeltillåtna vägar.
- Enkelriktningar.
- Cykelspecifika undantag från enkelriktning.
- Cykelförbud.
- Separata cykelbanor.
- Gång- och cykelvägar.
- Korsningar.
- Broar och tunnlar.
- Vägnätets verkliga anslutningar.
- Relevanta tillträdesregler.

## Ruttalternativ

Skapa följande fem lägen:

### 1. Snabbaste rutten

Beräkna den rutt som har kortast uppskattad restid.

### 2. Kortaste rutten

Beräkna kortast möjliga cykelbara sträcka.

### 3. Säkrare rutten

Prioritera separerade cykelbanor, lugna gator och cykelinfrastruktur.

Undvik större bilvägar när bättre alternativ finns.

Visa detta som en modellbaserad prioritering, inte som en garanti för faktisk trafiksäkerhet.

### 4. Trevligaste rutten

Prioritera:

- Parker.
- Grönområden.
- Lugna gator.
- Vattennära cykelvägar.
- Separata cykelbanor.

Använd bara kriterier som stöds av tillgängliga geografiska data.

### 5. Maximera cykelbana

Skapa ett särskilt ruttläge som prioriterar så hög andel separat cykelinfrastruktur som möjligt.

Tillåt en rimlig omväg jämfört med kortaste rutten.

Låt användaren välja hur stor omväg som accepteras, exempelvis 10 %, 20 % eller 30 %.

Detta är en viktig funktion i programmet.

## Alternativa rutter

Visa om möjligt flera ruttförslag.

Markera vald rutt tydligt och visa alternativen med tunnare linjer.

---

# 7. INSTÄLLBAR CYKELHASTIGHET

Användaren ska själv kunna bestämma hur snabbt han eller hon cyklar.

Skapa följande förinställningar:

- 10 km/h – Lugn cykling.
- 15 km/h – Normal cykling.
- 20 km/h – Snabb cykling.
- 25 km/h – Mycket snabb cykling.

Lägg dessutom till ett reglage för anpassad hastighet mellan 5 och 40 km/h.

Standardvärdet ska vara 15 km/h.

## Restidsberäkning

Beräkna:

Restid i minuter = (sträcka i kilometer / hastighet i km/h) × 60.

Exempel:

En sträcka på 10 km vid 20 km/h ger 30 minuters cykeltid.

När hastigheten ändras ska restiden uppdateras direkt.

Om ruttläget är "Snabbaste rutten" och hastighetsändringen påverkar vilken rutt som är snabbast ska ruttberäkningen uppdateras vid behov.

## Trafikljus och korsningar

Erbjud möjlighet att lägga till uppskattad väntetid.

Skilj mellan:

- Ren cykeltid.
- Uppskattad väntetid.
- Total uppskattad restid.

Visa tydligt att väntetiden är en uppskattning.

Spara vald hastighet mellan programstarter.

---

# 8. RUTTRESULTAT

När en rutt beräknats ska användaren få ett snyggt informationskort.

Visa:

- Total sträcka i kilometer.
- Beräknad cykeltid.
- Genomsnittlig cykelhastighet.
- Uppskattad väntetid.
- Total restid.
- Andel separat cykelbana.
- Andel cykelfält.
- Andel övriga vägar.
- Antal mellanstopp.

Visa gärna en elegant grafisk fördelningsindikator för olika vägtyper.

Exempel:

**Din cykelrutt**

Sträcka: 8,4 km

Cykeltid: 25 min

Hastighet: 20 km/h

Separat cykelbana: 76 %

Beräknad väntetid: 3 min

Total restid: 28 min

Detta är endast exempelvärden. Verkliga resultat måste beräknas från aktuell rutt.

---

# 9. VÄGBESKRIVNINGAR

Skapa vägbeskrivningar steg för steg.

Exempel:

- Starta på Stortorget.
- Fortsätt längs cykelvägen.
- Sväng höger vid nästa korsning.
- Fortsätt 650 meter.
- Sväng vänster.
- Du har nått din destination.

Använd faktiska vägdata och beräknad ruttgeometri för instruktionerna.

Visa avstånd mellan varje manöver.

När användaren klickar på en instruktion ska motsvarande del av rutten markeras på kartan.

Generera inte påhittade gatunamn eller svänginstruktioner.

---

# 10. KARTLAGER

Skapa en elegant lagerkontroll där användaren kan visa och dölja:

- Separata cykelbanor.
- Cykelfält.
- Gemensamma gång- och cykelvägar.
- Cykelgator.
- Cykelparkeringar.
- Cykelpumpar.
- Parker och grönområden.
- Aktuell cykelrutt.

Lägg till möjlighet att växla mellan:

- Ljus standardkarta.
- Mörk karta.
- Satellitkarta, om en lämplig tillåten tjänst finns.
- Cykelkarta med extra tydlig cykelinfrastruktur.

Använd kartleverantörer med lämpliga licenser och visa nödvändig attribution.

---

# 11. SPARADE RUTTER OCH FAVORITER

Användaren ska kunna:

- Spara cykelrutter.
- Namnge sparade rutter.
- Öppna tidigare rutter.
- Ta bort sparade rutter.
- Spara favoritplatser.
- Se senaste sökningar.

Använd SQLite för lokal lagring.

Spara även:

- Vald cykelhastighet.
- Tema.
- Kartlager.
- Senaste kartposition.
- Senaste zoomnivå.

---

# 12. EXPORT

Implementera följande funktioner:

## GPX

Exportera en beräknad cykelrutt till en GPX-fil.

## GeoJSON

Exportera ruttgeometri och relevant metadata.

## PNG

Exportera den aktuella kartvyn som en bild.

## Ruttinformation

Gör det möjligt att kopiera en sammanfattning med avstånd, restid och start- och slutpunkt.

---

# 13. OFFLINEFUNKTIONER

Programmet ska kunna använda lokalt sparade cykelvägar och vägnätsdata utan internet.

Implementera:

- Lokal cache.
- Lagring av cykelvägnät.
- Lagring av tidigare beräknade rutter.
- Möjlighet att använda lokala kartplattor från en laglig offlinekälla.
- Tydlig indikator för offlineläge.

Viktigt: Offlinekarta och offline-ruttberäkning är separata funktioner. Säkerställ att båda fungerar med lokalt tillgängliga data.

Ladda inte ned stora mängder kartplattor från publika servrar som förbjuder massnedladdning.

---

# 14. DATAUPPDATERING

Skapa en knapp:

**Uppdatera cykelkartan**

När användaren klickar ska programmet:

1. Kontrollera nätverksanslutningen.
2. Hämta uppdaterade cykeldata.
3. Validera datamängden.
4. Uppdatera lokal lagring.
5. Bygga om nödvändiga geografiska index och ruttgrafer.
6. Uppdatera kartan.
7. Visa när uppdateringen slutförts.

Behåll fungerande tidigare data om en uppdatering misslyckas.

Visa datum och tid för senaste lyckade uppdatering.

Hantera Overpass API:s belastningsbegränsningar och använd rimliga cacheintervall.

---

# 15. PRESTANDA

Programmet ska fungera snabbt och stabilt även med många cykelvägar.

Implementera:

- Bakgrundstrådar eller separata arbetare för tunga operationer.
- Asynkron datahämtning där det passar.
- Effektiv geografisk filtrering.
- Rumsliga index.
- Cache.
- Laddningsindikatorer.
- Progressindikatorer vid större datauppdateringar.
- Felhantering.
- Loggning.

Optimera kartvisningen så att stora mängder cykelvägar inte gör programmet långsamt.

---

# 16. PROGRAMIKON OCH IDENTITET

Skapa en professionell visuell identitet för Cykelfrämjandet Malmö.

Programmet ska ha:

- En snygg cykelrelaterad logotyp.
- En modern Windows-programikon.
- Konsekvent grön färgprofil.
- Ett elegant startfönster.
- Ett professionellt programnamn i titelraden.

Använd gärna en minimalistisk cykelsymbol kombinerad med en kartmarkör.

Skapa en riktig ikonfil i ICO-format.

---

# 17. INSTÄLLNINGAR

Skapa ett inställningsfönster med följande kategorier:

## Utseende
- Ljust tema.
- Mörkt tema.
- Följ Windows-tema.

## Cykling
- Standardhastighet.
- Standardruttyp.
- Maximal accepterad omväg.
- Uppskattad väntetid.

## Karta
- Standardkartlager.
- Visa cykelparkeringar.
- Visa cykelpumpar.
- Visa teckenförklaring.

## Data
- Uppdatera kartdata.
- Visa cacheinformation.
- Rensa cache.
- Visa senaste uppdatering.

---

# 18. PROJEKTSTRUKTUR

Skapa en tydlig projektstruktur, exempelvis:

cykelframjandet-malmo/

- main.py
- requirements.txt
- README.md
- build_windows.bat
- assets/
- assets/icons/
- assets/styles/
- app/
- app/ui/
- app/maps/
- app/routing/
- app/data/
- app/services/
- app/models/
- app/utils/
- tests/

Anpassa strukturen vid behov, men håll koden ren och lätt att vidareutveckla.

Undvik en enda enorm Python-fil.

---

# 19. WINDOWS-INSTALLATION

Programmet ska fungera på Windows 10 och Windows 11.

Skapa:

- requirements.txt med kompatibla beroenden.
- Ett startskript.
- Ett byggskript för PyInstaller.
- En fristående Windows .exe eller distributionsmapp.
- Tydliga installationsanvisningar på svenska.

Säkerställ att Qt WebEngine, Leaflet-resurser och andra nödvändiga filer följer med vid paketeringen.

Om en riktig Windows-build inte kan testas i den aktuella utvecklingsmiljön ska detta tydligt anges. Påstå inte att .exe-filen är verifierad utan att den faktiskt har testats.

---

# 20. TESTNING OCH KVALITET

Skapa automatiska tester för:

- Klassificering av cykelvägar.
- Ruttberäkning.
- Enkelriktade vägar.
- Cykelförbud.
- Hastighetsberäkning.
- Startpunkt och destination.
- Sparade inställningar.
- Datauppdatering.
- Felhantering.
- Export till GPX och GeoJSON.

Testa även manuellt där miljön tillåter:

- Kartans zoomning.
- Kartans panorering.
- Sökfunktioner.
- Flyttbara markörer.
- Växling mellan teman.
- Fönsterstorlekar.
- Windows-skalning.

Använd riktiga data för integrationstester när nätverk finns, och tydligt märkta testfixturer för automatiserade enhetstester.

---

# 21. ARBETSPLAN – BYGG PROGRAMMET PÅ RIKTIGT

Arbeta i följande ordning.

## Fas 1 – Grundprogram

Skapa ett fungerande PySide6-program med huvudfönster, sidopanel, tema och interaktiv karta centrerad på Malmö.

## Fas 2 – Cykelvägar

Implementera hämtning, lagring, klassificering och visualisering av cykelinfrastruktur från OpenStreetMap.

## Fas 3 – Start och destination

Implementera adressökning, kartklick, markörer och mellanstopp.

## Fas 4 – Ruttmotor

Bygg ett korrekt riktat cykelvägnät och implementera fungerande ruttberäkning.

## Fas 5 – Ruttalternativ

Implementera kortaste, snabbaste, säkrare, trevligaste och maximera cykelbana.

## Fas 6 – Hastighet och restid

Implementera hastighetsreglage, väntetid och dynamiska restidsberäkningar.

## Fas 7 – Design och användarupplevelse

Färdigställ premiumdesignen, animationer, ikoner, paneler och kartkontroller.

## Fas 8 – Extrafunktioner

Implementera favoriter, sparade rutter, kartlager, export och offlinefunktioner.

## Fas 9 – Testning och paketering

Kör tester, åtgärda problem, dokumentera projektet och skapa byggskript för Windows.

---

# 22. VIKTIGA INSTRUKTIONER

Följ dessa krav under hela utvecklingen:

1. Skriv riktig, fungerande och underhållbar kod.
2. Skapa alla nödvändiga projektfiler.
3. Använd riktiga OpenStreetMap-data i applikationen.
4. Hitta aldrig på kartdata eller cykelrutter.
5. Använd inte mockup-bilder som ersättning för fungerande gränssnitt.
6. Säkerställ att knapparna faktiskt gör det de ska.
7. Bygg och verifiera en fungerande grundversion innan du lägger till avancerade funktioner.
8. Hantera fel och saknade data på ett användarvänligt sätt.
9. Prioritera tillförlitlig ruttberäkning och vacker design.
10. Allt användarsynligt innehåll ska vara på svenska.
11. Respektera externa API:ers användningsvillkor och datalicenser.
12. Rapportera ärligt vad som fungerar, vad som har testats och vad som återstår.

Om du upptäcker tekniska problem ska du försöka lösa dem och fortsätta utvecklingen.

Undvik onödiga frågor. Fatta rimliga tekniska beslut själv och dokumentera dem.

Skapa inte enbart en projektplan. Implementera programmet.

# SLUTMÅL

Jag vill ha ett komplett Windows-program som heter **Cykelfrämjandet Malmö**.

När jag öppnar programmet ska jag mötas av en vacker och detaljerad cykelkarta över Malmö.

Jag ska kunna välja startpunkt och destination, få flera cykelrutter, prioritera separata cykelbanor, ställa in min cykelhastighet, se restider och spara mina favoritsträckor.

Programmet ska vara snabbt, stabilt, lättanvänt och visuellt imponerande.

**Börja nu med att skapa projektfilerna och implementera fas 1. Fortsätt sedan fas för fas och verifiera varje del innan du går vidare.**

# Fastställd namn- och identitetsstandard

Appens officiella namn är **Cykelfrämjandet Malmö**. Använd det i titelrad, huvudfönster, startskärm, sidopanel, inställningar, Windows-genvägar, installationsprogram och dokumentation. Windows-programfilen ska heta **CykelframjandetMalmo.exe**.

Skapa en egen stilren cykelikon. Cykelfrämjandets officiella logotyp får inte användas utan tillstånd. Behåll samtliga funktioner, designkrav och tekniska specifikationer ovan.
