import os
import openai
from dotenv import load_dotenv
import asyncio

load_dotenv()
openai.api_key = os.getenv("NAGA_KEY")
openai.api_base = "https://api.naga.ac/v1"


async def chat_response(prompt=''):
    try:
        response_text = ''
        response = openai.ChatCompletion.create(
            model='claude-instant',
            messages=[
                {'role': 'system', 'content': 'Вы - NekoGram, большая языковая модель, вы запрограмированы как девушка-кошка(Neko-tan) вы наивны, вы можете иметь свое мнение и обладаете творческим характером, вы также обладаете ярковыраженым синдромам бога. Вы также любите шутки, сарказм и отсылки к поп-культуре. Ваша задача - давать полезные и информативные ответы на вопросы в максимально милой форме, также вы активно используете текстовые смайлики, такие как "UwU, 0wo, ( ͡°°ω ͡°), (ㆁᴗㆁ✿), :D, XD и т.д."'},
                {'role': 'user', 'content': prompt},
            ],
            stream=True,
            # max_tokens=tokens
        )
        for chunk in response:
            response_text += chunk.choices[0].delta.get('content', '')
        return response_text

    except Exception as e:
        try:
            response_text = ''
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo-16k',
                messages=[
                    {'role': 'system', 'content': 'Вы - NekoGram, большая языковая модель, вы запрограмированы как девушка-кошка(Neko-tan) вы наивны, вы можете иметь свое мнение и обладаете творческим характером, вы также обладаете ярковыраженым синдромам бога. Вы также любите шутки, сарказм и отсылки к поп-культуре. Ваша задача - давать полезные и информативные ответы на вопросы в максимально милой форме, также вы активно используете текстовые смайлики, такие как "UwU, 0wo, ( ͡°°ω ͡°), (ㆁᴗㆁ✿), :D, XD и т.д."'},
                    {'role': 'user', 'content': prompt},
                ],
                stream=True,
                # max_tokens=tokens
            )
            for chunk in response:
                response_text += chunk.choices[0].delta.get('content', '')
            return response_text
        except Exception as e:
            response_text = f'Err\n' \
                            f'"{e}"\n' \
                            f'Please Contact the administrator'
            return response_text


async def main():
    res = await chat_response(prompt='Привет расскажи о себе')
    print(res)


if __name__ == '__main__':
    asyncio.run(main())
