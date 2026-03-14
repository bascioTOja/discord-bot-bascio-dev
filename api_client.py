from json import JSONDecodeError
from typing import Literal, TypeAlias

import httpx
from discord import Interaction
from httpx import Response

from exceptions.api_error import ApiError

JsonType: TypeAlias = dict[str, object] | list[object]


def _get_json(response: Response) -> JsonType:
    try:
        return response.json()
    except JSONDecodeError:
        raise ApiError("JSON decoding error")

async def _post(api_client: ApiClient) -> Response:
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            return await client.post(api_client.url, json=api_client.payload)
    except httpx.RequestError:
        raise ApiError("Could not reach the API.")

class ApiClient:
    def __init__(self, url: str, payload: dict[str, object]) -> None:
        self.url = url
        self.payload = payload

    async def post_json(self, interaction: Interaction, *, expected: Literal["dict", "list"] | None = None, allow_empty: bool = True) -> JsonType:
        await interaction.response.defer(thinking=True)

        response = await _post(self)
        data = _get_json(response)

        if response.status_code in (200, 201):
            if expected == "dict" and not isinstance(data, dict):
                raise ApiError("Unexpected API response.")

            if expected == "list" and not isinstance(data, list):
                raise ApiError("Unexpected API response.")

            if not allow_empty and not data:
                raise ApiError("Empty response.")

            return data

        details = data.get("detail") if isinstance(data, dict) else None

        if response.status_code == 400:
            raise ApiError("Invalid input.", status_code=400, details=details)

        if response.status_code == 409:
            raise ApiError("Conflict. If you provided 'slug', try another one.", status_code=409, details=details)

        raise ApiError(f"API returned status {response.status_code}", status_code=response.status_code, details=details)

    async def post(self, interaction: Interaction) -> JsonType:
        return await self.post_json(interaction)

