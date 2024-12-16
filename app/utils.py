import json
import ast
from typing import List, Dict


def generate_user_response(recipes: str) -> Dict[str, List[str]]:
    response = {"message": "", "recipes": []}

    try:
        recipes_list = json.loads(recipes)
    except json.JSONDecodeError:
        try:
            recipes_list = ast.literal_eval(recipes)
        except (ValueError, SyntaxError):
            response["message"] = "Invalid input format. Please check your query."
            return response

    if not recipes_list:
        response["message"] = "Unfortunately, we couldn't find any suitable recipes. Please try modifying your query."
        return response

    response["message"] = "Here are the recipes we found for you:"
    for recipe in recipes_list:
        try:
            response['recipes'].append(f"{recipe['title']}:\n{recipe['link']}")
        except KeyError:
            response['recipes'].append("Invalid recipe structure. Missing 'title' or 'link'.")

    return response
