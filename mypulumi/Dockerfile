# TODO
FROM python:3.9 AS main

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN curl -fsSL https://get.pulumi.com | sh

# Install poetry
ENV POETRY_VERSION=1.1.11
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH="${PATH}:/root/.poetry/bin"

CMD ["python", "--version"]

# Docker container with tools required to generate data.
FROM main AS infrastructure
WORKDIR /app
COPY app/poetry.lock /app
COPY app/pyproject.toml /app

RUN echo "Updating Pulumi Stack"

# Install project dependencies
RUN poetry config virtualenvs.create false && poetry install --no-dev

# Update the stack
RUN pulumi stack select $STACK_NAME
RUN pulumi up --yes
# During debugging, this entry point will be overridden.
# For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "app.py"]