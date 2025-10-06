from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import pytest
from mcp.server import FastMCP
from mcp.server.lowlevel.server import Server
from src.geonames_mcp_server.main import AppContext, \
    get_countries  # Assumiamo che hai rinominato la funzione


# Usiamo una classe per raggruppare i test relativi a get_countries
class TestGetCountries:

    @pytest.mark.asyncio
    async def test_get_all_countries(self, test_db):
        """
        Verifica che, senza filtri, la funzione restituisca tutti i paesi
        e che la struttura dei dati sia corretta.
        """

        @asynccontextmanager
        async def test_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
            yield AppContext(db=test_db)

        server = FastMCP("test", lifespan=test_lifespan)
        # Chiama la funzione passando il nostro contesto di test
        countries = await get_countries(ctx=server.get_context(), search_term="", lang="en")

        # ✅ CONTROLLO SPECIFICO: Il numero di risultati è esattamente 3?
        assert len(countries) == 3

        # ✅ CONTROLLO STRUTTURA: Il primo risultato ha le chiavi 'id' e 'label'?
        assert "id" in countries[0]
        assert "label" in countries[0]
        assert countries[0]["id"] == "IT"
        assert countries[0]["label"] == "Italy"

    @pytest.mark.asyncio
    async def test_get_countries_with_search_term(self, test_db):
        """
        Verifica che il filtro di ricerca funzioni correttamente.
        """

        @asynccontextmanager
        async def test_lifespan(server: Server) -> AsyncIterator[AppContext]:
            yield AppContext(db=test_db)

        countries = await get_countries(search_term="Germa", lang="en")

        # ✅ CONTROLLO FUNZIONALITÀ: Deve trovare solo la Germania
        assert len(countries) == 1
        assert countries[0]["label"] == "Germany"

    @pytest.mark.asyncio
    async def test_get_countries_case_insensitive(self, test_db):
        """
        Verifica che la ricerca ignori maiuscole e minuscole.
        """

        @asynccontextmanager
        async def test_lifespan(server: Server) -> AsyncIterator[AppContext]:
            yield AppContext(db=test_db)

        countries = await get_countries(search_term="united STATES", lang="en")

        # ✅ CONTROLLO FUNZIONALITÀ: Deve trovare gli Stati Uniti
        assert len(countries) == 1
        assert countries[0]["id"] == "US"

    @pytest.mark.asyncio
    async def test_get_countries_no_results(self, test_db):
        """
        Verifica che la funzione restituisca una lista vuota se non trova nulla.
        """

        @asynccontextmanager
        async def test_lifespan(server: Server) -> AsyncIterator[AppContext]:
            yield AppContext(db=test_db)

        server = Server[dict[str, bool]]("test", lifespan=test_lifespan)

        countries = await get_countries(ctx=server, search_term="Atlantis", lang="en")

        # ✅ CONTROLLO EDGE CASE: Il risultato deve essere una lista vuota
        assert len(countries) == 0
        assert countries == []
