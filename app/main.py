from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ValidationError
import logging
from services import get_recipes_from_service, filter_products_with_gpt, filter_recipes_based_on_exclusions
from utils import generate_user_response

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

    necessary_ingredients, excluded_ingredients = await filter_products_with_gpt(user_data.query)
    if necessary_ingredients is None:
        return {"message": "Your query is not related to recipes. Please clarify your request."}

    recipes = await get_recipes_from_service(necessary_ingredients)
    if not recipes:
        return {"message": "Unfortunately, nothing was found. Please try modifying your query."}

    filtered_recipes = await filter_recipes_based_on_exclusions(excluded_ingredients, recipes)

    response_message = generate_user_response(filtered_recipes)
    return {"message": response_message}
