from dataclasses import dataclass
from typing import Optional, Union, List
from aiosqlite import Connection
import logging

logger = logging.getLogger(__name__)

@dataclass
class PostalCode:
    country_code: str
    postal_code: str
    place_name: str
    state_name: Optional[str] = None
    state_code: Optional[str] = None
    county_name: Optional[str] = None
    county_code: Optional[str] = None
    community_name: Optional[str] = None
    community_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[int] = None


@dataclass
class Country:
    country_code: str
    country_name: str


@dataclass
class Item:
    id: str
    label: str


async def countries(
        db: Connection,
        search_term: str = None,
        lang: str = "it"
) -> Union[List[Item], str]:
    query = "SELECT country_code, country_name FROM countries WHERE lang = ?"
    params = [lang]

    if search_term:
        query += " AND LOWER(country_name) LIKE ?"
        params.append(f"%{search_term.lower()}%")

    async with db.execute(query, tuple(params)) as cursor:
        rows = await cursor.fetchall()
        # Formatta il risultato come richiesto
        return [Item(id=row["country_code"], label=row["country_name"]) for row in rows]


async def get_countries(
        db: Connection,
        search_term: str = "",
        lang: str = "it"
) -> Union[List[Country], str]:
    query = "SELECT country_code, country_name FROM countries WHERE lang = ?"
    params = [lang]

    if search_term:
        # La query SQL con LIKE è molto più efficiente del filtro in Python
        query += " AND LOWER(country_name) LIKE ?"
        params.append(f"%{search_term.lower()}%")
    try:
        async with db.execute(query, tuple(params)) as cursor:
            rows = await cursor.fetchall()
            # Converte le righe del DB in una lista di dizionari
            vals = [Country(**dict(row)) for row in rows]
            if vals is not None:
                # Convert the value to JSON string for consistent return type
                return vals
            else:
                return f"No data found for country '{search_term}'."
    except Exception as e:
        logger.error(f"Error retrieving data for country '{search_term}': {str(e)}", exc_info=True)
        return f"Error retrieving data for country '{search_term}': {str(e)}"



async def get_cities(
        db: Connection,
        country: str,
        city: str = "",
        top_k: int = 10
) -> Union[List[PostalCode], str]:
    """
    Searches for cities in the database based on a partial name.
    """
    query = """
            SELECT *
            FROM postal_codes
            WHERE country_code = ? \
              AND (LOWER(place_name) = ? OR LOWER(place_name) LIKE ?) \
              ORDER BY CASE WHEN LOWER(place_name) = ? THEN 0 ELSE 1 END \
              LIMIT ? \
            """
    # The '%' are wildcards for the SQL LIKE search
    params = (country.upper(), city.lower(), f"%{city.lower()}%", city.lower(), top_k)
    try:
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            # Convert database rows to a list of dictionaries
            logger.info(rows)
            vals = [PostalCode(**dict(row)) for row in rows]
            if vals is not None:
                # Convert the value to JSON string for consistent return type
                return vals
            else:
                return f"No data found for country '{country}' city '{city}'."
    except Exception as e:
        return f"Error retrieving data for country '{country}' city '{city}': {str(e)}"


async def get_postal_code(
        db: Connection,
        country: str,
        posta_code: str = ""
) -> Union[List[PostalCode], str]:
    query = """
            SELECT *
            FROM postal_codes
            WHERE country_code = ? \
              AND postal_code = ? \
            """
    params = (country.upper(), posta_code)
    try:
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            # Convert database rows to a list of dictionaries
            vals = [PostalCode(**dict(row)) for row in rows]
            if vals is not None:
                # Convert the value to JSON string for consistent return type
                return vals
            else:
                return f"No data found for country '{country}' city '{city}'."
    except Exception as e:
        return f"Error retrieving data for country '{country}' city '{city}': {str(e)}"
