import json
import logging
import os

from colorama import Fore
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from keep_alive import keep_alive

from modules import chatGPT, image_ai

load_dotenv()
TOKEN = os.getenv('TELEGRAM_KEY')
user_logger = True
json_file_path = "channels.json"
admin_id = int(os.getenv('OWNER'))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = '''
    /help - Выводит список команд(Логично да?)
    /start - Выводит информацию о боте
    /ask - задать вопрос боту (/ask prompt)
    /imagine - сгенерировать изображения (/imagine model prompt)
    /model_list выодит список моделей для генерации изображений 
    /get_id Возвращает id пользователя
    '''
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                                   reply_to_message_id=update.effective_message.id)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    try:
        with open(json_file_path, "r") as json_file:
            existing_data = json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        existing_data = []

    new_channel_id = update.effective_chat.id

    if new_channel_id not in existing_data:
        existing_data.append(new_channel_id)
        with open(json_file_path, 'w') as json_file:
            json.dump(existing_data, json_file)

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
    if user_logger:
        print(f'{Fore.YELLOW}User {update.effective_user.name} requested:{Fore.CYAN}\n'
              f'"{prompt}"\n'
              f'{Fore.YELLOW}nekogram response:{Fore.CYAN}\n"{text}"{Fore.RESET}')


# async def imagine(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     if not context.args:
#         return await context.bot.send_message(chat_id=update.effective_chat.id,
#                                               text='Пожалуйста, укажите текстовый запрос.\n'
#                                                    '/imagine model request')
#     model_name = context.args[0]
#     try:
#         model = image_ai.Model[model_name]
#     except KeyError:
#         await context.bot.send_message(chat_id=update.effective_chat.id,
#                                        text=f"Модель '{model_name}' не найдена в перечислении Model.\n"
#                                             f"Используйте '/model_list' для отображения всех моделей")
#         return
#     words_prompt = context.args[1:]
#     censor_words = ['NSFW', 'nude', 'naked',
#                     'shota', 'loli', 'hentai',
#                     'explicit', 'pornography', 'XXX',
#                     'sex', 'nsfw', 'gore']
#     censor = False
#     censor_warning = 'safe✅'
#     for word in words_prompt:
#         if word in censor_words:
#             censor = True
#             censor_warning = '⚠️!!!NSFW!!!⚠️'
#             break
#
#     prompt = ' '.join(words_prompt)
#     await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='upload_photo')
#     image = await image_ai.generate_image_prodia(prompt=prompt, model=model, neg=None)
#     await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image,
#                                  caption=f'по запросу: "{prompt}"\n'
#                                          f'rating: {censor_warning}',
#                                  reply_to_message_id=update.effective_message.id,
#                                  has_spoiler=censor)
#
#     if user_logger:
#         print(f'{Fore.YELLOW}User {update.effective_user.name} response:{Fore.CYAN}\n'
#               f'{prompt}\n'
#               f'{Fore.YELLOW}from:{Fore.CYAN}\n'
#               f'{update.effective_chat.id}{Fore.RESET}')


async def model_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = 'analog, anything, abyss, ' \
           'deliberate, dreamlike, ' \
           'dreamsharper, vivild, ' \
           'lyriel, mechamix, ' \
           'openjourney, ' \
           'portrait, ' \
           'realistic, ' \
           'revanimated, ' \
           'sd15, ' \
           'sbp, theallys, timeless'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                                   reply_to_message_id=update.effective_message.id)


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.effective_user.id)


async def msend(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if admin_id != update.effective_user.id:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Yor not permission for this command')
        return
    try:
        with open(json_file_path, "r") as json_file:
            existing_data = json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        existing_data = []
    text = ' '.join(context.args)
    for chat_id in existing_data:
        await context.bot.send_message(chat_id=chat_id, text=text)


async def imagine(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        return await context.bot.send_message(chat_id=update.effective_chat.id,
                                              text='Пожалуйста, укажите текстовый запрос. на английском\n'
                                                   '/imagine request')
    words_prompt = context.args
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
    context.user_data['prompt'] = prompt
    context.user_data['censor'] = censor
    context.user_data['censor_warning'] = censor_warning
    keyboard = [
        [InlineKeyboardButton("🤖 Analog", callback_data="analog")],
        [InlineKeyboardButton("💥 Anything diffusion (Good for anime)", callback_data="anything")],
        [InlineKeyboardButton("🌌 AbyssOrangeMix", callback_data="abyss")],
        [InlineKeyboardButton("💪 Deliberate v2 (Anything you want, nsfw)", callback_data="deliberate")],
        [InlineKeyboardButton("🌌 Dreamlike v2", callback_data="dreamlike")],
        [InlineKeyboardButton("🌌 Dreamshaper 5", callback_data="dreamsharper")],
        [InlineKeyboardButton("🌈 Elldreth vivid mix (Landscapes, Stylized characters, nsfw)", callback_data="vivild")],
        [InlineKeyboardButton("🎼 Lyriel", callback_data="lyriel")],
        [InlineKeyboardButton("🌌 MeinaMix", callback_data="mechamix")],
        [InlineKeyboardButton("🌅 Openjourney (Midjourney alternative)", callback_data="openjourney")],
        [InlineKeyboardButton("👨‍🎨 Portrait (For headshots I guess)", callback_data="portrait")],
        [InlineKeyboardButton("🏞️ Realistic (Lifelike pictures)", callback_data="realistic")],
        [InlineKeyboardButton("🌟 Rev animated (Illustration, Anime)", callback_data="revanimated")],
        [InlineKeyboardButton("🌌 Stable Diffusion v15", callback_data="sd15")],
        [InlineKeyboardButton("🌌 Shonin's Beautiful People", callback_data="sbp")],
        [InlineKeyboardButton("🌌 TheAlly's Mix II", callback_data="theallys")],
        [InlineKeyboardButton("🌌 Timeless", callback_data="timeless")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='select', reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    prompt = context.user_data.get('prompt')
    censor = context.user_data.get('censor')
    censor_warning = context.user_data.get('censor_warning')
    model = image_ai.Model[query.data]
    await query.answer()
    await query.delete_message()
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='upload_photo')
    image = await image_ai.generate_image_prodia(prompt=prompt, model=model, neg=None)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image,
                                 caption=f'по запросу: "{prompt}"\n'
                                         f'rating: {censor_warning}',
                                 reply_to_message_id=update.effective_message.id,
                                 has_spoiler=censor)


def main():
    try:
        keep_alive()
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("ask", ask))
        app.add_handler(CommandHandler("msend", msend))
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help))
        app.add_handler(CommandHandler("model_list", model_list))
        app.add_handler(CommandHandler("imagine", imagine))
        app.add_handler(CommandHandler("get_id", get_id))
        app.add_handler(CallbackQueryHandler(button))


        print(f'{Fore.YELLOW}Слава Омниссии бот запустился!\n'
              f'Логи запросов: {Fore.RED}{user_logger}{Fore.RESET}')
        app.run_polling()
    except Exception as e:
        print(f'{Fore.YELLOW}Бот умер по причине\n'
              f'{Fore.RED}{e}{Fore.RESET}')


if __name__ == '__main__':
    main()
