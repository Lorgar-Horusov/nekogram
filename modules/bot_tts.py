import asyncio
import os
from dotenv import load_dotenv

import aiohttp

load_dotenv()
TTS_URL = 'https://api.naga.ac/v1/audio/tts/generation'


async def generate_speech(text="Если долго вглядываться в бездну, то она покраснеет и отвернется"):
    headers = {'Authorization': f'Bearer {os.getenv("NAGA_KEY")}'}
    json_data = {'text': text}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(f"{TTS_URL}", json=json_data) as resp:
            response = await resp.json()
            return response.get('url')


async def main():
    res = await generate_speech()
    print(res)


if __name__ == '__main__':
    asyncio.run(main())
