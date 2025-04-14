from typing import Optional
from fastapi import FastAPI,Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import Column, create_engine, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "mysql+pymysql://tobisawa/yuki0108@database-1.c14yeqwm8prw.ap-southeast-2.rds.amazonaws.com:3306/recipe_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class RecipeTable(Base):
  __tablename__ = "recipe"
  id = Column(Integer, primary_key=True, index=True)
  title = Column(String(100))
  making_time = Column(String(100))
  serves = Column(String(100))
  ingredients = Column(String(300))
  cost = Column(Integer)
  created_at = Column(DateTime, default=datetime.now)
  updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Recipe(BaseModel):
  title: str
  making_time: str
  serves: str
  ingredients: str
  cost: int

class UpdateRecipe(BaseModel):
  title: Optional[str] = None
  making_time: Optional[str] = None
  serves: Optional[str] = None
  ingredients: Optional[str] = None
  cost: Optional[int] = None


app = FastAPI()

@app.post("/recipes")
async def post_recipes(recipe: Recipe):
  try:
    with SessionLocal() as session:
      new_recipe = RecipeTable(
        title = recipe.title,
        making_time = recipe.making_time,
        serves = recipe.serves,
        ingredients = recipe.ingredients,
        cost = recipe.cost,
        created_at = datetime.now(),
        updated_at = datetime.now()
      )
      session.add(new_recipe)
      session.commit()
      return{
        "message": "Recipe successfully created!",
        "recipe": [
          {
            "id": new_recipe.id,
            "title": new_recipe.title,
            "making_time": new_recipe.making_time,
            "serves": new_recipe.serves,
            "ingredients": new_recipe.ingredients,
            "cost": new_recipe.cost
          }
        ]
      }
  except Exception:
    return{
      "message": "Recipe creation failed!",
      "required": "title, making_time, serves, indegredients, cost"
    }


@app.get("/recipes")
async def get_all_recipe():
  try:
    with SessionLocal() as session:
      recipes = session.query(RecipeTable).all()
      all_recipes =[
        {
          "id": i.id,
          "title": i.title,
          "making_time": i.making_time,
          "serves": i.serves,
          "ingredients": i.ingredients,
          "cost": i.cost
        }
        for i in recipes
      ]
      return{
        "recipes": all_recipes
      }
  except Exception:
    return{
    "message": "Getting all recipes failed!"
  }

@app.get("/recipes/{id}")
async def get_one_recipe(id: int):
  try:
    with SessionLocal() as session:
      recipe = session.query(RecipeTable).filter(RecipeTable.id ==id).first()
      if recipe:
        return{
          "message": "Recipe details by id",
          "recipe": [
            {
              "id": recipe.id,
              "title": recipe.title,
              "making_time": recipe.making_time,
              "serves": recipe.serves,
              "ingredients": recipe.ingredients,
              "cost": recipe.cost
            }
          ]
        }
      else:
        return{
          "message": "Not Recipe found"
        }
  
  except Exception:
    return{
      "message": "Getting Recipe failed!"
    }

@app.patch("/recipes/{id}")
async def update_recipe(id: int, update_recipe: UpdateRecipe):
  try:
    with SessionLocal() as session:
      recipe = session.query(RecipeTable).filter(RecipeTable.id == id).first()
      if recipe:
        if update_recipe.title:
          recipe.title = update_recipe.title

        if update_recipe.making_time:
          recipe.making_time = update_recipe.making_time

        if update_recipe.serves:
          recipe.serves = update_recipe.serves

        if update_recipe.ingredients:
          recipe.ingredients = update_recipe.ingredients

        if update_recipe.cost:
          recipe.cost = update_recipe.cost
        
        recipe.updated_at = datetime.now()

        session.commit()

      else:
        return{
          "message": "No Recipe found"
        }

      return{
        "message": "Recipe successfully updated!",
        "recipe": [
          {
            "title": recipe.title,
            "making_time": recipe.making_time,
            "serves": recipe.serves,
            "ingredients": recipe.ingredients,
            "cost": recipe.cost
          }
        ]
      }
      
  except Exception:
    return{
      "message": "Updating recipe failed!"
    }

@app.delete("/recipes/{id}")
async def delete_recipe(id: int):
  try:
    with SessionLocal() as session:
      recipe = session.query(RecipeTable).filter(RecipeTable.id == id).first()
      if recipe:
        session.delete(recipe)
        session.commit()
        return{
          "message": "Recipe successfully removed!" 
        }
      else:
        return{
          "message": "No Recipe found!" 
        }
  except Exception:
    return{
      "message": "Removing Recipe failed!" 
    }

@app.exception_handler(HTTPException)
async def internal_server_error(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"message": "Not Found"}
    )