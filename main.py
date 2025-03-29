import asyncio
import uvicorn
from fastapi import FastAPI

import context
import bot
import report
import Types

app = FastAPI()

@app.post("/updateSchedule")
async def update_schedule(info: Types.ScheduleUpdateInfo):
    loop.create_task(report.update_schedule(info))

loop = context.loop
server = uvicorn.Server(uvicorn.Config(app, "0.0.0.0", 8002))

loop.run_until_complete(context.load_config())
loop.create_task(server.serve())
loop.create_task(context.bot.polling(True))
loop.run_forever()