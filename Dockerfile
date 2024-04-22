FROM python:3.12.2

RUN mkdir /src

WORKDIR /src

COPY poetry.lock* pyproject.toml ./
COPY pytest.ini ./

ARG INSTALL_DEV=false
RUN pip install --upgrade pip
RUN pip install poetry
RUN set -e \
    && poetry export --without-hashes --format requirements.txt --output requirements.main.txt \
    && poetry export --without-hashes --format requirements.txt --output requirements.all.txt --with dev
RUN echo Install dev packages: $INSTALL_DEV
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then pip install -r requirements.all.txt; else pip install -r requirements.main.txt; fi"

COPY ./src/. /src/.