import ast
from typing import List, Dict


def generate_user_response(recipes: List[dict]) -> Dict[str, List[str]]:
    response = {"message": "", "recipes": []}
    if not recipes:
        response["message"] = "Unfortunately, we couldn't find any suitable recipes. Please try modifying your query."
        return response

    response["message"] = "Here are the recipes we found for you:"
    recipes = ast.literal_eval(recipes)
    for recipe in recipes:
        response['recipes'].append(f"{recipe['title']}:\n{recipe['link']}")
    return response
