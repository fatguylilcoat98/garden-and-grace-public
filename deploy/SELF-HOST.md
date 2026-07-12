# Running Garden & Grace on your own server (phone-friendly)

Everything is one process — the app serves the website AND the AI. No Render.

## Get it running (do this once)

In the VS Code terminal, on your server:

```
cd /opt                                   # or wherever you keep your apps
git clone https://github.com/fatguylilcoat98/garden-and-grace-public.git
cd garden-and-grace-public
bash deploy/setup.sh
```

Then open the new **.env** file in VS Code and fill in one line:

```
ANTHROPIC_API_KEY=sk-ant-...your key...
```

Save it, then start the app:

```
bash deploy/run.sh
```

Open **http://YOUR-TAILSCALE-IP:8000** in a browser. That's it — it's live,
and it's now using cheap Claude Haiku instead of expensive Opus.

## Want it even cheaper (Groq)?

In .env, change these and restart:

```
AI_PROVIDER=groq
GROQ_API_KEY=gsk_...your groq key...
```

Test the photo IDs yourself first — cheap models are weaker at naming exact
species. If it's wrong a lot, set `AI_PROVIDER=anthropic` again.

## Make it start on boot (optional, do after it works)

1. Edit `deploy/garden-and-grace.service` — fix the 3 lines marked CHANGE
   (the folder path and your username).
2. Install it:

```
sudo cp deploy/garden-and-grace.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now garden-and-grace
sudo systemctl status garden-and-grace
```

## Updating later

```
cd /opt/garden-and-grace-public
bash deploy/update.sh
```
