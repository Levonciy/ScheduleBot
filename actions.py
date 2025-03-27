import aiohttp

import context
import Types

async def __check(resp: aiohttp.ClientResponse):
    if resp.status != 200:
        raise Types.RequestError(resp.status, await resp.text())

async def get_classes():
    async with aiohttp.ClientSession(base_url=context.API_ENDPOINT) as session:
        async with session.get("getClasses") as req:
            await __check(req)
            return Types.OptionCollection.model_validate((await req.json())["classes"])

async def get_teachers():
    async with aiohttp.ClientSession(base_url=context.API_ENDPOINT) as session:
        async with session.get("getTeachers") as req:
            await __check(req)
            return Types.OptionCollection.model_validate((await req.json())["teachers"])
    
async def get_class(id: int | str):
    async with aiohttp.ClientSession(base_url=context.API_ENDPOINT) as session:
        async with session.get("getClass", params={"id": id}) as req:
            await __check(req)
            return Types.OptionCollection.model_validate((await req.json())["class"])
    
async def get_teacher(id: int | str):
    async with aiohttp.ClientSession(base_url=context.API_ENDPOINT) as session:
        async with session.get("getTeacher", params={"id": id}) as req:
            await __check(req)
            return Types.OptionCollection.model_validate((await req.json())["teacher"])