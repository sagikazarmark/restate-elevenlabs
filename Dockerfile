FROM ghcr.io/astral-sh/uv:0.10.4@sha256:4cac394b6b72846f8a85a7a0e577c6d61d4e17fe2ccee65d9451a8b3c9efb4ac AS uv


FROM python:3.15.0a8@sha256:21f9b9717fbb2c383547341dc1f2a58e5c8a8942c3fac77492d1f01a0936d43d AS builder

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



FROM python:3.15.0a8-slim@sha256:0818681082dee53faaa7c5376a18ee2c88f5bccd2191d4816dfeea8eb91bcf59

WORKDIR /usr/src/app

ENV PATH="/usr/src/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=builder /usr/src/app .

EXPOSE 9080

CMD [ "python", "-m", "granian", "--interface", "asginl", "src.main:app", "--host", "0.0.0.0", "--port", "9080" ]
