FROM ghcr.io/astral-sh/uv:0.10.4@sha256:4cac394b6b72846f8a85a7a0e577c6d61d4e17fe2ccee65d9451a8b3c9efb4ac AS uv


FROM python:3.14.2@sha256:f05033a4c0ff84db95fd7e6cb361b940a260703d1cd63c63b3472c8ee48e9cff AS builder

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /uvx /bin/

WORKDIR /usr/src/app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --extra app --no-install-project

COPY . .

RUN uv sync --frozen --no-dev --extra app



FROM python:3.14.2-slim@sha256:f7864aa85847985ba72d2dcbcbafd7475354c848e1abbdf84f523a100800ae0b

WORKDIR /usr/src/app

ENV PATH="/usr/src/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=builder /usr/src/app .

EXPOSE 9080

CMD [ "python", "-m", "granian", "--interface", "asginl", "src.main:app", "--host", "0.0.0.0", "--port", "9080" ]
