import openai
from typing import List
from fastapi import HTTPException
import logging
import httpx
from pydantic import BaseModel
from config import get_config


class RecipeResponse(BaseModel):
    title: str
    link: str
config = get_config()

openai.api_key = config["OPENAI_API_KEY"]

MOCKED_RECIPES = [
    {
        "title": "Chilled Strawberry Soup",
        "ingredients": [
            "2 cups frozen strawberries",
            "2 cups milk",
            "1 cup heavy cream",
            "1/2 cup sour cream",
            "2 tablespoons white sugar, or to taste"
        ],
        "link": "https://www.allrecipes.com/recipe/26393/chilled-strawberry-soup/"
    },
    {
        "title": "Perfect Strawberry Milkshake",
        "ingredients": [
            "1 cup vanilla frozen yogurt",
            "1 cup 1% milk",
            "4 large strawberries"
        ],
        "link": "https://www.allrecipes.com/recipe/221059/perfect-strawberry-milkshake/"
    },
    {
        "title": "Blueberry Fruit Smoothie",
        "ingredients": [
            "1 cup reduced-fat vanilla ice cream",
            "1 cup fresh or frozen blueberries",
            "1/2 cup chopped peeled fresh peaches or frozen unsweetened sliced peaches",
            "1/2 cup pineapple juice",
            "1/4 cup vanilla yogurt"
        ],
        "link": "https://www.tasteofhome.com/recipes/blueberry-fruit-smoothie/"
    },
    {
        "title": "Easy Chocolate Mousse with Strawberries",
        "ingredients": [
            "125 ml cream (light)",
            "150 grams dark chocolate",
            "3 egg whites",
            "12 strawberries"
        ],
        "link": "https://cookpad.com/us/recipes/363097-easy-chocolate-mousse-with-strawberries"
    }
]

async def filter_products_with_gpt(query: str) -> List[str]:
    try:
        logging.info(f"Sending query to GPT: {query}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant who extracts ingredients from recipe-related queries."},
                {"role": "user", "content": f"Determine the list of necessary ingredients and list of excluded ingredients from the following query: '{query}'.If this is not a request for a recipe,write 'Not a request for a recipe'. In response, give only one sting with lists of ingredients separated by a dot, ingredients sepatate by a comma"}
            ],
            max_tokens=50
        )
        result = response["choices"][0]["message"]["content"].strip()
        logging.info(f"GPT response: {result}")
        if result.lower().startswith("not a request for a recipe"):
            return None , None
        
        ingredient_parts = result.split(".")

        # Получаем два списка ингредиентов
        necessary_ingredients = [ingredient.strip() for ingredient in ingredient_parts[0].split(",") if ingredient.strip()]
        excluded_ingredients = [ingredient.strip() for ingredient in ingredient_parts[1].split(",") if ingredient.strip()] if len(ingredient_parts) > 1 else []

        return necessary_ingredients, excluded_ingredients
    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")

async def filter_recipes_based_on_exclusions(excluded_ingredients: list, recipes: List[dict]) -> List[RecipeResponse]:
    try:
        logging.info(f"Extracting excluded ingredients with GPT from query: {excluded_ingredients}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant who identifies ingredients to exclude from recipes based on user queries."},
                {"role": "user", "content": f"You have a list of recipes, each containing ingredients{recipes}. You also have a list of ingredients that the user wants to exclude — {excluded_ingredients}.\
                  If the exclusion list is empty, return all recipes unchanged.\
                  If the exclusion list is not empty, remove from the list of recipes those that contain any ingredient from the exclusion list.\
                  Return the remaining recipes in the same format as input, without any additional comments."}
            ],
            max_tokens=2500
        )
        result = response["choices"][0]["message"]["content"].strip()
        logging.info(f"GPT response for exclusions: {result}")

        return result

    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")


async def get_recipes_from_service(products: List[str]):
    if products:
        return MOCKED_RECIPES 

    url = "http://recipe-search-service:8000/recipes/search/"  
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"products": products})
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Service error: {e}")