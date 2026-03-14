from discord import Interaction


class ApiError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None, details: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

    async def send(self, interaction: Interaction) -> None:
        details_txt = f" Details: {self.details}" if self.details is not None else ""
        await interaction.followup.send(f"{self.message}{details_txt}", ephemeral=True)
