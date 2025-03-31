import asyncio
import logging
import os
from rich.console import Console

from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot import ExceptionHandler

import files_helper
import Types

load_dotenv(override=True)

class LogHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()
        formatter = logging.Formatter("\033[38;5;178m%(asctime)s\033[0m %(levelname)s [%(name)s] %(message)s")
        self.setFormatter(formatter)
        
logging.basicConfig(handlers=[LogHandler()], level=logging.DEBUG)
__logger = logging.getLogger("CONTEXT")
__logger.info("init")

global_logger = logging.getLogger("Global")

config: Types.Config

c = Console()

async def load_config():
    global config
    
    __logger.info("Loading config")
    config = await files_helper.get_config()
    
async def save_config():
    await files_helper.save_config(config)

loop = asyncio.new_event_loop()

class Handler(ExceptionHandler):
    def handle(self, exception):
        c.print_exception(show_locals=True)

bot: AsyncTeleBot = AsyncTeleBot(os.environ["bot"], parse_mode="HTML", exception_handler=Handler())
API_ENDPOINT = os.environ["API_ENDPOINT"]