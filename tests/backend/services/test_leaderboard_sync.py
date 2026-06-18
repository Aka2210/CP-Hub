import pytest

from backend.app.core.db import AsyncSessionLocal
from backend.app.crud.platform_stats import get_cache_by_user_id
from backend.app.crud.user import get_user_by_discord_id, upsert_account_links
from backend.app.services.sync.leaderboard_sync import LeaderboardSyncService

DISCORD_ID_OK = 900000000000000021
DISCORD_ID_FAILING = 900000000000000022


class StubLeetCodeService:
    async def get_solved_stats(self, username: str):
        if username == "ok_user":
            return {"easy": 1, "medium": 2, "hard": 3}
        raise RuntimeError("simulated LeetCode failure")


class StubCodeforcesService:
    async def get_solved_count(self, handle: str):
        if handle == "ok_user":
            return 7
        raise RuntimeError("simulated Codeforces failure")


@pytest.fixture(autouse=True)
async def cleanup_users():
    yield

    async with AsyncSessionLocal() as session:
        for discord_id in (DISCORD_ID_OK, DISCORD_ID_FAILING):
            user = await get_user_by_discord_id(session, discord_id)
            if user is not None:
                await session.delete(user)
        await session.commit()


@pytest.fixture
def sync_service():
    return LeaderboardSyncService(StubLeetCodeService(), StubCodeforcesService())


@pytest.mark.asyncio
async def test_sync_all_continues_after_per_user_failure(sync_service, monkeypatch):
    monkeypatch.setattr("backend.app.services.sync.leaderboard_sync.DELAY_BETWEEN_REQUESTS_SECONDS", 0)

    async with AsyncSessionLocal() as session:
        ok_user = await upsert_account_links(
            session, discord_id=DISCORD_ID_OK, username="sync_ok_user", leetcode_id="ok_user", codeforces_id="ok_user"
        )
        failing_user = await upsert_account_links(
            session,
            discord_id=DISCORD_ID_FAILING,
            username="sync_failing_user",
            leetcode_id="failing_user",
            codeforces_id="failing_user",
        )

    # The dev database is shared and already has real linked users in it, so scope
    # this test to just the two users created above instead of hitting every real user.
    async def fake_get_users_with_any_platform_link(session):
        return [ok_user, failing_user]

    monkeypatch.setattr(
        "backend.app.services.sync.leaderboard_sync.get_users_with_any_platform_link",
        fake_get_users_with_any_platform_link,
    )

    async with AsyncSessionLocal() as session:
        summary = await sync_service.sync_all(session)

    assert summary == {"leetcode_ok": 1, "leetcode_failed": 1, "codeforces_ok": 1, "codeforces_failed": 1}

    async with AsyncSessionLocal() as session:
        cache = await get_cache_by_user_id(session, ok_user.id)

    assert cache.leetcode_easy == 1
    assert cache.leetcode_medium == 2
    assert cache.leetcode_hard == 3
    assert cache.codeforces_solved == 7
