import os
import asyncio
from google import genai
from fastmcp import Client

mcp_server_url = os.environ.get("MCP_SERVER_URL", "http://localhost:8160/mcp")
gemini_key = os.environ.get("GOOGLE_API_KEY", "demo")
gemini_model = "gemini-2.5-flash"
mcp_client = Client(mcp_server_url)
gemini_client = genai.Client(api_key=gemini_key)


# --- Il "Cervello" del nostro Agente ---
async def run_conversation(
        user_prompt: str,
        system_prompt: str
):
    """
    Gestisce un singolo ciclo di conversazione con l'agente Gemini.
    """
    print(f"👤: {user_prompt}")

    async with mcp_client:
        gemini_client = genai.Client(api_key=gemini_key)
        response = await gemini_client.aio.models.generate_content(
            model=gemini_model,
            contents=user_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0,
                tools=[mcp_client.session]  # Pass the FastMCP client session
            ),
        )
        print(f"🤖: {response.text}")
        gemini_client.close()

    print("-" * 50)


async def main():
    """
    Funzione principale che configura e avvia le conversazioni.
    """
    system_prompt = (
        "You are a helpful assistant for finding countries and cities. "
        "Respond briefly and concisely and in the language of the request."
    )


    user_prompts = [
        "give me city name of E3Y on Canada",
        "Cerca la label indirizzo per strada delle cacce 91 con cap 10135",
        "Cerca il codice postale di Alba in Italia, rispondi in inglese",
        "Cerca il codice postale di tutte le citta' che iniziano con Alba in Italia"
    ]

    for prompt in user_prompts:
        await run_conversation(
            user_prompt=prompt,
            system_prompt=system_prompt
        )

    gemini_client.close()

if __name__ == "__main__":
    asyncio.run(main())