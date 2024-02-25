from states import UserState
from pyrogram import Client
import settings
from handlers import register_handlers
from callbacks import register_callbacks

user_state = UserState()

app = Client(
    "my_task_bot",
    api_id=settings.API_ID,
    api_hash=settings.API_HASH,
    bot_token=settings.BOT_TOKEN
)

register_handlers(app, user_state)
register_callbacks(app, user_state)

if __name__ == "__main__":
    app.run()
