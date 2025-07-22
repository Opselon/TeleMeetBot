import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

class TelegramBot:
    def __init__(self, token, app, logger):
        self.token = token
        self.app = app
        self.logger = logger
        self.application = Application.builder().token(self.token).build()
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("meet", self.meet))
        self.application.add_handler(CommandHandler("play", self.play))
        self.application.add_handler(CommandHandler("stop", self.stop))

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
        self.app.meet_url_entry.delete(0, "end")
        self.app.meet_url_entry.insert(0, meet_url)
        self.app.deploy_bot()
        await update.message.reply_text("Acknowledged. Attempting to join Google Meet call...")

    async def play(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Please provide a YouTube video link.")
            return
        youtube_url = context.args[0]
        self.app.youtube_url_entry.delete(0, "end")
        self.app.youtube_url_entry.insert(0, youtube_url)
        self.app.play_video()
        await update.message.reply_text("Acknowledged. Preparing to play YouTube video...")

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.app.stop_bot()
        await update.message.reply_text("Acknowledged. Shutting down and leaving the call.")

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.application.run_polling()
