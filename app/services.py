import openai
from typing import List
from fastapi import HTTPException
import logging
import httpx
from pydantic import BaseModel
from app.config import get_config
import json


class RecipeResponse(BaseModel):
    title: str
    link: str


config = get_config()
openai.api_key = config["OPENAI_API_KEY"]
openai.proxy = config["PROXY"]


async def filter_products_with_gpt(query: str) -> tuple[None, None] | tuple[str, str]:
    try:
        logging.info(f"Sending query to OPENAI MODEL: {query}")

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant who extracts ingredients from recipe-related queries.",
                },
                {
                    "role": "user",
                    "content": f"Determine the list of necessary ingredients if there is at least one ingredient in the following query: "
                    f"'{query}'. Output a JSON object with three fields: status, ingredients, and original_query. "
                    f"The status field contains the value 'valid' if the query is related to asking for a recipe "
                    f"with ingredients input, and 'invalid' if the query is not related. The ingredients field "
                    f"contains a list of ingredients from the query; if there are no ingredients, this field must be an empty list. "
                    f"The original_query field contains the string of the original query.",
                },
            ],
            response_format={"type": "json_object"},
            max_tokens=1000,
        )

        try:
            result = json.loads(response["choices"][0]["message"]["content"])
        except json.JSONDecodeError as e:
            logging.info(f"Failed to decode JSON: {e}")
            return None, None

        logging.info(f"GPT response status: {result.get('status', 'invalid')}")
        logging.info(f"GPT response: {result.get('ingredients', [])}")

        if not result.get("status", "invalid"):
            return None, None

        necessary_ingredients = ", ".join(result["ingredients"])
        original_query = result["original_query"]

        return necessary_ingredients, original_query
    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")


async def filter_recipes_based_on_original_query(original_query: list, recipes: List[dict]) -> List[str]:
    try:
        logging.info(f"Filtering recipes with GPT based on original query: {original_query}")
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant who identifies valid recipes based on user query."},
                {
                    "role": "user",
                    "content": f"You have a list of recipes, each containing ingredients: {recipes}. "
                    f"You also have a query: '{original_query}' to which the recipes in the list "
                    f"must fully or very closely correspond. Exclude recipes that do not match "
                    f"this criterion from the list, and output a JSON object with a field 'recipes' "
                    f"that contains the modified list. If the list is empty after filtering, the 'recipes' field "
                    f"must contain an empty list.",
                },
            ],
            response_format={"type": "json_object"},
            max_tokens=10000,
        )

        try:
            result = json.loads(response["choices"][0]["message"]["content"])
        except json.JSONDecodeError as e:
            logging.info(f"Failed to decode JSON: {e}")
            return []

        recipes = [f"{recipe['title']}:\n{recipe['link']}" for recipe in result.get("recipes", [])]

        logging.info(f"Resulting recipes: {recipes}")

        return recipes

    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")


async def get_recipes_from_service(ingredients: List[str]):
    url = "http://recipe-search-service:8000/recipes/search/"

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(url, json={"query": ingredients})
            if response.status_code == 404:
                return None

            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Service error: {e}")
