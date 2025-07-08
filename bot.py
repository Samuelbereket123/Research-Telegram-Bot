import os
import time
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler,
)
from arxiv_api import search_arxiv  # your arXiv search function

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

def source_menu():
    keyboard = [
        [InlineKeyboardButton("Semantic Scholar", callback_data='source_semantic')],
        [InlineKeyboardButton("arXiv", callback_data='source_arxiv')],
        [InlineKeyboardButton("All Sources", callback_data='source_all')],
    ]
    return InlineKeyboardMarkup(keyboard)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Welcome to Startup Research Bot!\n\n"
        "Choose a source to search from:",
        reply_markup=source_menu()
    )

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    context.user_data['source'] = query.data
    query.edit_message_text(
        text=f"✅ You selected *{query.data.replace('source_', '').title()}*.\n\n"
             "Now send me your research topic.",
        parse_mode='Markdown'
    )

def handle_query(update: Update, context: CallbackContext):
    user_query = update.message.text
    source = context.user_data.get('source', 'source_all')  # default to all sources

    update.message.reply_text(
        f"🔍 Searching for research papers on:\n\n*{user_query}*\n\nPlease wait...",
        parse_mode='Markdown'
    )

    if source in ('source_semantic', 'source_all'):
        try:
            semantic_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={user_query}&limit=3&fields=title,url"
            response = requests.get(semantic_url, timeout=10)
            data = response.json()
            papers = data.get("data", [])

            if papers:
                response_text = "📚 *Semantic Scholar Results:*\n\n"
                for i, paper in enumerate(papers, 1):
                    title = paper.get("title", "No Title")
                    url = paper.get("url", "No URL")
                    response_text += f"{i}. [{title}]({url})\n"
                update.message.reply_text(response_text, parse_mode='Markdown', disable_web_page_preview=True)
            else:
                update.message.reply_text("❌ No Semantic Scholar results found.")

        except Exception:
            update.message.reply_text(
                "⚠️ Sorry, I couldn’t fetch results from Semantic Scholar right now. Please try again later."
            )

    if source in ('source_arxiv', 'source_all'):
        try:
            arxiv_results = search_arxiv(user_query)
            if arxiv_results:
                response_text = "📚 *arXiv Results:*\n\n"
                for i, (title, link) in enumerate(arxiv_results, 1):
                    response_text += f"{i}. [{title}]({link})\n"
                update.message.reply_text(response_text, parse_mode='Markdown', disable_web_page_preview=True)
            else:
                update.message.reply_text("❌ No arXiv results found.")

        except Exception:
            update.message.reply_text(
                "⚠️ Sorry, I couldn’t fetch results from arXiv right now. Please try again later."
            )

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_query))

    updater.start_polling()
    print("🤖 Bot is running...")
    updater.idle()

if __name__ == "__main__":
    main()
