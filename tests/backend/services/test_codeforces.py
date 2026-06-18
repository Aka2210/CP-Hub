import pytest

from backend.app.services.codeforces.client import CodeforcesService


@pytest.fixture
def codeforces_service():
    return CodeforcesService()


@pytest.mark.asyncio
async def test_user_exists_for_real_user(codeforces_service):
    assert await codeforces_service.user_exists("tourist") is True


@pytest.mark.asyncio
async def test_user_exists_for_nonexistent_user(codeforces_service):
    assert await codeforces_service.user_exists("this-handle-does-not-exist-12345") is False


@pytest.mark.asyncio
async def test_get_rating_for_real_user(codeforces_service):
    rating = await codeforces_service.get_rating("tourist")

    assert isinstance(rating, int)
    assert rating > 0


@pytest.mark.asyncio
async def test_get_rating_for_nonexistent_user(codeforces_service):
    rating = await codeforces_service.get_rating("this-handle-does-not-exist-12345")

    assert rating is None


@pytest.mark.asyncio
async def test_get_solved_count_for_real_user(codeforces_service):
    solved = await codeforces_service.get_solved_count("tourist")

    assert isinstance(solved, int)
    assert solved > 0


@pytest.mark.asyncio
async def test_get_solved_count_for_nonexistent_user(codeforces_service):
    solved = await codeforces_service.get_solved_count("this-handle-does-not-exist-12345")

    assert solved is None
