import os
from dotenv import load_dotenv
from modules import chatGPT, image_ai
from colorama import Fore
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv('TELEGRAM_KEY')
logger = True


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = '''
    /help - Выводит список команд(Логично да?)
    /info - Выводит информацию о боте
    /ask - задать вопрос боту (/ask prompt)
    /imagine - сгенерировать изображения (/imagine model prompt)
    /model_list выодит список моделей для генерации изображений 
    '''
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                                   reply_to_message_id=update.effective_message.id)


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
           "Вы также можете найти меня на [GitHub:](https://github.com/Lorgar-Horusov/nekogram)\n" \
           "Если вы хотите поддержать моего разработчика, то можете купить ему баночку энергетика\n"

    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo='https://i.ibb.co/VSvjnLh/image.png',
                                 caption=text, parse_mode='Markdown')


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        return await context.bot.send_message(chat_id=update.effective_chat.id,
                                              text='Пожалуйста, укажите текстовый запрос.\n'
                                                   '/ask request')
    prompt = ' '.join(context.args)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    text = await chatGPT.chat_response(prompt=prompt)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                                   reply_to_message_id=update.effective_message.id, parse_mode='Markdown')
    if logger:
        print(f'{Fore.YELLOW}User {update.effective_user.name} requested:{Fore.CYAN}\n'
              f'"{prompt}"\n'
              f'{Fore.YELLOW}nekogram response:{Fore.CYAN}\n"{text}"{Fore.RESET}')


async def imagine(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        return await context.bot.send_message(chat_id=update.effective_chat.id,
                                              text='Пожалуйста, укажите текстовый запрос.\n'
                                                   '/imagine model request')
    model_name = context.args[0]
    try:
        model = image_ai.Model[model_name]
    except KeyError:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"Модель '{model_name}' не найдена в перечислении Model.\n"
                                            f"Используйте '/model_list' для отображения всех моделей")
        return
    words_prompt = context.args[1:]
    censor_words = ['NSFW', 'nude', 'naked',
                    'shota', 'loli', 'hentai',
                    'explicit', 'pornography', 'XXX',
                    'sex', 'nsfw', 'gore']
    censor = False
    censor_warning = 'safe✅'
    for word in words_prompt:
        if word in censor_words:
            censor = True
            censor_warning = '⚠️!!!NSFW!!!⚠️'
            break

    prompt = ' '.join(words_prompt)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='upload_photo')
    image = await image_ai.generate_image_prodia(prompt=prompt, model=model, neg=None)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image,
                                 caption=f'Фото для: "{update.effective_user.name}"\n'
                                         f'по запросу: "{prompt}"\n'
                                         f'rating: {censor_warning}',
                                 reply_to_message_id=update.effective_message.id,
                                 has_spoiler=censor)

    if logger:
        print(f'{Fore.YELLOW}User {update.effective_user.name} response:{Fore.CYAN}\n'
              f'{prompt}\n'
              f'{Fore.YELLOW}from:{Fore.CYAN}\n'
              f'{update.effective_chat.id}{Fore.RESET}')


async def model_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = 'analog, anything, abyss, ' \
           'deliberate, dreamlike, ' \
           'dreamsharper, vivild, ' \
           'lyriel, mechamix, ' \
           'openjourney, ' \
           'portrait, ' \
           'realistic, ' \
           'revanimated, ' \
           'riffusion, sd15, ' \
           'sbp, theallys, timeless'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                                   reply_to_message_id=update.effective_message.id)


def main():
    try:
        keep_alive()
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("ask", ask))
        app.add_handler(CommandHandler("info", info))
        app.add_handler(CommandHandler("help", help))
        app.add_handler(CommandHandler("model_list", model_list))
        app.add_handler(CommandHandler("imagine", imagine))
        print(f'{Fore.YELLOW}Слава Омниссии бот запустился!\n'
              f'Логи запросов: {Fore.RED}{logger}{Fore.RESET}')
        app.run_polling()
    except Exception as e:
        print(f'{Fore.YELLOW}Бот умер по причине\n'
              f'{Fore.RED}{e}{Fore.RESET}')


if __name__ == '__main__':
    main()
