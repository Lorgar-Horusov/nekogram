import asyncio
import random
from enum import Enum
from urllib.parse import quote

import aiohttp


class Model(Enum):
    analog = "analog-diffusion-1.0.ckpt [9ca13f02]"
    anything = "anything-v4.5-pruned.ckpt [65745d25]"
    abyss = "AOM3A3_orangemixs.safetensors [9600da17]"
    deliberate = "deliberate_v2.safetensors [10ec4b29]"
    dreamlike = "dreamlike-diffusion-2.0.safetensors [fdcf65e7]"
    dreamsharper = "dreamshaper_6BakedVae.safetensors [114c8abb]"
    vivild = "elldreths-vivid-mix.safetensors [342d9d26]"
    lyriel = "lyriel_v16.safetensors [68fceea2]"
    mechamix = "meinamix_meinaV9.safetensors [2ec66ab0]"
    openjourney = "openjourney_V4.ckpt [ca2f377f]"
    portrait = "portrait+1.0.safetensors [1400e684]"
    realistic = "Realistic_Vision_V2.0.safetensors [79587710]"
    revanimated = "revAnimated_v122.safetensors [3f4fefd9]"
    riffusion = "riffusion-model-v1.ckpt [3aafa6fe]"
    sd15 = "v1-5-pruned-emaonly.ckpt [81761151]"
    sbp = "shoninsBeautiful_v10.safetensors [25d8c546]"
    theallys = "theallys-mix-ii-churned.safetensors [5d9225a4]"
    timeless = "timeless-1.0.ckpt [7c4971d4]"


async def generate_image_prodia(prompt, model, neg):
    sampler = 'Euler'
    seed = random.randint(1, 99999)

    async def create_job(prompt, model, sampler, seed, neg):
        if neg is None:
            negative = "verybadimagenegative_v1.3, ng_deepnegative_v1_75t, (ugly face:0.8),cross-eyed,sketches, (worst quality:2), (low quality:2), (normal quality:2), lowres, normal quality, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, bad anatomy, DeepNegative, facing away, tilted head, {Multiple people}, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worstquality, low quality, normal quality, jpegartifacts, signature, watermark, username, blurry, bad feet, cropped, poorly drawn hands, poorly drawn face, mutation, deformed, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, extra fingers, fewer digits, extra limbs, extra arms,extra legs, malformed limbs, fused fingers, too many fingers, long neck, cross-eyed,mutated hands, polar lowres, bad body, bad proportions, gross proportions, text, error, missing fingers, missing arms, missing legs, extra digit, extra arms, extra leg, extra foot, repeating hair, nsfw, [[[[[bad-artist-anime, sketch by bad-artist]]]]], [[[mutation, lowres, bad hands, [text, signature, watermark, username], blurry, monochrome, grayscale, realistic, simple background, limited palette]]], close-up, (swimsuit, cleavage, armpits, ass, navel, cleavage cutout), (forehead jewel:1.2), (forehead mark:1.5), (bad and mutated hands:1.3), (worst quality:2.0), (low quality:2.0), (blurry:2.0), multiple limbs, bad anatomy, (interlocked fingers:1.2),(interlocked leg:1.2), Ugly Fingers, (extra digit and hands and fingers and legs and arms:1.4), crown braid, (deformed fingers:1.2), (long fingers:1.2)"
        else:
            negative = neg
        url = 'https://api.prodia.com/generate'
        params = {
            'new': 'true',
            'prompt': f'{quote(prompt)}',
            'model': model.value,
            'negative_prompt': f"{negative}",
            'steps': '100',
            'cfg': '9.5',
            'seed': f'{seed}',
            'sampler': sampler,
            'upscale': 'True',
            'aspect_ratio': 'square'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                return data['job']

    job_id = await create_job(prompt, model, sampler, seed, neg)
    url = f'https://api.prodia.com/job/{job_id}'
    headers = {
        'authority': 'api.prodia.com',
        'accept': '*/*',
    }

    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url, headers=headers) as response:
                json = await response.json()
                if json['status'] == 'succeeded':
                    image_url = f'https://images.prodia.xyz/{job_id}.png'
                    # print(image_url)
                    return image_url


if __name__ == "__main__":
    model_name = input("Введите имя модели: ")
    try:
        model_enum = Model[model_name]
    except KeyError:
        print(f"Модель '{model_name}' не найдена в перечислении Model.")
    asyncio.run(generate_image_prodia(prompt='cat girl', model=model_enum, neg=None))
