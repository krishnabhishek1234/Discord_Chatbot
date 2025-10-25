# Discord AI Chatbot

A Discord chatbot powered by **Google Gemini AI** with **conversation memory** and **Neon PostgreSQL** database.  
The bot responds to mentions (`@BotName`) and keeps track of past interactions for context-aware replies.

---

## Features

- Responds to questions via **@mention** in Discord.
- Remembers the last 5 messages per user for context-aware responses.
- Stores chat history in a **PostgreSQL database** (Neon).
- Command to **forget conversation history** (`!forget`).
- Easy setup with `.env` configuration.

---

## Technologies Used

- Python 3.12+  
- [Pycord](https://docs.pycord.dev/) (Discord bot framework)  
- [Google Gemini AI](https://developers.generativeai.google/)  
- [SQLAlchemy](https://www.sqlalchemy.org/) (ORM for database)  
- [Neon PostgreSQL](https://neon.tech/) (cloud database)  
- `dotenv` for environment variable management  

---
