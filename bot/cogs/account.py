import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from backend.app.core.db import AsyncSessionLocal
from backend.app.crud.user import AccountIDAlreadyLinkedError, upsert_account_links
from backend.app.services.atcoder.client import AtCoderService
from backend.app.services.codeforces.client import CodeforcesService
from backend.app.services.leetcode.client import LeetCodeService

PLATFORM_NAMES = {"leetcode_id": "LeetCode", "codeforces_id": "Codeforces", "atcoder_id": "AtCoder"}


class Account(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.leetcode_service = LeetCodeService()
        self.codeforces_service = CodeforcesService()
        self.atcoder_service = AtCoderService()

    @app_commands.command(name="link", description="Link your competitive programming accounts (fill in at least one).")
    @app_commands.describe(
        leetcode="Your LeetCode username",
        codeforces="Your Codeforces handle",
        atcoder="Your AtCoder username",
    )
    async def link(
        self,
        interaction: discord.Interaction,
        leetcode: str | None = None,
        codeforces: str | None = None,
        atcoder: str | None = None,
    ):
        accounts = {"leetcode_id": leetcode, "codeforces_id": codeforces, "atcoder_id": atcoder}
        provided = [(field, value) for field, value in accounts.items() if value is not None]

        if not provided:
            await interaction.response.send_message("請至少填寫一個帳號：leetcode、codeforces 或 atcoder。", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            exists_results = await asyncio.gather(*(self._user_exists(field, value) for field, value in provided))

            not_found = [f"{PLATFORM_NAMES[field]} `{value}`" for (field, value), exists in zip(provided, exists_results) if not exists]

            if not_found:
                await interaction.followup.send(f"找不到以下帳號，請確認名稱是否正確：{', '.join(not_found)}")
                return

            async with AsyncSessionLocal() as session:
                try:
                    await upsert_account_links(
                        session,
                        discord_id=interaction.user.id,
                        username=interaction.user.name,
                        leetcode_id=leetcode,
                        codeforces_id=codeforces,
                        atcoder_id=atcoder,
                    )
                except AccountIDAlreadyLinkedError as exc:
                    taken = [f"{PLATFORM_NAMES[field]} `{value}`" for field, value in exc.conflicts.items()]
                    await interaction.followup.send(f"以下帳號已被其他使用者連結：{', '.join(taken)}")
                    return

            linked = [f"{PLATFORM_NAMES[field]}: `{value}`" for field, value in provided]
            await interaction.followup.send("已成功更新帳號連結：\n" + "\n".join(linked))
        except Exception as exc:
            await interaction.followup.send(f"連結失敗：{exc}")

    async def _user_exists(self, field: str, value: str) -> bool:
        if field == "leetcode_id":
            return await self.leetcode_service.user_exists(value)
        if field == "codeforces_id":
            return await self.codeforces_service.user_exists(value)
        return await self.atcoder_service.user_exists(value)


async def setup(bot: commands.Bot):
    await bot.add_cog(Account(bot))
