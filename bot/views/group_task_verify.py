from typing import Protocol

import discord

from backend.app.models.group_task_problem import GroupTaskProblem
from bot.views.base import BaseVerifyView


class GroupTaskVerifyHandler(Protocol):
    async def handle_verify_selection(
        self,
        interaction: discord.Interaction,
        codes: list[str],
    ) -> None: ...


class GroupTaskVerifySelect(discord.ui.Select):
    def __init__(self, view: "GroupTaskVerifyView", problems: list[GroupTaskProblem]):
        options = [discord.SelectOption(label=f"{p.code} {p.title}"[:100], value=p.code) for p in problems[:25]]

        super().__init__(
            placeholder="選擇要驗證的題目（可多選）",
            min_values=1,
            max_values=len(options),
            options=options,
        )

        self.verify_view = view

    async def callback(self, interaction: discord.Interaction):
        await self.verify_view.run_verify(interaction, list(self.values))


class GroupTaskVerifyView(BaseVerifyView):
    def __init__(
        self,
        handler: GroupTaskVerifyHandler,
        owner_id: int,
        problems: list[GroupTaskProblem],
    ):
        super().__init__(owner_id=owner_id, timeout=300, ephemeral=True)
        self.handler = handler
        self.add_item(GroupTaskVerifySelect(self, problems))

    async def do_verify(self, interaction: discord.Interaction, payload=None) -> None:
        codes = payload or []
        await self.handler.handle_verify_selection(interaction, codes)
        return None
