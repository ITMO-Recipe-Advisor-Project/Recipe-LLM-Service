from dotenv import dotenv_values


def get_config():
    """
    Loads configuration values from a `.env` file.

    :return: A dictionary containing:
             - RUNPOD_API_KEY: API key for RunPod authentication.
             - RUNPOD_ENDPOINT: API endpoint for RunPod.
             - DATASET: Path to the dataset file.
             - LOWER_THRESHOLD: A threshold value used in the application.
    """

    env_vars = dotenv_values("env/.env")
    return {
        "OPENAI_API_KEY": env_vars["OPENAI_API_KEY"],

    }