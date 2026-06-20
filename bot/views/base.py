import logging
from abc import ABC, abstractmethod
from typing import Any

import discord

logger = logging.getLogger(__name__)


class BaseTimeoutView(discord.ui.View):
    def __init__(self, timeout: int = 300):
        super().__init__(timeout=timeout)
        self.message: discord.Message | None = None

    def disable_all_items(self):
        for child in self.children:
            child.disabled = True

    async def on_timeout(self):
        self.disable_all_items()

        if self.message is not None:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                logger.exception("Failed to edit message after view timeout")


class BaseVerifyView(BaseTimeoutView, ABC):
    def __init__(
        self,
        owner_id: int | None = None,
        timeout: int = 300,
        ephemeral: bool = True,
    ):
        super().__init__(timeout=timeout)
        self.owner_id = owner_id
        self.ephemeral = ephemeral

    async def run_verify(self, interaction: discord.Interaction, payload: Any = None):
        if self.owner_id is not None and interaction.user.id != self.owner_id:
            await interaction.response.send_message("只有原本的使用者可以驗證。", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=self.ephemeral)

        try:
            message = await self.do_verify(interaction, payload)
        except Exception:
            logger.exception("Verify action failed")
            await interaction.followup.send("驗證時發生錯誤，請稍後再試。", ephemeral=True)
            return

        if message:
            await interaction.followup.send(message, ephemeral=self.ephemeral)

    @abstractmethod
    async def do_verify(self, interaction: discord.Interaction, payload: Any = None) -> str | None: ...
