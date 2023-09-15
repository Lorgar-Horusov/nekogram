import asyncio
import random
import time
from urllib.parse import quote

import aiohttp


async def generate_image_prodia(prompt, neg):
    print("\033[1;32m(Prodia) Creating image for :\033[0m", prompt)
    start_time = time.time()
    model = "anything-v4.5-pruned.ckpt [65745d25]"
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
            'model': model,
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
                    # async with session.get(f'https://images.prodia.xyz/{job_id}.png?download=1',
                    #                        headers=headers) as response:
                    #     content = await response.content.read()
                    #     img_file_obj = io.BytesIO(content)
                    #     duration = time.time() - start_time
                    #     print(f"\033[1;34m(Prodia) Finished image creation\n\033[0mJob id : {job_id}  Prompt : ",
                    #           prompt, "in", duration, "seconds.")
                    #     return img_file_obj


if __name__ == "__main__":

    asyncio.run(
        generate_image_prodia(prompt='cat girl', neg=None))
