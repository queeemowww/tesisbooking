from aiogoogle import Aiogoogle
import json
import asyncio


async def authorize():
    # Загружаем сохранённые client и user credentials
    with open("creds.json", "r") as f:
        user_creds = json.load(f)

    with open("client_creds.json", "r") as f:
        client_creds = json.load(f)

    aiogoogle = Aiogoogle(client_creds=client_creds)

    refreshed_creds = await aiogoogle.oauth2.refresh(user_creds, client_creds)

    with open("creds.json", "w") as f:
        json.dump(refreshed_creds[1], f, indent=2)

# asyncio.run(authorize())
