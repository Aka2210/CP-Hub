import httpx


class AtCoderService:
    def __init__(self):
        self.profile_url_template = "https://atcoder.jp/users/{username}"
        self.history_url_template = "https://atcoder.jp/users/{username}/history/json"

    async def user_exists(self, username: str) -> bool:
        """Checks whether an AtCoder account with the given username exists."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.profile_url_template.format(username=username), timeout=10.0)
                return response.status_code == 200

            except httpx.RequestError as exc:
                raise RuntimeError(f"Error occurred while checking AtCoder user: {exc}")

    async def get_rating(self, username: str) -> int | None:
        """Fetches the current rating for the given AtCoder username."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.history_url_template.format(username=username), timeout=10.0)

                if response.status_code != 200:
                    raise httpx.HTTPStatusError(
                        f"AtCoder server returned error: {response.status_code}",
                        request=response.request,
                        response=response,
                    )

                history = response.json()

                if not history:
                    return None

                return history[-1]["NewRating"]

            except httpx.RequestError as exc:
                raise RuntimeError(f"Error occurred while fetching AtCoder rating: {exc}")
