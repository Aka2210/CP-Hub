import httpx


class CodeforcesService:
    def __init__(self):
        self.api_url = "https://codeforces.com/api/user.info"

    async def user_exists(self, handle: str) -> bool:
        """Checks whether a Codeforces account with the given handle exists."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.api_url, params={"handles": handle}, timeout=10.0)
                data = response.json()

                return data.get("status") == "OK"

            except httpx.RequestError as exc:
                raise RuntimeError(f"Error occurred while checking Codeforces user: {exc}")

    async def get_rating(self, handle: str) -> int | None:
        """Fetches the current rating for the given Codeforces handle."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.api_url, params={"handles": handle}, timeout=10.0)
                data = response.json()

                if data.get("status") != "OK":
                    return None

                return data["result"][0].get("rating")

            except httpx.RequestError as exc:
                raise RuntimeError(f"Error occurred while fetching Codeforces rating: {exc}")
