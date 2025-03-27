import aiofiles
import const
import os
import Types

async def check_file():
    """Проверяет наличие конфига, если конфига нет, то создает его
    """
    if not os.path.exists("config.json"):
        async with aiofiles.open("config.json", "w", encoding="utf8") as f:
            await f.write(const.BARE_CONFIG.model_dump_json())
            
async def get_config() -> Types.Config:
    """Загружает конфига из config.json

    Returns:
        Types.Config: спаршенный в объект конфиг
        
    Raises:
        pydantic.ValidationError: произошла ошибка при попытке считать конфиг
    """
    await check_file()
    async with aiofiles.open("config.json", "r", encoding="utf8") as f:
        return Types.Config.model_validate_json(await f.read())
    
async def save_config(config: Types.Config):
    """Сохраняет переданный конфиг в config.json

    Args:
        config (Types.Config): объект конфига
    """
    async with aiofiles.open("config.json", "w", encoding="utf8") as f:
        await f.write(config.model_dump_json())