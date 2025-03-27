import asyncio
import uvicorn
from fastapi import FastAPI

import context
import bot

app = FastAPI()

loop = context.loop
server = uvicorn.Server(uvicorn.Config(app, "0.0.0.0", 8000))

loop.run_until_complete(context.load_config())
loop.create_task(server.serve())
loop.create_task(context.bot.polling(True))
loop.run_forever()