# ChatGPT Linux Client v0.1b (Alpha Release)

Это простой клиент для общения с ChatGPT, написанный на Python с GUI на CustomTkinter.  
Проект создан для удобной работы с OpenAI API и локальным хранением истории диалогов.

This is a simple client for communicating with ChatGPT, written in Python with a GUI using CustomTkinter.  
The project is designed for easy use of the OpenAI API and local storage of chat history.

## Особенности / Features

- Графический интерфейс на CustomTkinter / GUI built with CustomTkinter  
- Локальное хранение истории в SQLite / Local storage of chat history in SQLite  
- Поддержка работы с виртуальным окружением и настройками через `.env` / Support for virtual environments and configuration via `.env` files  
- Альфа-версия — всё ещё в разработке! / Alpha version — still under development!

## Требования / Requirements

- Python 3.12.3  
- Установленные библиотеки из `requirements.txt` / Installed libraries from `requirements.txt`

## Установка / Installation

1. Клонируйте репозиторий / Clone the repository:
      ```bash
      git clone https://github.com/lFiZiXl/chatgpt-linux-client-alpha.git
      cd chatgpt-linux-client-alpha

2. Создайте и активируйте виртуальное окружение / Create and activate a virtual environment:
      ```bash
      python -m venv venv
      source venv/bin/activate  # Linux/macOS
      venv\Scripts\activate     # Windows

4. Установите зависимости / Install dependencies:
      ```bash
      pip install -r requirements.txt

6. Создайте файл .env по образцу .env.example и заполните ключ API OpenAI / Create a .env file based on .env.example and fill in your OpenAI API key.

7. Запуск / Running:
      ```bash
      python main.py

Спасибо за интерес к проекту! Если хочешь помочь — открывай issues и pull requests.
Thank you for your interest in the project! If you want to contribute — feel free to open issues and pull requests.
