from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_db, engine, Base
from schemas import RecipeListOut, RecipeDetailOut, RecipeCreate
from crud import get_recipes, get_recipe, increment_views, create_recipe

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Действия при старте приложения
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield  # приложение работает
    # Здесь можно добавить очистку ресурсов при завершении, если нужно

app = FastAPI(
    title="Кулинарная книга",
    description="API для управления рецептами. Позволяет просматривать список рецептов, "
                "открывать детали, создавать новые.",
    version="1.0.0",
    lifespan=lifespan,
)

# Далее маршруты без изменений...
@app.get("/recipes", response_model=List[RecipeListOut])
async def list_recipes(db: AsyncSession = Depends(get_db)):
    recipes = await get_recipes(db)
    return recipes

@app.get("/recipes/{recipe_id}", response_model=RecipeDetailOut)
async def recipe_detail(recipe_id: int, db: AsyncSession = Depends(get_db)):
    recipe = await get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")
    await increment_views(db, recipe)
    return recipe

@app.post("/recipes", response_model=RecipeDetailOut, status_code=201)
async def add_recipe(recipe_data: RecipeCreate, db: AsyncSession = Depends(get_db)):
    data = recipe_data.model_dump()
    recipe = await create_recipe(db, data)
    return recipe