# ベースイメージ
FROM python:3.9

# 作業ディレクトリの設定
WORKDIR /app

# 必要なパッケージのインストール
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# アプリケーションのコピー
COPY . .

# FastAPIの起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
