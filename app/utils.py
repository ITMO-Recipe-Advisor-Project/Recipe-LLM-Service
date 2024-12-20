from typing import List, Dict


def generate_user_response(recipes: List[str]) -> Dict[str, List[str]]:
    response = {"message": "Here are the recipes I've found for you:", "recipes": recipes}

    if not response.get("recipes"):
        response["message"] = "Unfortunately, we couldn't find any matching recipes. Please try modifying your query."

    return response
