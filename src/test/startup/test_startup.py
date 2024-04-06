from httpx import AsyncClient


class TestStartup:
    async def test_check_startup(self, client: AsyncClient) -> None:
        response = await client.get("check_startup/")
        assert response.status_code == 200
        resp_json = response.json()
        assert isinstance(resp_json, dict)
        assert resp_json["description"] == "Application startup successfully completed"
