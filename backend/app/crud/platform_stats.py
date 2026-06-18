from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.platform_stats_cache import PlatformStatsCache
from backend.app.models.user import User


async def get_users_with_any_platform_link(session: AsyncSession) -> list[User]:
    result = await session.execute(select(User).where(or_(User.leetcode_id.is_not(None), User.codeforces_id.is_not(None))))
    return list(result.scalars().all())


async def get_cache_by_user_id(session: AsyncSession, user_id) -> PlatformStatsCache | None:
    result = await session.execute(select(PlatformStatsCache).where(PlatformStatsCache.user_id == user_id))
    return result.scalar_one_or_none()


async def _get_or_create_cache(session: AsyncSession, user_id) -> PlatformStatsCache:
    cache = await get_cache_by_user_id(session, user_id)
    if cache is None:
        cache = PlatformStatsCache(user_id=user_id)
        session.add(cache)
    return cache


async def upsert_leetcode_stats(session: AsyncSession, user_id, easy: int, medium: int, hard: int) -> None:
    cache = await _get_or_create_cache(session, user_id)
    cache.leetcode_easy = easy
    cache.leetcode_medium = medium
    cache.leetcode_hard = hard
    cache.leetcode_synced_at = datetime.now(timezone.utc)
    await session.commit()


async def upsert_codeforces_stats(session: AsyncSession, user_id, solved: int) -> None:
    cache = await _get_or_create_cache(session, user_id)
    cache.codeforces_solved = solved
    cache.codeforces_synced_at = datetime.now(timezone.utc)
    await session.commit()


async def get_top_by_leetcode(session: AsyncSession, limit: int = 10) -> list[tuple[User, PlatformStatsCache]]:
    result = await session.execute(
        select(User, PlatformStatsCache)
        .join(PlatformStatsCache, PlatformStatsCache.user_id == User.id)
        .where(PlatformStatsCache.leetcode_easy.is_not(None))
        .order_by((PlatformStatsCache.leetcode_easy + PlatformStatsCache.leetcode_medium + PlatformStatsCache.leetcode_hard).desc())
        .limit(limit)
    )
    return [(row.User, row.PlatformStatsCache) for row in result.all()]


async def get_top_by_codeforces(session: AsyncSession, limit: int = 10) -> list[tuple[User, PlatformStatsCache]]:
    result = await session.execute(
        select(User, PlatformStatsCache)
        .join(PlatformStatsCache, PlatformStatsCache.user_id == User.id)
        .where(PlatformStatsCache.codeforces_solved.is_not(None))
        .order_by(PlatformStatsCache.codeforces_solved.desc())
        .limit(limit)
    )
    return [(row.User, row.PlatformStatsCache) for row in result.all()]
