import ast
from typing import List


def generate_user_response(recipes: List[dict]) -> str:
    if not recipes:
        return "Unfortunately, we couldn't find any suitable recipes. Please try modifying your query."
    response = "Here are the recipes we found for you:\n"
    recipes = ast.literal_eval(recipes)
    for recipe in recipes:
        response += f"- {recipe['title']}: {recipe['link']}\n"
    return response
