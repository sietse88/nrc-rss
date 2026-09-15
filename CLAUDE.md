# NRC Feed — overdracht

Dit project begint met een overdracht uit het project **NOS Feed** (`iCloud Drive/Code/NOS Feed`). Daar is voor Sietse een RSS-feed van NOS Teletekst 101 gebouwd. Wat hieronder staat is de kennis uit dat project die hier van pas komt.

## Doel

Eén RSS-feed voor NetNewsWire die vier NRC-rubrieken samenvoegt, **zonder dubbele artikelen**. Sietse heeft de vier feeds nu los in NetNewsWire staan, en artikelen die in meerdere rubrieken staan verschijnen daardoor dubbel.

| Rubriek | Feed |
|---|---|
| Binnenland | `https://www.nrc.nl/index/binnenland/rss` |
| Buitenland | `https://www.nrc.nl/index/buitenland/rss` |
| Economie | `https://www.nrc.nl/index/economie/rss` |
| Den Haag | `https://www.nrc.nl/index/den-haag/rss` |

## Wat we al weten over de NRC-feeds (gecontroleerd in september 2026)

- Het zijn officiële RSS 2.0-feeds van NRC. Achter bijna elke overzichtspagina van nrc.nl kun je `/rss` zetten.
- Velden per artikel: `title`, `link`, `guid`, `pubDate`, `description`, `enclosure`.
- `description` is een **samenvatting** van ongeveer 300 tekens. Het hele artikel staat achter de betaalmuur op nrc.nl; Sietse heeft een abonnement.
- Het kanaal heeft een eigen logo: `https://assets.nrc.nl/static/front/img/nrc-logo.svg`.
- Aantallen per feed op 15 september 2026: Binnenland 50, Buitenland 110, Economie 56, Den Haag 24. Samen ongeveer 240, met veel overlap.
- Ontdubbelen: controleer eerst op de échte data of hetzelfde artikel in elke feed dezelfde `link` en/of `guid` heeft. Ga er niet van uit.

## Lessen uit het NOS-project

- **Ontdubbelen met een stabiel ID.** Bij NOS gaf een ID op basis van de tekst dubbele items zodra de redactie een woord wijzigde. Kies een ID dat niet verandert als de tekst licht wordt aangepast.
- **Een geheugen van gezien artikelen** (`seen.json` met `first`/`last` en 14 dagen bewaren) houdt de publicatiedatum stabiel en voorkomt dat een artikel dat even verdwijnt als nieuw terugkomt.
- **Door de robot beheerde bestanden nooit overschrijven met een lokale testversie.** Bij NOS stond `seen.json` op GitHub met 238 artikelen en lokaal met 8. Pushen van de lokale versie had de hele feed opnieuw als nieuw laten binnenkomen.
- **NetNewsWire 7.0.5 en hoger** haalt het feedlogo uit het RSS-element `<image><url>` (vierkant, minimaal 128 px). Zonder dat element toont het een grijze wereldbol.
- **Tekst controleren op echte data**, over veel artikelen, niet op één voorbeeld. Bij NOS kwamen de meeste fouten pas zo boven.

## Werkafspraken met Sietse

- Sietse is geen developer. Geef uitleg in het Nederlands, zonder jargon, en met klikstappen: waar je klikt en wat je dan op het scherm ziet.
- Bij alles wat meer is dan een kleine fix: eerst een plan en de keuzes voorleggen, en pas beginnen na een expliciet **"go"**.
- Zeg alleen dat iets werkt als je het echt hebt gecontroleerd. Zeg anders wat je wel en niet hebt gecontroleerd.

## GitHub, als het project op GitHub komt

- Account: `sietse88`. Voor NOS is er een aparte repo (`nos-teletekst-rss`) die Claude zelf mag pushen.
- Er is geen `gh` en geen `brew` op de Mac. Git 2.50 en SSH zijn er wel.
- Pushen gaat via een **deploy key per repo**. De bestaande sleutel `~/.ssh/nos_teletekst_rss` (host-alias `github-nosteletekst` in `~/.ssh/config`) werkt alleen voor de NOS-repo. Voor een nieuwe repo is een nieuwe sleutel met een eigen host-alias nodig, die Sietse bij die repo onder **Settings → Deploy keys** toevoegt met **Allow write access**.
- Commit met e-mailadres `sietse88@users.noreply.github.com`, zodat het echte adres niet in een openbare geschiedenis komt.
- Afgesproken bij NOS: Claude pusht zodra het iets aanpast waar Sietse om vroeg, en meldt daarna wat er gepusht is. Vraag voor dit project opnieuw of Sietse dat ook hier wil.
