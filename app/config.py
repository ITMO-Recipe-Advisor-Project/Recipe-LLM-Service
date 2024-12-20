from dotenv import dotenv_values


def get_config():
    """
    Loads configuration values from a `.env` file.

    :return: A dictionary containing:
             - OPENAI_API_KEY: API key for OpenAI authentication.
             - PROXY: Proxy settings for network requests (if applicable).
    """
    env_vars = dotenv_values("env/.env")
    return {
        "OPENAI_API_KEY": env_vars["OPENAI_API_KEY"],
        "PROXY": env_vars["PROXY"],
    }
