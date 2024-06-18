FROM python:3.9-slim

WORKDIR /app

COPY ./resource/requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY ./src .

RUN useradd -m fastapi_user
USER fastapi_user

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
