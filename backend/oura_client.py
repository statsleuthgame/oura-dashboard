import httpx
from fastapi import HTTPException


class OuraClient:
    def __init__(self, token: str, base_url: str = "https://api.ouraring.com"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0,
        )

    async def fetch(self, endpoint: str, start_date: str, end_date: str) -> list[dict]:
        results = []
        url = f"{self.base_url}{endpoint}"
        params = {"start_date": start_date, "end_date": end_date}

        while True:
            resp = await self.client.get(url, params=params)

            if resp.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid Oura API token")
            if resp.status_code == 429:
                raise HTTPException(status_code=429, detail="Oura API rate limit exceeded")
            if resp.status_code >= 400:
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=f"Oura API error: {resp.text}",
                )

            body = resp.json()
            results.extend(body.get("data", []))

            next_token = body.get("next_token")
            if not next_token:
                break
            params = {"next_token": next_token}

        return results

    async def close(self):
        await self.client.aclose()
