import pytest

from backend.app.services.atcoder.client import AtCoderService


@pytest.fixture
def atcoder_service():
    return AtCoderService()


@pytest.mark.asyncio
async def test_user_exists_for_real_user(atcoder_service):
    assert await atcoder_service.user_exists("tourist") is True


@pytest.mark.asyncio
async def test_user_exists_for_nonexistent_user(atcoder_service):
    assert await atcoder_service.user_exists("this-user-definitely-does-not-exist-12345") is False


@pytest.mark.asyncio
async def test_get_rating_for_real_user(atcoder_service):
    rating = await atcoder_service.get_rating("tourist")

    assert isinstance(rating, int)
    assert rating > 0


@pytest.mark.asyncio
async def test_get_rating_for_nonexistent_user(atcoder_service):
    rating = await atcoder_service.get_rating("this-user-definitely-does-not-exist-12345")

    assert rating is None
