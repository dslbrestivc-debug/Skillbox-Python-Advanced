from typing import List

from pydantic import BaseModel, Field


# ---- Ингредиент ----
class IngredientBase(BaseModel):
    name: str = Field(..., example="Мука")

class IngredientCreate(IngredientBase):
    pass

class IngredientOut(IngredientBase):
    id: int

    class Config:
        from_attributes = True

# ---- Рецепт ----
class RecipeBase(BaseModel):
    name: str = Field(..., example="Овсяная каша")
    cooking_time: int = Field(..., gt=0, example=15)
    description: str = Field(default="", example="Простое и полезное блюдо")

class RecipeCreate(RecipeBase):
    ingredients: List[str] = Field(
        ..., example=["Овсяные хлопья", "Молоко", "Вода", "Соль"]
    )

class RecipeListOut(BaseModel):
    """Поля для экрана со списком рецептов"""
    id: int
    name: str
    views: int
    cooking_time: int

    class Config:
        from_attributes = True

class RecipeDetailOut(RecipeBase):
    """Детальная информация о рецепте"""
    id: int
    views: int
    ingredients: List[IngredientOut]

    class Config:
        from_attributes = True
