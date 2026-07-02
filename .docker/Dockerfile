FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app \
    BERKELEYDB_DIR=/usr

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libleveldb-dev libdb-dev g++ \
    && rm -rf /var/lib/apt/lists/*

ADD https://github.com/apple/foundationdb/releases/download/7.4.6/foundationdb-clients_7.4.6-1_amd64.deb /tmp/fdb-clients.deb
RUN dpkg -i /tmp/fdb-clients.deb && rm /tmp/fdb-clients.deb

COPY .docker/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["sleep", "infinity"]