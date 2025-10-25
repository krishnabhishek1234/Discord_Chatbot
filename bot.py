# bot.py
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from google import generativeai as genai
from database import SessionLocal, engine, Base
from models import User, Chat

# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Configure Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------------
# Event: Bot is ready
# -----------------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# -----------------------------
# Event: On message (mention trigger)
# -----------------------------
@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if bot was mentioned
    if bot.user.mentioned_in(message):
        # Extract the question after the mention
        question = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if not question:
            await message.channel.send("💡 Please ask a question after mentioning me!")
            return

        # Database session
        db = SessionLocal()

        # Find or create user
        user = db.query(User).filter_by(discord_id=str(message.author.id)).first()
        if not user:
            user = User(discord_id=str(message.author.id), username=str(message.author))
            db.add(user)
            db.commit()
            db.refresh(user)

        # Fetch last 5 chats for memory
        recent_chats = (
            db.query(Chat)
            .filter(Chat.user_id == user.id)
            .order_by(Chat.timestamp.desc())
            .limit(5)
            .all()
        )

        # Build conversation context
        history = ""
        for chat in reversed(recent_chats):
            history += f"User: {chat.message}\nBot: {chat.response}\n"

        prompt = (
            f"The following is a conversation between a helpful AI bot and a Discord user.\n"
            f"Conversation so far:\n{history}\n"
            f"User: {question}\nBot:"
        )

        # Generate response from Gemini
        try:
            response = model.generate_content(prompt)
            answer = response.text
        except Exception as e:
            answer = "⚠️ Sorry, I couldn't process that request."
            print("Gemini Error:", e)

        # Save new chat
        chat = Chat(user_id=user.id, message=question, response=answer)
        db.add(chat)
        db.commit()
        db.close()

        # Send answer
        await message.channel.send(answer)

    # Process other commands (like !forget)
    await bot.process_commands(message)

# -----------------------------
# Command: Forget history
# -----------------------------
@bot.command()
async def forget(ctx):
    """Forget previous conversation history."""
    db = SessionLocal()
    user = db.query(User).filter_by(discord_id=str(ctx.author.id)).first()
    if user:
        db.query(Chat).filter(Chat.user_id == user.id).delete()
        db.commit()
        await ctx.send("🧹 Your chat history has been cleared!")
    else:
        await ctx.send("No previous history found.")
    db.close()

# -----------------------------
# Run the bot
# -----------------------------
bot.run(DISCORD_TOKEN)
