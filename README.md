# SportStats 2.1

Fotbalová analytická aplikace v Pythonu a Streamlitu s PostgreSQL, správou soutěží, sezón, týmů a zápasů, ligovou tabulkou, statistikami a predikčním modelem Elo + Poisson.

## Co projekt obsahuje

- Přehledový dashboard a výběr soutěže/sezóny
- Správa lig, sezón a týmů
- Plánování zápasů, zadávání výsledků, editace a mazání
- Ligová tabulka (body, skóre, rozdíl gólů)
- Statistiky týmů a grafy
- Predikce 1X2, očekávané góly, nejpravděpodobnější skóre, Elo žebříček a historie přesnosti predikcí
- Uživatelské účty s bcrypt hashováním hesel
- Import původního `sports_data.json`
- PostgreSQL přes SQLAlchemy
- Jednotný tmavý vzhled DarkGreen s neonově zelenými akcenty

## Požadavky

- Python 3.11 nebo novější
- Docker Desktop / Docker Engine (pro lokální PostgreSQL), případně vlastní PostgreSQL server

## 1. Instalace

Rozbal archiv a otevři terminál v adresáři `SportStats_2.0`.

Vytvoř virtuální prostředí:

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Spuštění PostgreSQL

Nejjednodušší lokální varianta:

```bash
docker compose up -d
```

Databáze poběží na `localhost:5432`. Výchozí vývojové přihlašovací údaje jsou definované v `docker-compose.yml`. Pro produkci je bezpodmínečně změň.

## 3. Konfigurace

Zkopíruj `.env.example` na `.env` a uprav hodnoty.

Windows:

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

Změň především `BOOTSTRAP_ADMIN_PASSWORD` na dlouhé unikátní heslo (alespoň 12 znaků). `DATABASE_URL` musí ukazovat na tvoji PostgreSQL databázi.

## 4. První spuštění

```bash
streamlit run streamlit_app.py
```

Aplikace vytvoří databázové tabulky. Pokud je nastaven `BOOTSTRAP_ADMIN_PASSWORD`, vytvoří prvního administrátora, pokud účet `BOOTSTRAP_ADMIN_USERNAME` ještě neexistuje.

Ukázková soutěž se ve výchozím nastavení nevytváří. Demo data lze výslovně zapnout nastavením `SEED_DEMO_DATA=true`.

## 5. Migrace původních dat

1. Zkopíruj původní `sports_data.json` do kořenové složky vedle `streamlit_app.py`.
2. Spusť aplikaci a přihlas se jako administrátor.
3. Otevři **Administrace → Import původních dat** a spusť import.

Alternativně lze import spustit z terminálu:

```bash
python migrate_legacy.py
```

Import podporuje oba formáty používané původní aplikací:
- `liga -> sezóna -> teams/matches`
- starší plochý formát `liga -> teams/matches` (přiřadí sezónu `2025/2026`)

Import je navržen jako nedestruktivní: původní JSON nemaže ani neupravuje a existující týmy/zápasy neduplikuje podle sezóny, data, domácího týmu a hostujícího týmu. Před migrací si přesto udělej kopii JSON souboru a zálohu databáze.

## 6. Záloha PostgreSQL

```bash
docker exec -t sportstats-postgres pg_dump -U sportstats sportstats > sportstats_backup.sql
```

Obnova do lokálního kontejneru:

```bash
docker exec -i sportstats-postgres psql -U sportstats -d sportstats < sportstats_backup.sql
```

## Struktura projektu

```text
SportStats_2.0/
├── streamlit_app.py
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── styles.py
├── migrate_legacy.py
├── core/
│   ├── db.py
│   ├── models.py
│   ├── security.py
│   ├── repository.py
│   ├── migration.py
│   └── seed.py
├── analytics/
│   ├── standings.py
│   └── predictions.py
└── views/
    ├── dashboard.py
    ├── leagues.py
    ├── standings.py
    ├── matches.py
    ├── teams.py
    ├── statistics.py
    ├── predictions.py
    └── admin.py
```

## Důležité poznámky před produkčním nasazením

Toto je funkční výchozí projekt / MVP, ne auditovaná produkční služba.

- Používej HTTPS a tajné, unikátní databázové heslo.
- Nastav zálohování PostgreSQL a otestuj obnovu.
- Pro větší provoz doplň Alembic migrace schématu; `create_all()` samo neprovádí bezpečné změny existujících tabulek.
- Role `viewer` má blokované zapisovací obrazovky; `editor` může spravovat soutěže, týmy a zápasy; `admin` navíc spravuje uživatele a migraci.
- Streamlit session autentizace je zde jednoduchá přihlašovací vrstva. Pro veřejný provoz s více uživateli doporučujeme OIDC/SSO, ochranu proti brute-force, auditní log a bezpečné session cookies.
- Predikční model je orientační statistický základ. Je potřeba jej validovat na historických datech (např. Brier score / log loss), kalibrovat a nepovažovat za záruku výsledku.
- xG není počítáno automaticky, protože původní data neobsahují střelecké události ani xG vstupy.
- Při importu se duplicitní zápas identifikuje kombinací sezóny, data a pořadí domácí/hostující tým. Pokud máš v datech více stejných utkání ve stejný den, zkontroluj import ručně.

## SportStats 2.1 – rozšíření

- Dashboard odděluje poslední odehrané a nadcházející zápasy.
- Statistiky obsahují samostatné domácí a venkovní tabulky a porovnání sezón.
- Predikce naplánovaných zápasů se ukládají a po zadání výsledku se vyhodnocují Brier skóre.
- GitHub Actions kontroluje syntaxi Pythonu a spouští testy výpočtů.

## Další doporučený vývoj

1. Alembic migrace databáze.
2. Opravdové oprávnění `viewer` / `editor` / `admin` na každé CRUD operaci.
3. Auditní log změn a historie výsledků.
4. Testy výpočtů tabulek, migrace a predikcí.
5. Ukládání a zpětné vyhodnocování predikcí (Brier score, log loss).
6. Kalibrace modelu na historických výsledcích.

---

# Nasazení zdarma: Streamlit Community Cloud + Neon PostgreSQL

Tato varianta je určena pro online provoz bez vlastní domény a bez vlastního serveru.
Streamlit Community Cloud hostuje Python aplikaci a Neon poskytuje externí PostgreSQL databázi.
Bezplatné tarify mají limity a jejich podmínky se mohou měnit.

## A. Vytvoření databáze v Neonu

1. Zaregistruj se na <https://neon.com/> a vytvoř projekt `sportstats`.
2. V dashboardu otevři **Connect** a zkopíruj connection string pro PostgreSQL.
3. Pokud Neon nabízí volbu pooled connection, můžeš ji použít pro Streamlit Cloud.
4. Connection string musí mít SSL; aplikace vyžaduje `sslmode=require` a automaticky převede adresu `postgresql://` na ovladač `postgresql+psycopg://`.
5. Connection string nikam veřejně nevkládej a neukládej ho do GitHubu.

## B. Nahrání projektu na GitHub

1. Rozbal ZIP a vytvoř nový GitHub repository, například `sportstats-2`.
2. Nahraj obsah složky `SportStats_2.0` do kořene repozitáře (tak, aby `streamlit_app.py` byl v kořeni).
3. Zkontroluj, že `.env`, `.streamlit/secrets.toml` a databázová hesla nejsou v repozitáři. Jsou uvedeny v `.gitignore`.

## C. Nasazení na Streamlit Community Cloud

1. Otevři <https://share.streamlit.io/> a přihlas se přes GitHub.
2. Zvol **Create app**, vyber repository `sportstats-2`, branch `main` a hlavní soubor `streamlit_app.py`.
3. V pokročilém nastavení vyber Python 3.11, pokud je tato volba zobrazena.
4. Před spuštěním nebo hned po vytvoření aplikace otevři **App settings → Secrets** a vlož TOML konfiguraci níže.
5. Ulož secrets a aplikaci spusť/restartuj.

Vzor Streamlit Secrets (nahraď vlastními hodnotami):

```toml
DATABASE_URL = "postgresql://UZIVATEL:HESLO@HOST/DATABAZE?sslmode=require"
BOOTSTRAP_ADMIN_USERNAME = "admin"
BOOTSTRAP_ADMIN_PASSWORD = "SEM_DEJ_DLOUHE_UNIKATNI_HESLO"
SEED_DEMO_DATA = "false"
```

Doporučení: `BOOTSTRAP_ADMIN_PASSWORD` nastav na dlouhé jedinečné heslo. Jakmile se administrátor vytvoří, změna této hodnoty v Secrets už nezmění heslo existujícího účtu. Heslo lze následně změnit přes správu uživatelů, pokud ji aplikace nabízí.

## D. První spuštění a kontrola

- Při prvním spuštění aplikace vytvoří chybějící tabulky v Neon PostgreSQL; existující záznamy nepřepisuje.
- Pokud je databáze prázdná a `SEED_DEMO_DATA = "true"`, vloží se ukázková liga. Pro čistý start nastav `false`.
- Přihlas se administrátorským účtem.
- Otestuj vytvoření testovací soutěže a zápasu, obnov stránku a ověř, že data zůstala uložena.
- Ověř, že aplikace funguje i v anonymním okně a na mobilu.

## E. Aktualizace aplikace

Po propojení GitHubu Streamlit Community Cloud automaticky nasazuje změny z nastavené větve. Před větší změnou databázového modelu vždy udělej zálohu a počítej s tím, že `create_all()` vytváří chybějící tabulky, ale nenahrazuje verzované databázové migrace.

## F. Import původních dat

Pro import `sports_data.json` je potřeba soubor dodat aplikaci a spustit import jako administrátor v části **Administrace → Import původních dat**. Necommituj citlivá data do veřejného GitHub repozitáře. Pokud původní JSON obsahuje osobní nebo neveřejné údaje, přenes ho bezpečným způsobem a po importu ho z hostingu odstraň.

## Lokální vývoj zůstává podporovaný

Lokálně dál použij `.env` a `docker compose up -d`. Na Streamlit Cloud se místo `.env` používají **App settings → Secrets**. Konfigurace v aplikaci podporuje obě varianty.
