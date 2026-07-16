# Palworld Server REST API Reference

Source: https://docs.palworldgame.com/category/rest-api

This document mirrors the official Palworld dedicated server REST API documentation, for use as a
reference while building the `ha-palworld` HACS integration.

## Overview

The REST API is a simple HTTP API for managing a Palworld dedicated server (server info, player
management, world save/shutdown, metrics, etc).

- License: Apache 2.0
- Maintained by: Pocketpair, Inc.
- The server also exposes an equivalent RCON API; this document only covers the REST API.

> **Security note:** These APIs are not designed to be exposed directly to the Internet. Exposing
> them publicly could allow unauthorized manipulation of the server, which may interfere with play.
> Pocketpair recommends they only be used within the LAN.

## Enabling the API

The REST API is disabled by default. Enable it in the server's `PalWorldSettings.ini` under
`[/Script/Pal.PalGameWorldSettings]`:

```ini
RESTAPIEnabled=True
RESTAPIPort=8212
AdminPassword=<your-admin-password>
```

- `RESTAPIEnabled` — must be `True` to turn the API on.
- `RESTAPIPort` — port the API listens on (default `8212`).
- `AdminPassword` — used as the password for HTTP Basic Authentication (see below).

## Base URL

```
http://<server-ip>:<RESTAPIPort>/v1/api
```

Default port is `8212` unless overridden in `RESTAPIPort`.

## Authentication

The API uses **HTTP Basic Authentication**.

- Username: `admin`
- Password: the server's `AdminPassword` (as configured in `PalWorldSettings.ini`)

Example with `curl`:

```bash
curl -u admin:<AdminPassword> http://<server-ip>:8212/v1/api/info
```

## Common Response Codes

Most endpoints share this general status code pattern (exceptions noted per-endpoint):

| Code | Meaning |
|------|---------|
| 200  | Success |
| 400  | Bad request / request error |
| 401  | Unauthorized (missing/invalid credentials) |

All successful responses use `Content-Type: application/json` (except where noted).

---

## Endpoints

### GET `/info`

Get the server information.

**Request:** none

**Response `200`:**

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | The server version. |
| `servername` | string | The server name. |
| `description` | string | The server description. |
| `worldguid` | string | The world GUID. |

```json
{
  "version": "v0.1.5.0",
  "servername": "Palworld example Server",
  "description": "This is a Palworld server.",
  "worldguid": "A7E97BAA767DB9029EF013BB71E993A0"
}
```

---

### GET `/players`

Get the player list.

**Request:** none

**Response `200`:**

| Field | Type | Description |
|-------|------|-------------|
| `players` | array of objects | List of connected players (see below). |

Each player object:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | The player name. |
| `accountName` | string | User's platform account name. |
| `playerId` | string | The player ID. |
| `userId` | string | The user ID. |
| `ip` | string | The player IP address. |
| `ping` | number | The player ping. |
| `location_x` | number | The player location X. |
| `location_y` | number | The player location Y. |
| `level` | integer | Current player game level. |
| `building_count` | integer | The number of buildings owned by the player. |

```json
{
  "players": [
    {
      "name": "PalUser",
      "accountName": "paluser",
      "playerId": "AFAFD830000000000000000000000000",
      "userId": "steam_00000000000000000",
      "ip": "127.0.0.1",
      "ping": 3.14,
      "location_x": 123.45,
      "location_y": 67.89,
      "level": 1,
      "building_count": 119
    }
  ]
}
```

---

### GET `/settings`

Get the server settings.

**Request:** none

**Response `200`:**

```json
{
  "Difficulty": "string",
  "DayTimeSpeedRate": 0,
  "NightTimeSpeedRate": 0,
  "ExpRate": 0,
  "PalCaptureRate": 0,
  "PalSpawnNumRate": 0,
  "PalDamageRateAttack": 0,
  "PalDamageRateDefense": 0,
  "PlayerDamageRateAttack": 0,
  "PlayerDamageRateDefense": 0,
  "PlayerStomachDecreaceRate": 0,
  "PlayerStaminaDecreaceRate": 0,
  "PlayerAutoHPRegeneRate": 0,
  "PlayerAutoHpRegeneRateInSleep": 0,
  "PalStomachDecreaceRate": 0,
  "PalStaminaDecreaceRate": 0,
  "PalAutoHPRegeneRate": 0,
  "PalAutoHpRegeneRateInSleep": 0,
  "BuildObjectDamageRate": 0,
  "BuildObjectDeteriorationDamageRate": 0,
  "CollectionDropRate": 0,
  "CollectionObjectHpRate": 0,
  "CollectionObjectRespawnSpeedRate": 0,
  "EnemyDropItemRate": 0,
  "DeathPenalty": "string",
  "bEnablePlayerToPlayerDamage": true,
  "bEnableFriendlyFire": true,
  "bEnableInvaderEnemy": true,
  "bActiveUNKO": true,
  "bEnableAimAssistPad": true,
  "bEnableAimAssistKeyboard": true,
  "DropItemMaxNum": 0,
  "DropItemMaxNum_UNKO": 0,
  "BaseCampMaxNum": 0,
  "BaseCampWorkerMaxNum": 0,
  "DropItemAliveMaxHours": 0,
  "bAutoResetGuildNoOnlinePlayers": true,
  "AutoResetGuildTimeNoOnlinePlayers": 0,
  "GuildPlayerMaxNum": 0,
  "PalEggDefaultHatchingTime": 0,
  "WorkSpeedRate": 0,
  "bIsMultiplay": true,
  "bIsPvP": true,
  "bCanPickupOtherGuildDeathPenaltyDrop": true,
  "bEnableNonLoginPenalty": true,
  "bEnableFastTravel": true,
  "bIsStartLocationSelectByMap": true,
  "bExistPlayerAfterLogout": true,
  "bEnableDefenseOtherGuildPlayer": true,
  "CoopPlayerMaxNum": 0,
  "ServerPlayerMaxNum": 0,
  "ServerName": "string",
  "ServerDescription": "string",
  "PublicPort": 0,
  "PublicIP": "string",
  "RCONEnabled": true,
  "RCONPort": 0,
  "Region": "string",
  "bUseAuth": true,
  "BanListURL": "string",
  "RESTAPIEnabled": true,
  "RESTAPIPort": 0,
  "bShowPlayerList": true,
  "AllowConnectPlatform": "string",
  "bIsUseBackupSaveData": true,
  "LogFormatType": "string"
}
```

All numeric fields above are the corresponding `PalWorldSettings.ini` rate/limit values; boolean
fields (prefixed `b`) mirror the matching `.ini` flags (e.g. `RESTAPIEnabled`, `bIsPvP`).

---

### POST `/announce`

Announce (broadcast) a message to the server.

**Request body** (`application/json`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | yes | The message to announce. |

```json
{
  "message": "The server will be restarting in 5 minutes."
}
```

**Responses:**

| Code | Meaning |
|------|---------|
| 200 | The message was announced. |
| 400 | Bad request. |
| 401 | Unauthorized. |

---

### POST `/kick`

Kick a player from the server.

**Request body** (`application/json`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `userid` | string | yes | The player ID to kick. |
| `message` | string | no | The message to display to the kicked player. |

```json
{
  "userid": "steam_00000000000000000",
  "message": "You have been kicked from the server."
}
```

**Responses:**

| Code | Meaning |
|------|---------|
| 200 | The player was kicked. |
| 400 | Bad request. |
| 401 | Unauthorized. |

---

### POST `/ban`

Ban a player from the server.

**Request body** (`application/json`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `userid` | string | yes | The player ID to ban. |
| `message` | string | no | The message to display to the banned player. |

```json
{
  "userid": "steam_00000000000000000",
  "message": "You have been banned from the server."
}
```

**Responses:**

| Code | Meaning |
|------|---------|
| 200 | The player was banned. |
| 400 | Bad request. |
| 401 | Unauthorized. |

---

### POST `/unban`

Unban a previously banned player.

**Request body** (`application/json`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `userid` | string | yes | The player ID to unban. |

```json
{
  "userid": "steam_00000000000000000"
}
```

**Responses:**

| Code | Meaning |
|------|---------|
| 200 | The player was unbanned. |
| 400 | Bad request. |
| 401 | Unauthorized. |

---

### POST `/save`

Save the world.

**Request:** none

**Responses:**

| Code | Meaning |
|------|---------|
| 200 | Successfully saved the world. |
| 400 | Request error. |
| 401 | Unauthorized. |

---

### POST `/shutdown`

Gracefully shut down the server after a delay, optionally announcing a message first.

**Request body** (`application/json`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `waittime` | integer | yes | Time to wait (seconds) before shutting down the server. |
| `message` | string | no | The message to display before shutting down the server. |

```json
{
  "waittime": 60,
  "message": "The server is shutting down for maintenance."
}
```

**Responses:**

| Code | Meaning |
|------|---------|
| 200 | The server will shutdown. |
| 400 | Bad request. |
| 401 | Unauthorized. |

---

### POST `/stop`

Force stop the server immediately (no save, no grace period).

**Request:** none

**Responses:**

| Code | Meaning |
|------|---------|
| 200 | The server force stopped. |
| 400 | Request error. |
| 401 | Unauthorized. |

---

### GET `/game-data`

Returns a snapshot object with metadata containing a list of all actors in the world at the
moment of the call.

**Request:** none

**Response `200`:**

| Field | Type | Description |
|-------|------|-------------|
| `Time` | string | Snapshot timestamp, `YYYY-MM-DD HH:MM:SS` (server local time). |
| `FPS` | float | Instantaneous server FPS at snapshot time. |
| `AverageFPS` | float | Average server FPS. |
| `ActorData` | array of objects | List of actors in the world (see below). |

`ActorData` entries are one of two shapes:

**CharacterActor** (players, Pals, NPCs):

| Field | Type | Description |
|-------|------|-------------|
| `Type` | string | `"Character"` |
| `InstanceID` | string | Unique actor instance ID. |
| `UnitType` | string | One of `Player`, `OtomoPal`, `BaseCampPal`, `WildPal`, `NPC`. |
| `NickName` | string | Display name. |
| `TrainerInstanceID` | string | Owner's `InstanceID` (only for `OtomoPal`/`BaseCampPal`). |
| `TrainerNickName` | string | Owner's nickname. |
| `TrainerClass` | string | Owner's class. |
| `userid` | string | Player user ID (`Player` type only). |
| `ip` | string | Player IP address. |
| `level` | integer | Level. |
| `HP` | integer | Current HP. |
| `MaxHP` | integer | Max HP. |
| `GuildID` | string | Guild ID. |
| `GuildName` | string | Guild name. |
| `Class` | string | Character/Pal class name. |
| `Action` | string | Current action. |
| `AI_Action` | string | Current AI action. |
| `LocationX`, `LocationY`, `LocationZ` | float | World coordinates. |
| `RotationX`, `RotationY`, `RotationZ` | float | World rotation. |
| `Stage` | string | Map/stage identifier. |
| `IsActive` | string | `"true"` or `"false"`. |

**PalBoxActor** (Palboxes):

| Field | Type | Description |
|-------|------|-------------|
| `Type` | string | `"PalBox"` |
| `GuildID` | string | Guild ID. |
| `GuildName` | string | Guild name. |
| `Class` | string | Class name. |
| `LocationX`, `LocationY`, `LocationZ` | float | World coordinates. |

```json
{
  "Time": "2026-06-17 13:00:40",
  "FPS": 91.71,
  "AverageFPS": 33.78,
  "ActorData": [
    {},
    {}
  ]
}
```

**Responses:**

| Code | Meaning |
|------|---------|
| 200 | Success. |
| 401 | Unauthorized. |

---

### GET `/metrics`

Get the server performance metrics.

**Request:** none

**Response `200`:**

| Field | Type | Description |
|-------|------|-------------|
| `serverfps` | integer | The server FPS. |
| `currentplayernum` | integer | The number of current players. |
| `serverframetime` | number | Server frame time (ms). |
| `maxplayernum` | integer | The maximum number of players. |
| `uptime` | integer | The server uptime, in seconds. |
| `basecampnum` | integer | The number of base camps on the server. |
| `days` | integer | The number of in-game days elapsed. |

```json
{
  "serverfps": 57,
  "currentplayernum": 10,
  "serverframetime": 16.7671,
  "maxplayernum": 32,
  "uptime": 3600,
  "basecampnum": 32,
  "days": 1
}
```

**Responses:**

| Code | Meaning |
|------|---------|
| 200 | Success. |
| 400 | Request error. |
| 401 | Unauthorized. |

---

## Summary Table

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/info` | Server info (version, name, description, world GUID) |
| GET | `/players` | List of connected players |
| GET | `/settings` | Full server settings/config |
| POST | `/announce` | Broadcast a message |
| POST | `/kick` | Kick a player |
| POST | `/ban` | Ban a player |
| POST | `/unban` | Unban a player |
| POST | `/save` | Save the world |
| POST | `/shutdown` | Graceful shutdown with delay/message |
| POST | `/stop` | Force stop immediately |
| GET | `/game-data` | Snapshot of all world actors |
| GET | `/metrics` | Server performance metrics |
