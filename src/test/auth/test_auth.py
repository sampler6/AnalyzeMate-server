from test.settings_test import check_time

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

    base_register_data = {
        "birthdate": "2024-04-06T16:09:20.161173Z",
        "patronymic": "a",
        "surname": "b",
        "name": "f",
        "balance": 0,
        "config": {"test": "test"},
    }

    async def register_with_validation_error(
        self, client_without_auth: AsyncClient, password: str, validation_error_text: str
    ) -> None:
        data = {
            "email": f"{self.faker.word()}@example.com",
            "password": password,
        } | self.base_register_data
        response = await client_without_auth.post("auth/register", json=data)
        assert response.status_code == 422
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert response_data["detail"][0]["msg"] == "Assertion failed, " + validation_error_text

    @check_time(300)
    async def test_register(self, client_without_auth: AsyncClient) -> None:
        data = {"email": self.email, "password": self.password} | self.base_register_data
        response = await client_without_auth.post("auth/register", json=data)
        assert response.status_code == 201, response.text
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert UserRead.model_validate(response_data)

    @pytest.mark.depends(on="test_register")
    @check_time(600)
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

    @check_time(300)
    async def test_register_with_short_password(self, client_without_auth: AsyncClient) -> None:
        # генерация пароля из меньше чем 8 символов, но с большими буквами и числом
        password = str(self.faker.word()).capitalize()
        if len(password) >= 6:
            password = password[0:5]
        password += "1"

        await self.register_with_validation_error(
            client_without_auth, password, "Password must have 8 or greater symbols"
        )

    @check_time(300)
    async def test_register_with_password_without_upper_letter(self, client_without_auth: AsyncClient) -> None:
        # генерация пароля из 8 символов с числом, но без больших букв
        password = str(self.faker.word()).lower()
        password += str(self.faker.random.randint(0, 9))
        while len(password) < 8:
            password += str(self.faker.random.randint(0, 9))

        await self.register_with_validation_error(client_without_auth, password, "Password must have capital letter")

    @check_time(300)
    async def test_register_with_password_without_numeric_symbol(self, client_without_auth: AsyncClient) -> None:
        # генерация пароля из 8 символов с большой буквой, но без числа
        password = str(self.faker.word()).capitalize()
        while len(password) < 8:
            password += str(self.faker.word())

        await self.register_with_validation_error(client_without_auth, password, "Password must have numeric symbol")

    @check_time(300)
    async def test_auth_with_wrong_credentials(self, client_without_auth: AsyncClient) -> None:
        response = await client_without_auth.post(
            "auth/login", json={"username": f"{self.faker.word()}@example.com", "password": self.password}
        )
        assert response.status_code == 422

    @pytest.mark.depends(on="test_register")
    @check_time(300)
    async def test_auth_with_wrong_password(self, client_without_auth: AsyncClient) -> None:
        response = await client_without_auth.post(
            "auth/login", json={"username": self.email, "password": self.password + "wrong"}
        )
        assert response.status_code == 422
