FROM python:3.9 AS main

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# node for aws-cdk
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g aws-cdk@2.27.0

ENV POETRY_VERSION=1.1.11
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH="${PATH}:/root/.poetry/bin"

CMD ["python", "--version"]

# Docker container to generate infrastructure
FROM main AS infra-generator
WORKDIR /app
COPY app/poetry.lock /app
COPY app/pyproject.toml /app

RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY .env /app
COPY app/src /app/src
# During debugging, this entry point will be overridden.
# For more information, please refer to https://aka.ms/vscode-docker-python-debug
WORKDIR /app/src
CMD ["cdk", "deploy"]