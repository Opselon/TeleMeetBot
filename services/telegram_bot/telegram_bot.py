import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import database
from selenium_automation import SeleniumAutomation

class TelegramBot:
    def __init__(self, token, logger):
        self.token = token
        self.logger = logger
        self.application = Application.builder().token(self.token).build()
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("meet", self.meet))
        self.application.add_handler(CommandHandler("play", self.play))
        self.application.add_handler(CommandHandler("stop", self.stop))
        self.automation = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Welcome to the TeleMeet Bot! Use /help to see the available commands."
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "/meet <google_meet_link>: Joins the specified Google Meet call.\n"
            "/play <youtube_link>: Plays the YouTube video in the shared screen.\n"
            "/stop: Stops the video, stops the screen share, and leaves the call."
        )

    async def meet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Please provide a Google Meet link.")
            return
        meet_url = context.args[0]
        database.set_config('meet_url', meet_url)

        if not self.automation:
            self.automation = SeleniumAutomation(self.logger)

        asyncio.create_task(self.run_automation_async(self.automation.join_meet, meet_url))
        await update.message.reply_text("Acknowledged. Attempting to join Google Meet call...")

    async def play(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Please provide a YouTube video link.")
            return
        youtube_url = context.args[0]
        database.set_config('youtube_url', youtube_url)

        if not self.automation or not self.automation.driver:
            await update.message.reply_text("Bot is not in a meeting. Use /meet first.")
            return

        asyncio.create_task(self.run_automation_async(self.automation.play_youtube_video, youtube_url))
        asyncio.create_task(self.run_automation_async(self.automation.share_screen))
        await update.message.reply_text("Acknowledged. Preparing to play YouTube video...")

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.automation:
            asyncio.create_task(self.run_automation_async(self.automation.stop_automation))
            self.automation = None
        await update.message.reply_text("Acknowledged. Shutting down and leaving the call.")

    async def run_automation_async(self, func, *args):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, func, *args)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.application.run_polling()
