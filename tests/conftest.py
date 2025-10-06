import pytest
import aiosqlite
from types import SimpleNamespace
from geonames_mcp_server.main import AppContext
from collections.abc import AsyncIterator, AsyncGenerator

# 1. Definiamo una fixture per creare un database di test in memoria
@pytest.fixture
@pytest.mark.asyncio
async def test_db():
    # Usa una connessione in memoria per non creare file
    db = await aiosqlite.connect(":memory:")
    db.row_factory = aiosqlite.Row  # Per accedere ai dati per nome di colonna

    # Crea la tabella e inserisci dati di test che conosciamo
    await db.execute("""
        CREATE TABLE countries (
            countryCode TEXT,
            countryName TEXT,
            lang TEXT
        )
    """)
    await db.execute("INSERT INTO countries VALUES ('IT', 'Italy', 'en')")
    await db.execute("INSERT INTO countries VALUES ('DE', 'Germany', 'en')")
    await db.execute("INSERT INTO countries VALUES ('US', 'United States', 'en')")
    await db.commit()

    yield AppContext(db=db)  # Fornisce il database al test

    # Pulisce tutto dopo il test
    await db.close()


@pytest.fixture
def weather_server():
    server = FastMCP("Geonames MCP server")

    @server.tool
    def countries(city: str) -> dict:
        temps = {"NYC": 72, "LA": 85, "Chicago": 68}
        return {"city": city, "temp": temps.get(city, 70)}

    return server

# 2. Definiamo una fixture che simula l'oggetto 'ctx' richiesto dai tool
# @pytest.fixture
# def test_ctx(test_db):
#     """
#     Crea un finto oggetto 'ctx' che contiene la connessione al database di test.
#     Questo ci permette di chiamare i nostri tool in modo isolato.
#     """
#
#
#     # Simuliamo la struttura complessa di 'ctx' che il tool si aspetta
#     lifespan_context = AppContext(db=test_db)
#     request_context = SimpleNamespace(lifespan_context=lifespan_context)
#     ctx = SimpleNamespace(request_context=request_context)
#     return ctx

