FROM python:3.12.2

RUN mkdir /src

WORKDIR /src

COPY poetry.lock* pyproject.toml ./
COPY pytest.ini ./

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry export --without-hashes --format requirements.txt --output requirements.txt
RUN bash -c "pip install -r requirements.txt"

COPY ./src/. /src/.
