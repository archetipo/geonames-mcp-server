# 1. Use a slim, efficient base image
FROM python:3.13-slim AS builder

# 2. Set the working directory
WORKDIR /app

# 3. Set the Poetry environment variable
ENV POETRY_VIRTUALENVS_CREATE=false

# 4. Copy only the dependency files first to leverage Docker's cache
COPY .  /app/.

# 5. Install dependencies
RUN pip install --upgrade pip
RUN pip install poetry

RUN echo "Environment: ${ENVIRONMENT}"

RUN if [ "${ENVIRONMENT}" = "test" ]; then  \
       poetry install --no-root ;  \
    else \
      poetry install --no-root --only main ;  \
    fi



FROM builder AS test

ARG TZ=Europe/Rome

ENV MCP_ENVIRONMENT=${ENVIRONMENT}

CMD ["pytest"]

FROM builder AS runtime
ARG TZ=Europe/Rome

ENV MCP_ENVIRONMENT=${ENVIRONMENT}

CMD ["fastmcp", "run", "src/main.py:mcp", "--transport", "streamable-http", "--host", "0.0.0.0",  "--port", "8000"]