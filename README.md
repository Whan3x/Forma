# FORMA 2.0

Mobilní PWA pro trénink, výživu, progres a přátele. Běží na Pythonu 3.9+, SQLite a čistém JavaScriptu bez balíčků třetích stran.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Whan3x/Forma)

Tlačítko vytvoří veřejný HTTPS náhled z `render.yaml`. Bez placeného persistentního disku je bezplatná varianta vhodná jen k prohlížení a testování — data se mohou při restartu nebo novém nasazení ztratit.

## Co je nové ve 2.0

- Samostatná sekce **Plány** s rotací priorit Upper (`záda → hrudník → ramena`) a Lower (`kvadricepsy → zadní řetězec`).
- Pořadí cviků se při zahájení tréninku uloží do databáze. Aktivní trénink se už po obnovení stránky ani na jiném zařízení nepřeskupí.
- Automatická migrace databáze z FORMA 1.0; stávající účty, série, jídla a fotografie zůstávají zachované.
- Nová responzivní vrstva pro iPhone, Android a desktop: safe areas, spodní navigace, 44px dotykové cíle, systémová typografie a přístupnost pro omezení pohybu, průhlednosti a vyšší kontrast.
- Přenositelné frontend testy v Node a automatické ověřování přes GitHub Actions.

## Rychlé spuštění

```sh
python3 server.py
```

Otevři `http://127.0.0.1:8765`, vytvoř účet a zvol **Načíst Upper / Lower**. Data se ukládají do `data/forma.sqlite3`.

Na macOS lze po rozbalení spustit také `START.command`. Server ukončíš pomocí `Ctrl+C`.

## Vývoj

Nejsou potřeba `npm install`, `pip install` ani externí databáze.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
node --check public/planner.js
node --check public/app.js
node --check public/sw.js
node tests/test_planner.mjs
node tests/test_frontend_node.mjs
python3 -m py_compile server.py
```

Lokální spuštění s oddělenými testovacími daty:

```sh
FORMA_DATA=/tmp/forma-dev-data python3 server.py
curl -fsS http://127.0.0.1:8765/api/health
```

## Jak fungují plány

V části **Plány** je před startem možné zvolit aktuální prioritu. Výchozí volba navazuje na poslední trénink stejného typu. Prioritní svalová skupina jde dopředu, hlavní vícekloubové cviky před izolace a paže či doplňky později.

Při klepnutí na **Začít trénink** server uloží:

- typ plánu,
- zvolenou prioritu,
- přesné pořadí ID cviků.

Server kontroluje, že všechna ID patří přihlášenému uživateli a stejnému plánu. Cizí, duplicitní nebo neplatná ID odmítne.

## Funkce

- Tréninky, série, RPE, pauzy, historie, grafy, PR a kalkulačka kotoučů.
- Upper/Lower šablona i vlastní plány a cviky.
- Jídelní deník, makra, oblíbená jídla, recepty a Open Food Facts.
- Voda, váha, pas a soukromé fotografie progresu.
- Přátelé, dobrovolně sdílené tréninky, reakce, komentáře a výzvy.
- Export JSON, offline fronta sérií a instalovatelná PWA.
- Volitelná analýza fotografie jídla přes OpenAI API.

## Konfigurace

Proměnné jsou popsané v `.env.example`. Soubor `.env` se záměrně nenačítá automaticky; hodnoty nastav v prostředí procesu nebo hostingu.

| Proměnná | Účel | Výchozí hodnota |
|---|---|---|
| `FORMA_DATA` | adresář SQLite databáze | `./data` |
| `FORMA_HOST` | adresa serveru | `127.0.0.1` |
| `PORT` | port | `8765` |
| `FORMA_ENV` | při `production` vyžaduje HTTPS veřejnou URL | prázdná |
| `FORMA_PUBLIC_URL` | veřejná HTTPS adresa a kontrola Origin | prázdná |
| `RENDER_EXTERNAL_HOSTNAME` | automatická veřejná doména Renderu | nastavuje Render |
| `OPENAI_API_KEY` | volitelná serverová AI analýza | prázdná |
| `OPENAI_MODEL` | obrazový model | `gpt-4.1-mini` |
| `FORMA_AI_DAILY_LIMIT` | AI volání na účet za UTC den | `10` |
| `FORMA_MAX_ACCOUNTS` | maximální počet registrací; `0` = bez limitu | `0` |
| `FORMA_MAX_PHOTO_MB_PER_ACCOUNT` | limit fotografií jednoho účtu | `100` |
| `FORMA_MAX_TOTAL_PHOTO_MB` | celkový limit fotografií; `0` = bez limitu | `0` |
| `FORMA_WRITE_RATE_PER_MINUTE` | zápisové požadavky na účet za minutu | `240` |

Tajné hodnoty nikdy neukládej do GitHubu, frontendových souborů ani chatu.

## Docker a nasazení

```sh
docker build -t forma .
docker run -d --name forma \
  -p 127.0.0.1:8765:8765 \
  -e FORMA_PUBLIC_URL=https://forma.example.cz \
  -v forma-data:/data \
  forma
```

Produkce potřebuje HTTPS reverse proxy, trvalý disk `/data`, pravidelné SQLite zálohy a limit požadavků na proxy. Současná databázová vrstva je určená pro jednu instanci aplikace.

### Nejrychlejší HTTPS náhled na Renderu

1. Klepni na tlačítko **Deploy to Render** nahoře.
2. Přihlas se přes GitHub a potvrď Blueprint.
3. Po dokončení buildu otevři URL končící `.onrender.com`.

Render předá aplikaci svou doménu přes `RENDER_EXTERNAL_HOSTNAME`, takže bezpečné cookies, HSTS a kontrola Origin se zapnou automaticky. Trvalé uchování dat by vyžadovalo persistentní disk; ten záměrně není součástí bezplatné konfigurace.

Blueprint je záměrně nastaven na `plan: free`, nemá databázi, placený disk ani API klíč a automatické deploye jsou vypnuté. Bezplatný náhled proto používá dočasné úložiště: po restartu nebo uspání mohou účty i data zmizet. Při potvrzení nasazení pokračuj pouze tehdy, když Render ukazuje cenu **0 USD**; nepřidávej disk, databázi ani placený typ instance. Samotný repozitář nemůže ovládat fakturační nastavení účtu Render ani zabránit ručnímu upgradu služby.

## Zabezpečení a soukromí

- Hesla: PBKDF2-HMAC-SHA256, náhodná sůl, 310 000 iterací.
- Sessions: náhodný token, v databázi pouze hash; `HttpOnly`, `SameSite=Lax`, na HTTPS také `Secure`.
- Parametrizované SQL, kontrola vlastníka, kontrola Origin / `Sec-Fetch-Site`, limity požadavků a validace vstupů.
- Fotografie jsou dostupné pouze přihlášenému vlastníkovi; jídlo, míry a fotky postavy se do feedu neposílají.
- API odpovědi mají CSP, `nosniff`, omezená oprávnění a na HTTPS HSTS.

## Známé hranice

- Google a Apple přihlášení, ověření e-mailu a obnova hesla nejsou implementované.
- Připomínky fungují pouze v otevřené aplikaci; nejde o push notifikace.
- AI potřebuje vlastní placený API klíč a uživatel výsledek před uložením kontroluje.
- Před veřejným provozem je nutné ověření na skutečném iPhonu a Androidu, zátěžový test, monitoring a retenční pravidla záloh.
- Cloudový Chromium v této pracovní relaci nedokončil screenshot kvůli systémové DBus/zygote chybě. HTTP, API, datová migrace, syntaxe a renderovací funkce byly ověřeny automatickými testy; vizuální kontrola na zařízení tím není nahrazena.

## Přidání na plochu

- iPhone: otevři veřejnou HTTPS adresu v Safari → Sdílet → **Přidat na plochu**.
- Android: otevři ji v Chromu → nabídka ⋮ → **Nainstalovat aplikaci** / Přidat na plochu.

`localhost` z Macu není veřejná adresa telefonu. Pro instalaci mimo vývoj použij HTTPS nasazení.
