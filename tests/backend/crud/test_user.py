import pytest

from backend.app.core.db import AsyncSessionLocal
from backend.app.crud.user import AccountIDAlreadyLinkedError, get_user_by_discord_id, upsert_account_links

DISCORD_ID_A = 900000000000000001
DISCORD_ID_B = 900000000000000002


@pytest.fixture(autouse=True)
async def cleanup_users():
    yield

    async with AsyncSessionLocal() as session:
        for discord_id in (DISCORD_ID_A, DISCORD_ID_B):
            user = await get_user_by_discord_id(session, discord_id)
            if user is not None:
                await session.delete(user)
        await session.commit()


@pytest.mark.asyncio
async def test_get_user_by_discord_id_not_found():
    async with AsyncSessionLocal() as session:
        user = await get_user_by_discord_id(session, DISCORD_ID_A)

    assert user is None


@pytest.mark.asyncio
async def test_upsert_account_links_creates_user():
    async with AsyncSessionLocal() as session:
        user = await upsert_account_links(session, discord_id=DISCORD_ID_A, username="test_user_a", leetcode_id="neal_wu")

        assert user.discord_id == DISCORD_ID_A
        assert user.leetcode_id == "neal_wu"
        assert user.codeforces_id is None
        assert user.atcoder_id is None
        assert user.stats.level == 1
        assert user.stats.coins == 0


@pytest.mark.asyncio
async def test_upsert_account_links_adds_to_existing_user_without_overwriting():
    async with AsyncSessionLocal() as session:
        await upsert_account_links(session, discord_id=DISCORD_ID_A, username="test_user_a", leetcode_id="neal_wu")

    async with AsyncSessionLocal() as session:
        user = await upsert_account_links(session, discord_id=DISCORD_ID_A, username="test_user_a", codeforces_id="tourist")

        assert user.leetcode_id == "neal_wu"
        assert user.codeforces_id == "tourist"


@pytest.mark.asyncio
async def test_upsert_account_links_with_multiple_accounts_at_once():
    async with AsyncSessionLocal() as session:
        user = await upsert_account_links(
            session,
            discord_id=DISCORD_ID_A,
            username="test_user_a",
            leetcode_id="neal_wu",
            codeforces_id="tourist",
            atcoder_id="tourist",
        )

        assert user.leetcode_id == "neal_wu"
        assert user.codeforces_id == "tourist"
        assert user.atcoder_id == "tourist"


@pytest.mark.asyncio
async def test_upsert_account_links_rejects_duplicate_account_id():
    async with AsyncSessionLocal() as session:
        await upsert_account_links(session, discord_id=DISCORD_ID_A, username="test_user_a", leetcode_id="neal_wu")

    async with AsyncSessionLocal() as session:
        with pytest.raises(AccountIDAlreadyLinkedError) as exc_info:
            await upsert_account_links(session, discord_id=DISCORD_ID_B, username="test_user_b", leetcode_id="neal_wu")

    assert exc_info.value.conflicts == {"leetcode_id": "neal_wu"}
