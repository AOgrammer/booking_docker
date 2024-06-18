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

RUN useradd -m streamlit_user
USER streamlit_user

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
