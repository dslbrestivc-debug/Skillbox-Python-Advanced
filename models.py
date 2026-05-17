from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from database import Base

recipe_ingredient = Table(
    "recipe_ingredient",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True),
)

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cooking_time = Column(Integer, nullable=False)  # минуты
    views = Column(Integer, default=0)
    description = Column(Text, default="")

    ingredients = relationship(
        "Ingredient",
        secondary=recipe_ingredient,
        back_populates="recipes",
        lazy="selectin",  # подгружаем ингредиенты в одном запросе
    )

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    recipes = relationship(
        "Recipe",
        secondary=recipe_ingredient,
        back_populates="ingredients",
        lazy="selectin",
    )
