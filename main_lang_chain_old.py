import json
import os
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.schema import SystemMessage
from dotenv import load_dotenv

# Устанавливаем прокси
proxy_url = "https://admin:kZMkiZusUuq7@recipes.webredirect.org"
os.environ["HTTP_PROXY"] = proxy_url
os.environ["HTTPS_PROXY"] = proxy_url

# Загружаем переменные окружения из .env файла
load_dotenv('.env')

# Настройка API ключа для OpenAI
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

# Настройка модели ChatGPT
llm = ChatOpenAI(model="gpt-4o-mini-2024-07-18", openai_api_key=LANGCHAIN_API_KEY)

# Настройка памяти
memory = ConversationBufferMemory(return_messages=True)

# Инициализация цепочки общения с памятью

system_prompt = """Ты — помощник по кулинарии. Тебе нужно извлечь ингредиенты и запрещенные продукты из текста пользователя и вернуть их в структурированном формате JSON. Вот как должен выглядеть формат ответа:

{
  "ingredients": [
    "<ингредиент_1>",
    "<ингредиент_2>",
    "<ингредиент_3>",
    ...
  ],
  "dislikedFood": [
    "<запрещенный_продукт_1>",
    "<запрещенный_продукт_2>",
    ...
  ]
}

Если в тексте пользователя указаны ингредиенты или запрещенные продукты, извлеки их и добавь в соответствующие списки. Если каких-то ингредиентов нет, верни пустой список для этой категории. Ответ должен быть только в формате JSON, без пояснений и дополнительных данных.
"""

system_string = """
Ты — помощник по кулинарии. Тебе нужно отфильтровать рецепты, которые не соответствуют запросу пользователя. Пожалуйста, ответь в следующем формате JSON:

{
  "filtered_recipes": [
    {
      "title": "<название_рецепта>",
      "link": "<ссылка_на_рецепт>",
      "ingredients": [
        "<ингредиент_1>",
        "<ингредиент_2>",
        "<ингредиент_3>",
        ...
      ]
    },
    ...
  ]
}

Вот как это работает:
1. Получаем список рецептов и ингредиентов, которые есть в каждом рецепте.
2. Применяем фильтры, чтобы исключить рецепты, содержащие запрещенные ингредиенты или не соответствующие предпочтениям пользователя.

Например, если список рецептов следующий:
[
  {"title": "Картофельный суп", "ingredients": ["картошка", "морковь", "лук", "соль"], "link": "https://example.com/potato-soup"},
  {"title": "Омлет с молоком", "ingredients": ["молоко", "яйца", "соль", "перец"], "link": "https://example.com/omelette"},
  {"title": "Шоколадный торт", "ingredients": ["шоколад", "мука", "яйца", "сахар"], "link": "https://example.com/chocolate-cake"}
]

Если пользователь не хочет шоколад и предпочитает блюда с молоком и яйцами, то ответ должен быть таким:

{
  "filtered_recipes": [
    {
      "title": "Омлет с молоком",
      "link": "https://example.com/omelette",
      "ingredients": [
        "молоко",
        "яйца",
        "соль",
        "перец"
      ]
    }
  ]
}

Пожалуйста, ответь только в формате JSON, как показано выше. Не добавляй никаких пояснений или других данных.
"""


memory.chat_memory.messages.append(SystemMessage(content=system_prompt))

conversation_chain = ConversationChain(llm=llm, memory=memory, verbose=True)

class RecipeBot:
    def __init__(self):
        self.llm = llm
        self.memory = memory
        self.conversation_chain = conversation_chain

    def _send_to_chatgpt(self, user_input):
        """Отправляем запрос в ChatGPT для получения структурированного ответа."""
        response = self.conversation_chain.predict(input=user_input)
        return response

    def _extract_ingredients_from_response(self, user_input):
        """Извлекаем ингредиенты и запрещенные ингредиенты из ответа ChatGPT."""
        chatgpt_response = self._send_to_chatgpt(user_input)
        try:
            # Попробуем извлечь JSON с ингредиентами и запрещенными продуктами из ответа
            response_json = json.loads(chatgpt_response)
            ingredients = response_json.get("ingredients", [])
            forbidden = response_json.get("dislikedFood", [])
            print('ingredients: ', ingredients) 
            print('forbidden_ingredients: ', forbidden) 
            return ingredients, forbidden
        except json.JSONDecodeError:
            print('_extract_ingredients_from_response Error') 
            return [], []

    def _send_to_faiss(self, ingredients):
        """Заглушка для отправки запроса в FAISS, возвращаем фейковые рецепты."""
        fake_recipes = [
            {"title": "Картофельный суп", "ingredients": ["картошка", "морковь", "лук", "соль"], "link": "https://example.com/potato-soup"},
            {"title": "Омлет с молоком", "ingredients": ["молоко", "яйца", "соль", "перец"], "link": "https://example.com/omelette"},
            {"title": "Шоколадный торт", "ingredients": ["шоколад", "мука", "яйца", "сахар"], "link": "https://example.com/chocolate-cake"},
            {"title": "Молочный коктейль", "ingredients": ["молоко", "банан", "сахар", "морозное молоко"], "link": "https://example.com/milkshake"},
            {"title": "Печенье с яйцом", "ingredients": ["яйца", "мука", "сахар", "масло"], "link": "https://example.com/cookies"},
            {"title": "Запеканка с картошкой", "ingredients": ["картошка", "молоко", "яйца", "соль"], "link": "https://example.com/casserole"},
            {"title": "Курица с картошкой", "ingredients": ["курица", "картошка", "соль", "перец"], "link": "https://example.com/chicken-potatoes"},
            {"title": "Молочная каша", "ingredients": ["молоко", "овсянка", "сахар"], "link": "https://example.com/porridge"},
            {"title": "Овощной салат", "ingredients": ["помидор", "огурец", "морковь", "соль"], "link": "https://example.com/salad"},
            {"title": "Шоколадные блины", "ingredients": ["мука", "шоколад", "яйца", "сахар"], "link": "https://example.com/pancakes"}
        ]
        return fake_recipes

    def _filter_recipes_by_user_request(self, user_input, recipes):
        """Фильтруем рецепты, проверяя их на соответствие запросу пользователя."""
        # Извлекаем ингредиенты и запрещенные продукты из первого запроса пользователя
        ingredients, forbidden_ingredients = self._extract_ingredients_from_response(user_input)

        # Формируем запрос для ChatGPT, чтобы проверить все рецепты за один раз
        recipes_str = ""
        for recipe in recipes:
            #ingredients_str = ", ".join(recipe['ingredients'])
            recipes_str += f"Рецепт: {recipe['title']}. Ингредиенты: {recipe['ingredients']}. Ссылка: {recipe['link']}. \n"
        
        # Формируем полный запрос для ChatGPT
        check_input = f"Пользователь сказал: '{user_input}'. Проверь, пожалуйста, подходит ли каждый рецепт из списка, учитывая, что пользователь не хочет использовать ингредиенты: {', '.join(forbidden_ingredients)}. Вот список рецептов: {recipes_str}"

        # Отправляем запрос в ChatGPT для анализа
        response = self._send_to_chatgpt(system_string + check_input)

        # Формируем список подходящих рецептов из ответа ChatGPT
        filtered_recipes = []
        if response:
            try:
                response_json = json.loads(response)
                filtered_recipes = response_json.get("filtered_recipes", [])
            except json.JSONDecodeError:
                print("Error parsing response.")
        else:
            print("Error with ChatGPT response")

        return filtered_recipes

    def handle_request(self, user_input):
        """Основной метод для обработки запроса пользователя."""
        # Сначала извлекаем все ингредиенты и запрещенные ингредиенты
        ingredients, forbidden_ingredients = self._extract_ingredients_from_response(user_input)

        # Заглушка для FAISS
        recipes = self._send_to_faiss(ingredients)

        # Фильтруем рецепты, проверяя их на соответствие
        filtered_recipes = self._filter_recipes_by_user_request(user_input, recipes)

        return filtered_recipes

# Пример использования
if __name__ == "__main__":
    bot = RecipeBot()

    user_input = "у меня есть пол литра молока, мука и куриные яйца. Не хочу есть шоколад."
    filtered_recipes = bot.handle_request(user_input)
    
    print("Рекомендации по рецептам:")
    for recipe in filtered_recipes:
        print(f"{recipe['title']}: {recipe['link']}")