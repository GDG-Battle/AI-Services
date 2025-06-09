FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# Update apt, install curl and unzip, install Deno, install Python deps, then clean apt cache
RUN apt-get update && apt-get install -y curl unzip \
    && curl -fsSL https://deno.land/install.sh | sh \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8000

CMD ["python3", "-m", "src.main"]
