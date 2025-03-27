import context

async def report(exception: Exception, traceback: str):
    await context.bot.send_message(
        1004310482,
        f"An error occured\n{format(str(type(exception)))} - {format(str(exception))}\n<pre>{format(traceback)}</pre>"
    )
    
format = lambda a: a.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")