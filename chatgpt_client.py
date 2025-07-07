import os
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from dotenv import load_dotenv

load_dotenv()

def get_chatgpt_response(messages: list, model: str, api_key: str = None) -> str:
    """
    Отправляет список сообщений в OpenAI и возвращает ответ.
    
    :param messages: Список словарей с ролями и сообщениями (роль: 'user', 'assistant', 'system').
    :param model: Название модели.
    :param api_key: Ключ OpenAI API. Если не передан, используется из .env
    :return: Ответ ChatGPT в виде строки.
    """
    try:
        client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        response: ChatCompletion = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Ошибка при обращении к OpenAI API: {str(e)}]"