from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Ingredient, Recipe


async def get_recipes(db: AsyncSession) -> list[Recipe]:
    # Сортировка: сначала по убыванию просмотров, затем по возрастанию времени приготовления
    result = await db.execute(
        select(Recipe)
        .order_by(Recipe.views.desc(), Recipe.cooking_time.asc())
    )
    return result.scalars().all()

async def get_recipe(db: AsyncSession, recipe_id: int) -> Recipe | None:
    result = await db.execute(
        select(Recipe)
        .where(Recipe.id == recipe_id)
        .options(selectinload(Recipe.ingredients))
    )
    return result.scalars().first()

async def increment_views(db: AsyncSession, recipe: Recipe) -> None:
    recipe.views += 1
    await db.commit()
    await db.refresh(recipe)

async def create_recipe(db: AsyncSession, data: dict) -> Recipe:
    # Извлекаем список названий ингредиентов, остальное – поля рецепта
    ingredient_names = data.pop("ingredients")
    recipe = Recipe(**data)
    # Находим или создаём ингредиенты
    for name in ingredient_names:
        result = await db.execute(select(Ingredient).where(Ingredient.name == name))
        ingredient = result.scalars().first()
        if not ingredient:
            ingredient = Ingredient(name=name)
            db.add(ingredient)
            await db.flush()  # чтобы получить id
        recipe.ingredients.append(ingredient)
    db.add(recipe)
    await db.commit()
    await db.refresh(recipe)
    return recipe
