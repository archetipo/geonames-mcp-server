import logging
import pathlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Union, List, Any

import aiosqlite  # Importa la libreria per SQLite asincrono
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_context
from mcp.server.lowlevel.server import LifespanResultT

from initdata import check_and_sync
from services import PostalCode, Country, get_cities, get_countries, \
    get_postal_code

logging.basicConfig(format="%(asctime)-15s %(levelname)-8s %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Le tue configurazioni originali
# GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME", "demo")
# GEONAMES_URL = os.getenv("GEONAMES_URL", "http://api.geonames.org/")
DATA_DIR = pathlib.Path(__file__).parent.resolve()
POSTAL_CODES_DIR = DATA_DIR / "data"
DB_PATH = DATA_DIR / "countries.db"


# --- NUOVA GESTIONE LIFESPAN CON SQLITE ---
@asynccontextmanager
async def app_lifespan(server: FastMCP[LifespanResultT]) -> AsyncIterator[Any]:
    print("Starting app... Connecting to database.")
    # Connettiti al DB SQLite e imposta la row_factory per ottenere dict invece di tuple
    check_and_sync()
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    ctx = {"db": db}  # il tuo lifespan context
    yield ctx
    await db.close()
    print("Starting app... Closinng to database.")


mcp = FastMCP("Geoname MCP", lifespan=app_lifespan)


# --- ENDPOINT REFACTORIZZATI CON SQL ---

@mcp.tool()
async def countries(
        search_term: str = "",
        lang: str = "it"
) -> Union[List[Country], str]:
    """
    Retrieves a list of countries, optionally filtering by a search term.

    This tool queries the database for countries matching the specified language.
    The result is a list of dictionaries, each containing an 'id' (the country code)
    and a 'label' (the country name), suitable for display in user interfaces.
    """
    ctx = get_context()
    db = ctx.request_context.lifespan_context.get("db")
    return await get_countries(db, search_term, lang)


@mcp.tool()
async def find_cities_by_name(
        country_code: str = "",
        city_name: str = "",
        limit: int = 10
) -> Union[List[PostalCode], str]:
    """
    Searches for cities within a given country based on a partial name.

    Returns a list of matching locations, including details like county, postal code,
    and geographic coordinates. The search is case-insensitive.
    Params:
        country_code: The two-letter ISO 3166-1 alpha-2 country code (e.g., 'IT', 'DE').
        city_name: A partial or full city name to search for.
        limit: The maximum number of results to return. Defaults to 10.
    """
    ctx = get_context()
    db = ctx.request_context.lifespan_context.get("db")
    return await get_cities(db, country_code, city_name, limit)


@mcp.tool()
async def get_location_by_postal_code(
        country_code: str = "",
        postal_code: str = ""
) -> Union[List[PostalCode], str]:
    """
    Retrieves detailed location information for a specific postal code in a country.

    This tool first queries the local database. If a record is found, it then attempts
    to enrich the data with additional details (like cadastral info) from an external API.
    The tool is designed to work even if the external API is unavailable.
    Params:
        country_code: The two-letter ISO 3166-1 alpha-2 country code (e.g., 'IT', 'DE').
        postal_code: The exact postal code to search for.
    """
    ctx = get_context()
    db = ctx.request_context.lifespan_context.get("db")

    return await get_postal_code(db, country_code, postal_code)


def main():
    # Initialize and run the server
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
