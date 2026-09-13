FROM python:3.14-slim

# app/main.py computes REPO_ROOT as parents[2] (matches the local dev layout
# repo_root/backend/app/main.py) - WORKDIR must be /app/backend, not /app, so
# that math still resolves to /app (where data/ gets bind-mounted) inside
# the container.
WORKDIR /app/backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
