import discord

from backend.app.core.db import AsyncSessionLocal
from backend.app.crud.user import get_user_by_discord_id
from backend.app.services.stage.service import (
    NoPlatformAccountError,
    NotEnrolledError,
    StageService,
)
from bot.views.base import BaseVerifyView


class StageVerifyView(BaseVerifyView):
    def __init__(self, stage_id: int, original_user_id: int, service: StageService):
        super().__init__(owner_id=original_user_id, timeout=300, ephemeral=False)
        self.stage_id = stage_id
        self.service = service

    @discord.ui.button(label="完成驗證", style=discord.ButtonStyle.green, emoji="✅")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.run_verify(interaction)

    async def do_verify(self, interaction: discord.Interaction, payload=None) -> str | None:
        async with AsyncSessionLocal() as session:
            user = await get_user_by_discord_id(session, interaction.user.id)
            if user is None:
                return "找不到你的帳號，請先用 `/account register` 註冊。"

            try:
                result = await self.service.verify_and_advance(session, user, self.stage_id)
            except (NotEnrolledError, NoPlatformAccountError) as e:
                return str(e)

        if not result.solved:
            return "尚未看到你的 AC 提交，請確認已成功提交後再試一次。"

        lines = [f"{interaction.user.mention} 解題成功！獲得 **{result.problem_rewards['exp']} EXP** 和 **{result.problem_rewards['coins']} 金幣**！"]

        if result.stage_complete:
            lines.append(f"🎉 關卡完成！額外獲得 **{result.stage_rewards['exp']} EXP** 和 **{result.stage_rewards['coins']} 金幣**！")
            self.disable_all_items()
            if interaction.message is not None:
                await interaction.message.edit(view=self)
        else:
            lines.append("繼續加油！使用 `/stage play` 查看下一題。")

        return "\n".join(lines)
