import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    discord_token: str
    announce_channel_id: int
    debug_channel_id: int
    api_base_url: str
    api_scheme: str
    api_host: str

def _parse_int(value: str | None) -> int | None:
    if value is None or value.strip() == "":
        return None
    return int(value.strip())

def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    v = value.strip().lower()
    if v in {"1", "true"}:
        return True
    if v in {"0", "false"}:
        return False
    return default

def load_config() -> Config:
    load_dotenv()

    discord_token = os.getenv("DISCORD_TOKEN")
    if not discord_token:
        raise RuntimeError("Missing DISCORD_TOKEN in .env")

    announce_channel_id = _parse_int(os.getenv("ANNOUNCE_CHANNEL_ID"))
    if not announce_channel_id:
        raise RuntimeError("Missing ANNOUNCE_CHANNEL_ID in .env")

    debug_channel_id = _parse_int(os.getenv("DEBUG_CHANNEL_ID")) or announce_channel_id

    api_base_url = os.getenv("API_BASE_URL")
    if api_base_url and api_base_url.strip():
        api_base_url = api_base_url.strip().rstrip("/")
        if "://" not in api_base_url:
            raise RuntimeError("API_BASE_URL must include scheme, e.g. https://api.example.com")
        api_scheme, rest = api_base_url.split("://", 1)
        api_host = rest.strip().rstrip("/")
        if not api_host:
            raise RuntimeError("API_BASE_URL missing host")
    else :
        raise RuntimeError("Missing API_BASE_URL in .env")

    return Config(
        discord_token=discord_token.strip(),
        announce_channel_id=announce_channel_id,
        debug_channel_id=debug_channel_id,
        api_base_url=api_base_url,
        api_scheme=api_scheme,
        api_host=api_host,
    )
