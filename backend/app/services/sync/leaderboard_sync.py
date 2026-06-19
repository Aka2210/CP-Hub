import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.crud.platform_stats import get_users_with_any_platform_link, upsert_codeforces_stats, upsert_leetcode_stats
from backend.app.services.codeforces.client import CodeforcesService
from backend.app.services.leetcode.client import LeetCodeService

logger = logging.getLogger(__name__)

DELAY_BETWEEN_REQUESTS_SECONDS = 1.0


class LeaderboardSyncService:
    def __init__(self, leetcode_service: LeetCodeService, codeforces_service: CodeforcesService):
        self.leetcode_service = leetcode_service
        self.codeforces_service = codeforces_service

    async def sync_all(self, session: AsyncSession) -> dict[str, int]:
        """Sequentially syncs every linked user's LeetCode/Codeforces stats into the cache table."""
        users = await get_users_with_any_platform_link(session)
        summary = {"leetcode_ok": 0, "leetcode_failed": 0, "codeforces_ok": 0, "codeforces_failed": 0}

        for user in users:
            if user.leetcode_id is not None:
                try:
                    stats = await self.leetcode_service.get_solved_stats(user.leetcode_id)
                    if stats is not None:
                        await upsert_leetcode_stats(session, user.id, stats["easy"], stats["medium"], stats["hard"])
                        summary["leetcode_ok"] += 1
                    else:
                        summary["leetcode_failed"] += 1
                except RuntimeError:
                    logger.warning("LeetCode sync failed for user_id=%s (%s)", user.id, user.leetcode_id)
                    summary["leetcode_failed"] += 1
                await asyncio.sleep(DELAY_BETWEEN_REQUESTS_SECONDS)

            if user.codeforces_id is not None:
                try:
                    solved = await self.codeforces_service.get_solved_count(user.codeforces_id)
                    if solved is not None:
                        await upsert_codeforces_stats(session, user.id, solved)
                        summary["codeforces_ok"] += 1
                    else:
                        summary["codeforces_failed"] += 1
                except RuntimeError:
                    logger.warning("Codeforces sync failed for user_id=%s (%s)", user.id, user.codeforces_id)
                    summary["codeforces_failed"] += 1
                await asyncio.sleep(DELAY_BETWEEN_REQUESTS_SECONDS)

        return summary
