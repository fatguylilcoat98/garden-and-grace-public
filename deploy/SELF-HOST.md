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

Then put two lines in the new **.env** file (you can paste these straight in
the terminal instead of opening an editor):

```
printf '\nANTHROPIC_API_KEY=sk-ant-...your key...\n' >> .env
printf '\nPORT=8001\n' >> .env
```

Port **8001** keeps it clear of Claspion (which uses 8000). Then start the app:

```
bash deploy/run.sh
```

Open **http://YOUR-TAILSCALE-IP:8001** in a browser. That's it — it's live,
and it's now using cheap Claude Haiku instead of expensive Opus.

## Want it even cheaper (Groq)?

In .env, change these and restart:

```
AI_PROVIDER=groq
GROQ_API_KEY=gsk_...your groq key...
```

Test the photo IDs yourself first — cheap models are weaker at naming exact
species. If it's wrong a lot, set `AI_PROVIDER=anthropic` again.

## Make it always-on (start on boot, restart if it crashes)

This is the "set it and forget it" step — like Render, but on your box. One
command. It figures out your username and folder automatically, so there's
nothing to hand-edit:

```
sudo bash deploy/install-service.sh
```

That's it. The app now runs in the background, comes back on reboot, and
restarts itself if it ever crashes. You can close the terminal.

Handy commands afterward:

```
sudo journalctl -u garden-and-grace -f     # watch the logs live
sudo systemctl restart garden-and-grace    # restart it (e.g. after changing .env)
sudo systemctl stop garden-and-grace       # stop it
```

## Updating later

```
cd /opt/garden-and-grace-public
bash deploy/update.sh
```
