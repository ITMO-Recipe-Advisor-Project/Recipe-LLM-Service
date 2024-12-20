from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ValidationError
import logging
from app.services import get_recipes_from_service, filter_products_with_gpt, filter_recipes_based_on_original_query
from app.utils import generate_user_response
from app.exceptions import InvalidLanguageException

logging.basicConfig(level=logging.INFO)

app = FastAPI()


class UserRequest(BaseModel):
    query: str


class RecipeResponse(BaseModel):
    title: str
    link: str


@app.post("/process")
async def process_user_request(request: Request):
    try:
        user_request = await request.json()
        user_data = UserRequest(**user_request)
    except (ValidationError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid request format.")

    try:
        necessary_ingredients, original_query = await filter_products_with_gpt(user_data.query)
        if not necessary_ingredients:
            return {"message": "Your query is not related to recipes. Please clarify your request."}
    except InvalidLanguageException as _:
        return {"message": "Sorry, but I only understand English. Please try making a new request in English."}

    recipes = await get_recipes_from_service(necessary_ingredients)
    if not recipes:
        return {"message": "Unfortunately, nothing was found. Please try modifying your query."}

    filtered_recipes = await filter_recipes_based_on_original_query(original_query, recipes)

    return generate_user_response(filtered_recipes)
