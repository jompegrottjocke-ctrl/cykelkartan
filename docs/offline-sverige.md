# Sverige och offlinebruk

Appens namn är fortfarande **Cykelfrämjandet Malmö**. Kart- och ruttområdet kan nu omfatta Sverige.

## Installera hela Sverige en gång

1. Starta den nya appversionen och välj **Hämta Sverige för offlinebruk** i sidopanelen (rulla ned vid behov).
2. Bekräfta den stora engångshämtningen. Appen hämtar Sveriges OSM-extrakt över HTTPS från [Geofabrik](https://download.geofabrik.de/europe/sweden.html) och kontrollerar leverantörens MD5-kontrollsumma. TLS-verifiering är påslagen.
3. Vänta medan det lokala kartindexet byggs. Förloppet visas i statusfältet och arbetet kan avbrytas. Stäng inte av datorn under installationen. En misslyckad installation ersätter inte en tidigare fungerande karta.
4. Därefter väljs offlinekartan automatiskt och återöppnas från disk nästa gång. Knappen **Sverige** visar landets översikt. Zooma in för cykelvägar och byggnader.

Räkna med minst 8 GB ledigt diskutrymme under installationen. På Windows används ett tillfälligt nodindex i minnet under bearbetningen; 16 GB RAM rekommenderas för hela Sverige. Vid vanlig användning läses kartan från disk och ruttdata begränsas till valt område. Filstorlek och tid varierar med aktuell datamängd, dator och anslutning. Kartfilen, det färdiga indexet och tillfälliga filer kan tillsammans kräva mer utrymme; appen gör även en kontroll mot nedladdningens rapporterade storlek. Originalfilen behålls för att kunna återanvändas efter en avbruten bearbetning. Den distribueras separat från programmet och ingår inte i EXE-filen eller Git-repositoriet.

## Vad fungerar utan internet?

- Kartvisning från det lokala Sverigeindexet: vägar, cykelinfrastruktur, byggnader, enkla park- och vattenytor samt kustlinjer där dessa finns som OSM-vägar.
- Val av punkter och mellanstopp på kartan samt inmatning av koordinater.
- Ruttberäkning från lokala vägar kring start, mål och mellanstopp.
- Sparade rutter, hastighetsinställning och export.

Uppskattad trafikljusväntan beräknas ännu inte i Sverigeläget och visas därför som ej beräknad. Cykeltid beräknas från ruttlängd och vald hastighet.

Adressökning använder fortfarande Nominatim och kräver internet. Klicka på kartan eller skriv koordinater med decimalpunkt, exempelvis `59.330, 18.060`, för att välja punkter offline.

Det görs inga anrop till kommunens datakälla/Overpass för rutter när Sverigeläget används. Appen läser bara vägar i en korridor kring den valda rutten. Om nätet inte är sammanhängande prövas ett bredare område. Mycket långa rutter kan överskrida gränsen för lokal grafstorlek; dela då upp resan i etapper. Hela landets täckning betyder inte att en enda rutt genom hela Sverige är prestandaverifierad.

## Kartans begränsningar

Det lokala Sverigeindexet är en egen, förenklad vektorkarta över verkliga OSM-data, inte en exakt offlinekopia av OpenStreetMaps standardkarta. Multipolygonrelationer, fullständig orts-/gatunamnsplacering, höjdkurvor och alla OSM-restriktionsrelationer hanteras ännu inte. Vissa sjöar, öar och andra ytor kan därför saknas. Datatäckning beror på OSM. Vid mycket täta kartvyer begränsas antalet ritade objekt och statusfältet uppmanar till inzoomning. Ruttgrafen använder inte denna kartvisningsgräns.

Cykelförbud, riktningar och uttryckliga cykelundantag används, men motorn ersätter inte lokal skyltning och garanterar inte att alla juridiska tillträdesvillkor är representerade.

## Andra offlinekartor

**Öppna offlinekarta** öppnar ett eget lagligt rasterpaket i MBTiles-format (PNG eller JPEG). Filen läses direkt på den plats där den ligger; flytta eller ta inte bort den medan appen använder den. MBTiles innehåller bakgrundsbilder, inte automatiskt ruttdata. Vektor-MBTiles/PBF kan inte öppnas med denna knapp; Sveriges PBF hämtas och bearbetas via Sverigeknappen.

En saknad offlinekartplatta ger ett meddelande och ersätts inte i smyg av en internetplatta. **Internetkarta** växlar uttryckligen tillbaka till den vanliga bakgrundskartan. Installerade Sverigeruttdata fortsätter användas lokalt även med internetbakgrund. Knappen **Hämta Sverige för offlinebruk** öppnar det befintliga paketet direkt om det redan är installerat; någon ny hämtning behövs inte.

## Befintliga kommunpaket

Som mindre alternativ kan **Ruttområde** ange en ort/kommun i Sverige. Hämtning sker endast med **Hämta/uppdatera valt ruttområde**, och varje område sparas separat. Vid nästa start laddas det sparade området från disk. Sverigeläget behöver inte dessa kommunpaket.

## Källa och licens

© OpenStreetMap-bidragsgivare, [ODbL](https://www.openstreetmap.org/copyright). Sverigeextrakt från Geofabrik. Attribution visas i kartan. Ingen masshämtning av publika OSM-kartplattor sker. Vid vidare distribution av databasen måste ODbL-villkoren följas.
