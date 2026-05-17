import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database import Base, get_db
from main import app

# Асинхронный SQLite в памяти для тестов
TEST_DATABASE_URL = "sqlite+aiosqlite://"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSession = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestAsyncSession() as session:
        yield session

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Создаёт таблицы перед тестами и удаляет после."""
    async def _create():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(_create())

    app.dependency_overrides[get_db] = override_get_db

    yield

    async def _drop():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    asyncio.run(_drop())

client = TestClient(app)

def test_create_recipe():
    response = client.post("/recipes", json={
        "name": "Яичница",
        "cooking_time": 10,
        "description": "Вкусная глазунья",
        "ingredients": ["Яйца", "Масло"]
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Яичница"
    assert data["ingredients"][0]["name"] == "Яйца"
    assert data["views"] == 0

def test_list_recipes():
    response = client.get("/recipes")
    assert response.status_code == 200
    recipes = response.json()
    assert len(recipes) >= 1
    assert "id" in recipes[0]

def test_get_detail_increases_views():
    resp = client.post("/recipes", json={
        "name": "Омлет",
        "cooking_time": 5,
        "ingredients": ["Яйца", "Молоко"]
    })
    recipe_id = resp.json()["id"]

    detail1 = client.get(f"/recipes/{recipe_id}")
    assert detail1.status_code == 200
    assert detail1.json()["views"] == 1

    detail2 = client.get(f"/recipes/{recipe_id}")
    assert detail2.json()["views"] == 2

def test_404():
    response = client.get("/recipes/99999")
    assert response.status_code == 404
