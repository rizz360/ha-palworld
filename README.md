# Palworld Server for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A [HACS](https://hacs.xyz/) custom integration that connects Home Assistant to a Palworld
dedicated server via its built-in [REST API](https://docs.palworldgame.com/category/rest-api).
See [docs/api.md](docs/api.md) for the full API reference this integration is built against.

## Features

- Sensors: server FPS, frame time, current/max players, base camp count, in-game days,
  uptime, server version, and connected player list.
- Buttons: save world, force stop (disabled by default).
- Services: `palworld.announce`, `palworld.kick`, `palworld.ban`, `palworld.unban`,
  `palworld.save_world`, `palworld.shutdown`, `palworld.force_stop`.

## Requirements

Enable the REST API on your Palworld dedicated server in `PalWorldSettings.ini`:

```ini
[/Script/Pal.PalGameWorldSettings]
RESTAPIEnabled=True
RESTAPIPort=8212
AdminPassword=<your-admin-password>
```

> The API is not designed to be exposed to the Internet — only use it within your LAN, or over
> a VPN/tunnel you control.

## Installation

### HACS (recommended)

1. In HACS, go to **Integrations** → menu (⋮) → **Custom repositories**.
2. Add `https://github.com/rizz360/ha-palworld` as an **Integration**.
3. Install "Palworld Server" from HACS, then restart Home Assistant.

### Manual

Copy `custom_components/palworld` into your Home Assistant `config/custom_components/`
directory and restart Home Assistant.

## Configuration

In Home Assistant, go to **Settings → Devices & Services → Add Integration**, search for
"Palworld Server", and enter:

- **Host** — the server's IP address or hostname.
- **Port** — the `RESTAPIPort` from your `PalWorldSettings.ini` (default `8212`).
- **Username** — normally `admin`.
- **Admin password** — the `AdminPassword` from your `PalWorldSettings.ini`.

Polling interval can be adjusted afterward from the integration's **Configure** options.

## Disclaimer

This is an unofficial, community-built integration and is not affiliated with or endorsed by
Pocketpair, Inc.
