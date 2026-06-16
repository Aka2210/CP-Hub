import discord
from discord.ext import commands
from google import genai
from google.genai import types

from backend.app.core.config import settings


class MentionChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = genai.Client(api_key=settings.gemini_api_key)

        self.system_instruction = (
            "請 5000 字內回答完問題"
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if self.bot.user in message.mentions and not message.mention_everyone:
            clean_content = message.content.replace(f"<@!{self.bot.user.id}>", "").replace(f"<@{self.bot.user.id}>", "").strip()

            if not clean_content:
                await message.reply("你標我然後什麼話都不說，丘比生氣了")
                return

            async with message.channel.typing():
                try:
                    response = self.client.models.generate_content(
                        model="gemini-2.5-flash-lite",
                        contents=clean_content,
                        config=types.GenerateContentConfig(
                            system_instruction=self.system_instruction,
                            temperature=0.7,
                        ),
                    )

                    await message.reply(response.text[:5500])

                except Exception as e:
                    await message.reply(f"發生錯誤: {str(e)}")


async def setup(bot):
    await bot.add_cog(MentionChat(bot))
