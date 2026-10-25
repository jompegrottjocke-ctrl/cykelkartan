# Verifiering av Sverigeläget

Verifierat i Linux-molnmiljön den 25 oktober 2026:

- Geofabriks riktiga Sverigefil hämtades över HTTPS: cirka 896 MiB. Leverantörens MD5-kontrollsumma matchade.
- Hela extraktet bearbetades till ett lokalt SQLite-index med 6 978 182 kartobjekt, cirka 4 GiB. Tillfälligt nodindex togs bort efter färdig bearbetning. Den stora bearbetningen tog omkring 18 minuter i denna miljö; tiden varierar mellan datorer.
- Lokala cykelrutter och kartobjekt kontrollerades med externa HTTP-anrop uttryckligen blockerade i testet:

| Plats | Ruttlängd | Rutt- och kartkontroll |
| --- | ---: | ---: |
| Malmö | 1 957 m | cirka 3,1 s |
| Stockholm | 2 283 m | cirka 2,8 s |
| Umeå | 1 642 m | cirka 0,9 s |

Tiderna är observationer för dessa korta provrutter i denna miljö, inga garantier för användarens dator eller långa rutter.

Den körande Qt-appen visade riktig lokal Malmödata och beräknade en rutt på 1 957 meter. En Qt WebEngine-interceptor registrerade **noll externa HTTP-anrop** under offlinekontrollen. Den lokala kartan innehöll över 6 000 ritade kartobjekt i denna vy. Hela Sveriges vägöversikt kontrollerades också utan trunkering; den generaliserade GeoJSON-responsen var cirka 260 kB och genererades på cirka 1,6 sekunder.

Automatiska tester täcker bland annat OSM-import, lokal raster-MBTiles-leverans, cykelundantag och förbud, ruttlägen, export, SQLite-lagring, kontrollsummefel och avbruten import. Testfixturerna är syntetiska och skiljs från de verkliga integrationstesterna ovan.

Windows CI har byggt distributionsmappen och installationsprogrammet samt startat den färdiga EXE-filen och testat WebChannel, paketerade kartresurser, OSM-import och en lokal provrutt. Detta ersätter inte ett manuellt test av hela Sverigebearbetningen, GPU-rendering eller olika skärmskalningar på användarens Windows-dator. Se repositoryts senaste lyckade Windows-körning för aktuell nedladdningsbar artefakt.

Kartfilen och databasen ligger utanför Git-repositoriet och följer inte med i EXE-filen. [Omfattning och begränsningar](offline-sverige.md) gäller fortfarande.
