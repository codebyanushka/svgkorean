# Deploying Hangugeo to AWS EC2 (t3.micro, always-on)

## 1. Security Group - open ports 80 and 443
Your instance's Security Group (shown on the "Connect" page, e.g.
`launch-wizard-5`) only has port 22 open by default. Add 2 inbound rules:
EC2 Console -> Security Groups -> your group -> Edit inbound rules -> Add rule
-> Type: HTTP (port 80), Source: 0.0.0.0/0. Repeat for HTTPS (port 443).
Without this the app is unreachable from the internet even once it's running.

## 2. Connect to the instance
Easiest: EC2 Console -> Instances -> select your instance -> Connect ->
"EC2 Instance Connect" tab -> Connect. This opens a browser-based terminal,
no SSH key file needed.

## 3. One-time server setup
In that browser terminal:
```
git clone <your-repo-url> hangugeo
cd hangugeo
bash deploy/aws-setup.sh
```
Log out and back in (Connect again) for the docker group change to apply.

## 4. Copy the real content files (not in git)
`data/raw/` and `data/extracted/` are gitignored on purpose (copyrighted
source material) - `git clone` will NOT bring them. From your LOCAL machine's
terminal (not the EC2 one), copy them up once:
```
rsync -avz /Users/anushkatiwarii/hangugeo/data/ ubuntu@<EC2_PUBLIC_IP>:~/hangugeo/data/
```
Re-run this any time the local content changes. Find `<EC2_PUBLIC_IP>` on the
instance's details page (e.g. `3.110.176.254`).

## 5. Configure secrets
Back in the EC2 terminal:
```
cd ~/hangugeo
cp .env.example .env                                   # root - sets POSTGRES_PASSWORD
cp backend/env.production.example backend/.env.production
```
Edit both files (`nano .env` / `nano backend/.env.production`):
- `.env`: set `POSTGRES_PASSWORD` to a long random value (e.g. `openssl rand -hex 24`).
- `backend/.env.production`: use the SAME password in `DATABASE_URL`, set
  `JWT_SECRET_KEY` (e.g. `openssl rand -hex 32`), set `CORS_ALLOW_ORIGINS` to
  `["http://<EC2_PUBLIC_IP>"]` (or your domain once you have one).

## 6. Build and start everything
```
docker compose up -d --build
```
This starts Postgres, runs Alembic migrations automatically (see
`backend/entrypoint.sh`), starts the backend, and starts nginx serving the
frontend + proxying `/api` and `/media` to the backend - all with
`restart: always`, so they come back up automatically after a crash or
instance reboot.

Visit `http://<EC2_PUBLIC_IP>` - the app should be live.

## 7. Create your first teacher account
```
docker compose exec backend python scripts/create_user.py --username teacher1 --password <choose one> --role TEACHER
```

## 8. (Optional, later) Add a real domain + HTTPS
Point a domain's A record at `<EC2_PUBLIC_IP>`, then set up certbot
(`docker run --rm -v ./deploy/certbot/conf:/etc/letsencrypt -v ./deploy/certbot/www:/var/www/certbot certbot/certbot certonly --webroot -w /var/www/certbot -d yourdomain.com`)
and update `frontend/nginx.conf` to listen on 443 with the issued cert. Ask
if/when you're ready for this step - it needs a real domain name first.

## Notes on t3.micro (1GB RAM)
`deploy/aws-setup.sh` adds a 2GB swap file since Postgres + backend + nginx
together are tight on 1GB alone. If the instance ever feels sluggish, check
`free -h` and `docker stats` before assuming it's a real capacity problem -
this app's traffic (a handful of students) is light enough that a properly
swapped t3.micro should hold up fine.

## Also double-check AWS Free Tier eligibility
Confirm in the AWS Billing console that this instance/region is actually
covered by your account's free tier terms before leaving it running long-term
- AWS's free-tier offer has changed over time and varies by account age.

## Updating the app later
```
git pull
docker compose up -d --build
```
