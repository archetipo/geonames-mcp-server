import csv
import logging
import os
import pathlib
import sqlite3
from io import BytesIO, TextIOWrapper
from zipfile import ZipFile

import httpx  # Sostituito requests con httpx
from bs4 import BeautifulSoup
import logging
# --- Configurazione ---

logger = logging.getLogger(__name__)

# Username per l'API di GeoNames (legge da variabile d'ambiente con un fallback)
GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME", "demo")

# Percorsi dei dati
DATA_DIR = pathlib.Path(__file__).parent.resolve()
POSTAL_CODES_DIR = DATA_DIR / "data"
DB_PATH = DATA_DIR / "countries.db"

# URL delle API
GEONAMES_ZIP_URL = "http://download.geonames.org/export/zip/"
GEONAMES_API_URL = "http://api.geonames.org/"


# --- Funzioni di Inizializzazione ---

def create_tables(con):
    """Creates all necessary tables in the database."""
    cur = con.cursor()
    # Countries table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            country_code TEXT NOT NULL,
            country_name TEXT NOT NULL,
            lang TEXT NOT NULL,
            PRIMARY KEY (country_code, lang)
        )
    """)
    # Postal codes table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS postal_codes (
            country_code TEXT,
            postal_code TEXT,
            place_name TEXT,
            state_name TEXT,
            state_code TEXT,
            county_name TEXT,
            county_code TEXT,
            community_name TEXT,
            community_code TEXT,
            latitude REAL,
            longitude REAL,
            accuracy INTEGER
        )
    """)
    # Create an index for faster lookups by postal code
    cur.execute("CREATE INDEX IF NOT EXISTS idx_postal_code ON postal_codes (postal_code)")
    con.commit()


def sync_postal_codes(con):
    """
    Downloads postal code data from GeoNames and inserts it into the SQLite database.
    """
    logger.info(f"Starting postal code sync from {GEONAMES_ZIP_URL}")

    try:
        res = httpx.get(GEONAMES_ZIP_URL)
        res.raise_for_status()
    except httpx.RequestError as e:
        logger.error(f"Could not access the dataset list: {e}")
        return

    txt = res.content.decode("utf-8")
    links_all = BeautifulSoup(txt, "html.parser").find_all("a")
    datasets = [
        el["href"] for el in links_all
        if el["href"].endswith(".zip") and el["href"] not in ["GB_full.csv.zip",
                                                              "allCountries.zip"]
    ]

    logger.info(f"Found {len(datasets)} datasets to sync.")
    cur = con.cursor()

    for idx, name_zip in enumerate(datasets):
        country_code = name_zip.replace(".zip", "")
        try:
            url = f"{GEONAMES_ZIP_URL}{name_zip}"
            with httpx.stream("GET", url) as r:
                r.raise_for_status()
                zip_content = BytesIO(r.read())

            # Process the zip file entirely in memory
            with ZipFile(zip_content) as zf:
                name_txt = f"{country_code}.txt"
                # Open the text file from the zip and wrap it for text-mode reading
                with zf.open(name_txt, "r") as fh_in_binary:
                    fh_in_text = TextIOWrapper(fh_in_binary, 'utf-8')
                    # Use csv.reader for robust TSV parsing
                    reader = csv.reader(fh_in_text, delimiter='\t')

                    # Delete old data for this country for a clean import
                    cur.execute("DELETE FROM postal_codes WHERE country_code = ?",
                                (country_code,))

                    # Use executemany for a fast bulk insert
                    cur.executemany(
                        """INSERT INTO postal_codes (
                            country_code, postal_code, place_name,
                            state_name, state_code,
                            county_name, county_code,
                            community_name, community_code,
                            latitude, longitude, accuracy
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        reader
                    )

            logger.info(
                f"  .. [{idx + 1:02}/{len(datasets)}] Synced {cur.rowcount} records for {country_code}")

        except httpx.RequestError as e:
            logger.error(f"Error downloading {name_zip}: {e}")
        except KeyError:
            logger.warning(f"File .txt not found in zip {name_zip}")
        except Exception as e:
            logger.error(f"An unexpected error occurred with {name_zip}: {e}")

    con.commit()
    logger.info("Postal code sync complete.")


def create_country_database(con):
    """
    Crea il database SQLite 'countries.db' e lo popola con i dati
    delle nazioni in italiano e inglese, chiamando l'API di GeoNames.
    """
    logger.info(f"Start creation and population database SQLite  {DB_PATH}")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        cur = con.cursor()
        for lang in ['it', 'en']:
            logger.info(f"Retreive nations pfor lang: '{lang}'")
            params = {'lang': lang, 'username': GEONAMES_USERNAME}
            try:
                # Usa httpx per la chiamata API
                res = httpx.get(f"{GEONAMES_API_URL}countryInfoJSON", params=params)
                res.raise_for_status()
                data = res.json()

                countries_to_insert = [
                    (c['country_code'], c['country_name'], lang)
                    for c in data.get('geonames', [])
                ]

                if countries_to_insert:
                    cur.executemany(
                        "INSERT OR REPLACE INTO countries (country_code, country_name, lang) VALUES (?, ?, ?)",
                        countries_to_insert
                    )
                    logger.info(
                        f"-> Insert update {len(countries_to_insert)} nations for lang '{lang}'.")

            except httpx.RequestError as e:
                logger.error(f"API GeoNames error for language '{lang}': {e}")
            except Exception as e:  # Cattura anche errori di decoding JSON
                logger.error(f"Invalid response or '{lang}' languange error:  {e}")

        con.commit()
        logger.info("Database 'countries.db' creation and population completed.")

    except sqlite3.Error as e:
        logger.error(f"Errore del database SQLite: {e}")


# --- Esecuzione Principale ---


def check_and_sync():
    """Funzione principale che orchestra l'inizializzazione dei dati."""
    if not DB_PATH.is_file():
        logger.info("===== START INIT DATA  =====")
        with sqlite3.connect(DB_PATH) as con:
            logger.info(f"Database opened at {DB_PATH}")
            create_tables(con)  # Create all tables first
            create_country_database(con)
            # Now run the sync functions
            sync_postal_codes(con)

        logger.info("===== INIT DATA COMPLETED =====")
    else:
        logger.info("===== DATA ALREADY EXISTS =====")
