FROM python:3.7

RUN pip3 install poetry

WORKDIR /app

# Install app dependencies
COPY pyproject.toml ./
COPY poetry.lock ./
RUN poetry install --no-dev

# Bundle app source
COPY . /app

ENV PYTHONUNBUFFERED=1

# Run the node
CMD poetry run python server.py
