import pytest
from auth.schemas.user import UserRead
from faker import Faker
from httpx import AsyncClient


class TestAuth:
    faker: Faker = Faker()
    # генерация случайной почты
    email = f"{faker.word()}@example.com"
    # Генерация случайной пароля
    password: str = str(faker.word()).capitalize()
    password += str(faker.random.randint(0, 9))
    while len(password) < 10:
        password += str(faker.random.randint(0, 9))

    async def test_register(self, client_without_auth: AsyncClient) -> None:
        data = {
            "email": self.email,
            "password": self.password,
            "birthdate": "2024-04-06T16:09:20.161173Z",
            "patronymic": "a",
            "surname": "b",
            "name": "f",
            "balance": 0,
            "config": {"test": "test"},
        }
        response = await client_without_auth.post("auth/register", json=data)
        assert response.status_code == 201, response.text
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert UserRead.model_validate(response_data)

    @pytest.mark.depends(on="test_register")
    async def test_auth(self, client_without_auth: AsyncClient) -> None:
        data = {"username": self.email, "password": self.password}
        response = await client_without_auth.post("auth/login", data=data)
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert "access_token" in response_data
        token = response_data["access_token"]

        response = await client_without_auth.get("users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert UserRead.model_validate(response_data)
