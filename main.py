import os
from dotenv import load_dotenv
from modules import chatGPT, image_ai

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv('TELEGRAM_KEY')


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = '''
    /help - Выводит список команд(Логично да?)
    /info - Выводит информацию о боте
    /ask - задать вопрос боту
    /imagine - сгенерировать изображения 
    '''


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "UwU~ Прииивет, сенпай! " \
           "Я - Nekogram, ваша милейшая кото-девочка-ботяра!\n" \
           "Мурр-р!~ (˃ᆺ˂)\n" \
           "Я специально создана для того, " \
           "чтобы помогать вам с ответами, " \
           "Я умею создавать не только ответы, но и создавать " \
           "прекрасные изображения, как настоящая арт-мастерица! " \
           "(ノ^∇^) \n" \
           "Если у вас есть какие-либо вопросы или хотите " \
           "что-нибудь удивительное, то просто пишите мне! Я всегда здесь, " \
           "чтобы радовать вас ответами и изображениями!~ (─‿‿─)\n" \
           "Вы также можете найти меня на [GitHub:](https://github.com/Lorgar-Horusov)"
    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo='https://i.ibb.co/VSvjnLh/image.png',
                                 caption=text, parse_mode='Markdown')


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt = ' '.join(context.args)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    text = await chatGPT.chat_response(prompt=prompt)
    # await context.bot.send_messager(chat_id=update.effective_chat.id, text=text)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                                   reply_to_message_id=update.effective_message.id)


async def imagine(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    words_prompt = context.args
    censor_words = ['NSFW', 'nude', 'naked', 'shota', 'loli', 'hentai', 'explicit', 'pornography', 'XXX', 'sex', 'nsfw']
    censor = False
    censor_warning = 'safe'
    for word in words_prompt:
        if word in censor_words:
            censor = True
            censor_warning = '⚠️!!!NSFW!!!⚠️'
            break

    prompt = ' '.join(words_prompt)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='upload_photo')
    image = await image_ai.generate_image_prodia(prompt=prompt, neg=None)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image,
                                 caption=f'Фото для: "{update.effective_user.name}"\n'
                                         f'по запросу: "{prompt}"\n'
                                         f'rating: {censor_warning}',
                                 reply_to_message_id=update.effective_message.id,
                                 has_spoiler=censor)


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("imagine", imagine))
    app.run_polling()


if __name__ == '__main__':
    main()
