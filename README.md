# GeoNames MCP Server

A **Model Context Protocol (MCP)** server for GeoNames — provides structured geographic lookups via the GeoNames API.

---

## Table of Contents

- [About](#about)  
- [Repository Structure](#repository-structure)  
- [Requirements](#requirements)  
- [Configuration](#configuration)  
- [Installation & Setup](#installation--setup)  
- [Running Docker](#running--docker)
- [Examples](#examples)  
- [Testing](#testing)  
- [Contributing](#contributing)  
- [License](#license)  

---

## About

This project implements an MCP server streamable-http that wraps GeoNames web services, enabling clients (such as agents or applications) to query geographic place names, administrative data, coordinates, and related metadata in a structured manner.

---

## Repository Structure

```
.
├── src/                        # Source code (MCP logic, GeoNames adapter, controllers)
├── example_client/             # an example client (CLI) 
├── tests/                      # Unit / integration tests (WIP)
├── Dockerfile                  # Docker build definition
├── docker-compose.yml          # Compose file for development / local setup
├── docker-compose-test.yaml    # Compose file variant for running tests in containers
├── run_tests.sh                # Script to run tests  
├── update.sh                    # Script to update / restart in production  
├── pyproject.toml              # Poetry configuration (dependencies, scripts)  
├── .dockerignore               # Docker ignore file  
└── .gitignore                   # Git ignore file  
```

Notes:

- The project uses **Poetry** / `pyproject.toml`.
- The Docker / compose setup helps with local development, testing, or containerized deployment.

---

## Requirements

- Python 3.x (minimum version as specified in `pyproject.toml`)  
- Poetry (to install dependencies and manage the environment)  
- Internet access (to call GeoNames API)  
- Docker & Docker Compose (optional, for container-based execution)  

---
## Configuration

The server relies on environment variables (or optionally a `.env` file) for configuration. Typical variables include:

| Variable | Description | Example / Default |
|---|---|---|
| `GEONAMES_USERNAME` | GeoNames API username | *Required* |

---

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/archetipo/geonames-mcp-server.git
   cd geonames-mcp-server
   ```

2. **Install dependencies via Poetry**
   ```bash
   poetry install
   ```

3. **Run Server**
   ```bash
   fastmcp run src/main.py:mcp --transport streamable-http --host 0.0.0.0 --port 8000
   ```

---

## Running Docker

to restart or update the server (pull new code, install changes, restart services) without re-running the full build.
1. **Clone the repository**
   ```bash
   git clone https://github.com/archetipo/geonames-mcp-server.git
   cd geonames-mcp-server
   ```
2. **Run Server**
    ```bash
    ./update.sh
    ```

---

## Examples

[See README the example ](example_client/README.md)

---

## Contributing

1. Fork the repository  
2. Create a feature branch (`feature/xyz`)  
3. Make your changes + add tests  
4. Submit a Pull Request with explanation  

---

## License

Specify the license (MIT, Apache 2.0, etc.).
