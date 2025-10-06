# MCP Client with Ollama

This is a client application that uses **LangChain**, **FastMCP**, and **Ollama** to query geonames / address / postal code via an MCP server, and generate responses via an LLM.

---

## 📦 Prerequisites

- Python 3.13 (locally, if you want to run without Docker)
- Docker & Docker Compose (for containerized mode)
- A running **MCP server** accessible via HTTP. see the [main README](../README.md)
- A running **Ollama server** accessible via HTTP

---

## 🧩 Environment Variables

The client reads its configuration via environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Base URL where Ollama is reachable (no trailing slash) |
| `OLLAMA_MODEL_NAME` | `qwen3:8b` | Name (identifier) of the model to use in Ollama |
| `MCP_SERVER_URL` | `http://localhost:8160/mcp` | URL of the MCP server’s API endpoint (no trailing slash) |

You can override them in your shell or via Docker Compose environment.

---

## 🐳 Docker / Docker Compose Usage

Your `docker-compose.yml` should contain a service definition like:

```yaml
services:
  client:
    build: .
    container_name: mcp_client
    volumes:
      - .:/app
    environment:
      OLLAMA_MODEL_NAME: "qwen3:8b"
      OLLAMA_BASE_URL: "http://host.docker.internal:11434"
      MCP_SERVER_URL: "http://host.docker.internal:8160/mcp"
