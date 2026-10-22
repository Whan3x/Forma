# FORMA 1.0 — funkční základ, připravený k nasazení

Mobilní web pro trénink, výživu a kamarády. Tmavý vzhled se zeleným akcentem, samostatná PWA, Python 3.9+ a SQLite. Pro lokální spuštění nejsou potřeba balíčky třetích stran.

## Stav dodávky

Veřejné nasazení nebylo provedeno: vytvoření hostovaného webu zablokovala politika schvalování prostředí. Předání obsahuje spustitelnou aplikaci, zdrojové soubory a konfiguraci pro Docker. Není to hotová veřejná služba a není ověřená pro velký provoz.

## Spuštění na Macu

1. Rozbal balíček a otevři složku `forma`.
2. Spusť `START.command`. Pokud jej systém neotevře, otevři Terminál v této složce a použij `python3 server.py`.
3. Otevři **http://127.0.0.1:8765**.
4. Zvol Vytvořit účet. E-mail můžeš používat k přihlášení, heslo musí mít alespoň 10 znaků.
5. Klepni na **Načíst Upper / Lower**. Zkontroluj výchozí váhy, opakování a varianty cviků. Nejde o doporučené tréninkové váhy pro ostatní lidi.
6. Při běhu nech okno serveru otevřené; ukončíš jej Ctrl+C.

Python musí být už nainstalovaný (ověření `python3 --version`). Jedna instance serveru uchovává více oddělených účtů. Všechny záznamy a fotky jsou v `data/forma.sqlite3`; tato složka se musí zachovat a zálohovat.

## Ovládání

- **Trénink:** vyber Upper/Lower, Začít trénink, plus u cviku. Uprav kg a opakování, ulož sérii. Pod názvem cviku je jeho způsob zápisu. Klepnutím na cvik otevřeš graf a historii. Po cvičení zvol Dokončit.
- **Zásobník + přídavek:** zapisuj zvlášť například 92 kg základ a 30 kg navíc. Jednoručky a jednostranné stroje zapisuj na jednu činku/stranu. Full stack bez známé hmotnosti se porovnává podle opakování, nevymýšlí kilogramy.
- **Plány:** název plánu je upravitelný u cviku; můžeš tak přidat vlastní split. Předvyplněné hodnoty nejsou dokončené série ani historické rekordy. Nejasně datovaná PR z původních poznámek nejsou automaticky importována.
- **Jídlo:** ruční hodnoty celé porce, fotografie, hledání potravin nebo číselný čárový kód. Potraviny z Open Food Facts se přepočtou z hodnot na 100 g podle porce. Databáze potřebuje internet a může mít neúplné údaje; ověř obal. Zdroj: https://world.openfoodfacts.org/ — databáze ODbL.
- **Vlastní recept:** v Profilu otevři Vlastní recept, napiš jednotlivé suroviny a jejich hodnoty pro skutečně použité množství. Aplikace sečte hodnoty a vydělí počtem porcí. Výsledek lze uložit jako oblíbené jídlo.
- **Progres:** váha, pas a fotografie jsou soukromé. U cviků jsou grafy nejvyšší zapsané zátěže za den a historie sérií. Pro full stack jde o graf opakování. Odhad 1RM se nevydává za skutečné PR.
- **Parta:** každý potřebuje svůj účet na stejné instanci aplikace. Pozvánka odkazem propojí účty po přijetí. Pro zveřejnění výkonu zapni sdílení v Profilu a zaškrtni sdílení konkrétního tréninku při dokončení. Jídla, váha a fotky postavy se nikdy neposílají do feedu.
- **Výzvy:** vytvoř období a cíl počtu tréninků. Kamarádi se připojí dobrovolně. Účastníci uvidí počty dokončených tréninků v období, včetně soukromých; nikoli jejich detaily. Z výzvy lze vystoupit.
- **Gamifikace:** 100 XP za dokončený trénink, 25 XP za odcvičený den, úroveň po 500 XP, odznaky a dobrovolné výzvy. Přepínač v Profilu. Nevytváří se tlak na kalorické deficity ani řetězec denních návštěv bez odpočinku. Není chráněna proti úmyslnému podvádění uživatelů.
- **Doplňky:** voda, RPE, kalkulačka kotoučů, pauzy, soukromé fotografie postavy a připomínka v otevřené aplikaci. Připomínky nejsou push notifikace a při zavřené aplikaci nefungují.
- **Export:** Profil → Export všech záznamů (JSON). Export obsahuje metadata fotografií, ne jejich binární data. Plná záloha včetně fotografií je kopie databáze pomocí SQLite backup API. Import exportu přes uživatelské rozhraní není implementovaný.

## Offline režim

Na HTTPS a localhost aplikace registruje service worker pro obálku aplikace. V již otevřeném tréninku lze při výpadku sítě ukládat další série do lokální fronty oddělené podle účtu. Po obnovení připojení se fronta odešle; unikátní ID brání duplicitním sériím. Dokončení tréninku vyžaduje vyprázdněnou frontu.

První přihlášení, zahájení nového tréninku, jídla, fotografie, nastavení a komunita potřebují server. Neodhlašuj se ani nemaž data prohlížeče, dokud máš neodeslané série. Zařízení uchovává poslední kopii vlastních záznamů pro offline režim; používej svůj vlastní zamčený telefon. Při odhlášení se offline kopie odstraní, čekající série se zachovají pro příští přihlášení stejného účtu.

## Nasazení pro iPhone a kamarády

K provozu je nutný server nebo hosting s Dockerem, trvalým diskem a HTTPS. Samotné otevření HTML souboru ani nahrání na čistě statický hosting nestačí.

1. Sestav image: `docker build -t forma .`
2. Nastav `FORMA_PUBLIC_URL` na skutečnou HTTPS adresu. Příklad spuštění za HTTPS reverse proxy:

   ```sh
   docker run -d --name forma -p 127.0.0.1:8765:8765 \
     -e FORMA_PUBLIC_URL=https://forma.example.cz \
     -v forma-data:/data forma
   ```

3. Reverse proxy musí směrovat danou doménu na port 8765, zajistit platný certifikát a omezit velikost požadavků na 3 MB. Zachovej hlavičku Host. Pro rate limitování nastav limity na proxy; interní základní limit používá IP přímého připojení (za proxy tedy může být společný).
4. Připoj trvalý disk `/data`, pravidelnou SQLite zálohu a monitoring. Neukládej SQLite na ephemeral disk ani na běžný sdílený síťový souborový systém. Tento návrh běží jako jedna instance; více replik by potřebovalo změnu databázové vrstvy.
5. Před pozváním velké komunity dokonči ověřování e-mailů, obnovu hesla, zátěžový test a ověření ovládání na skutečném iPhonu a Androidu. V tomto prostředí nebylo možné spustit naslouchající server ani vizuální test prohlížeče.

Na jednom serveru vzniká sdílená databáze s oddělenými účty. Žádná uživatelská data v balíčku nejsou. Náklady a limity hostingu nejsou ověřené a není zaručen nulový provozní náklad.

## Přidání na plochu iPhonu — až po nasazení

1. Otevři **veřejnou HTTPS adresu FORMA v Safari**. `localhost` ani `127.0.0.1` z Macu na telefonu nefungují.
2. Klepni na **Sdílet** (případně přes nabídku dalších možností podle verze iOS).
3. Zvol **Přidat na plochu**.
4. Je-li dostupné **Otevřít jako webovou aplikaci**, ponech zapnuté.
5. Potvrď **Přidat**. Na ploše bude zelená ikona FORMA.

Android: Chrome → nabídka ⋮ → Přidat na plochu / Nainstalovat aplikaci.

Oficiální postup Apple: https://support.apple.com/cs-cz/guide/iphone/iphea86e5236/ios

## AI fotografie — připravené napojení, zatím neaktivní

Provozovatel nastaví `OPENAI_API_KEY` v tajných proměnných serveru (nikdy do frontendových souborů nebo chatu). `OPENAI_MODEL` má výchozí `gpt-4.1-mini`; lze zvolit jiný kompatibilní model s obrazovým vstupem a JSON výstupem. `FORMA_AI_DAILY_LIMIT` omezuje volání na účet (výchozí 10/den, účtování podle UTC). Klíč ani účet API nebyly vytvořeny nebo otestovány v této dodávce. Použití podléhá účtování poskytovatele; běžné předplatné ChatGPT se nepřenáší do vlastní aplikace.

Uživatel před odesláním potvrzuje sdílení fotografie a popisu s OpenAI. Server neposílá jméno, e-mail ani historii. Analýza vrátí odhad kcal a maker pro celou porci; nejsou odhadovány vitamíny ani přesné mikroživiny. Bez klíče aplikace otevřeně zobrazí, že AI není připojená. Nikdy si nevymýšlí výsledek náhodnými čísly. API reference: https://developers.openai.com/api/docs/guides/images-vision

## Účty a zabezpečení

- Funguje e-mail + heslo. **Google a Apple nejsou implementované**; není k dispozici konfigurace klientů ani přihlašovací napojení. Nezobrazují se falešná funkční tlačítka.
- Chybí ověření e-mailu a samoobslužná obnova hesla. Tuto verzi používej jako pilot, ne jako veřejnou službu pro velkou komunitu.
- Hesla PBKDF2-HMAC-SHA256 s náhodnou solí, 310 000 iterací. Sessions mají náhodný token, v databázi je pouze hash; HttpOnly, SameSite=Lax a 30denní expirace. Na HTTPS je nastaven Secure.
- SQL parametry, kontrola vlastníka u privátních operací, ochrana proti cizím Origin, limity požadavků, velikosti souborů a přípon nezávislé ověření formátu JPG/PNG/WebP podle signatury.
- Fotografie se čtou jen přes přihlášený účet vlastníka. Limit uložených fotografií je 100 MB na účet.
- Smazání účtu odstraní jeho data a fotografie kaskádou, ale zálohy musí mít vlastní retenční pravidla provozovatele.
- Pro produkční Docker je povinné `FORMA_PUBLIC_URL=https://…`; přímý vývojový server bez HTTPS není určen pro veřejný internet.

## Ověření

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`

Testy procházejí skutečný HTTP handler přes paměťový transport (prostředí nepovoluje otevřít port). Ověřují registraci, odlišení účtů, idempotentní série, sdílení a jeho odvolání, komentáře, reakce, jídla, metriky, export, soukromé fotografie, validaci, CSRF a smazání účtu. Na macOS navíc JavaScriptCore kontroluje syntaxi app.js/sw.js a čisté funkce vykreslení a oddělení offline front.

Vizuální a end-to-end test skutečného prohlížeče, instalace na iPhone, Docker build, externí databáze potravin a reálné AI volání zde **nebyly provedeny**. Testy nezaručují bezchybný provoz ani výkon pro velký počet současných uživatelů.
