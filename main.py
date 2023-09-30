import json
import logging
import os

from colorama import Fore, Style
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import time
from keep_alive import run_flask_in_thread

from modules import chatGPT, image_ai, bot_tts

load_dotenv()
TOKEN = os.getenv('TELEGRAM_KEY')
user_logger = True
logger = False
json_file_path = "channels.json"
admin_id = int(os.getenv('OWNER'))

if logger:
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
           "Если вы хотите поддержать моего разработчика, то можете купить ему баночку энергетика\n" \
           "Или помочь ему с приобретением нового хостинга [Boosty:](https://boosty.to/lorgar-horusov/single-payment/donation/474159/target?share=target_link)"

    try:
        with open(json_file_path, "r") as json_file:
            existing_data = json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        existing_data = []

    new_channel = update.effective_chat.id
    chat_entry = next((entry for entry in existing_data if entry.get("Chat ID") == new_channel), None)

    if chat_entry is None:
        chat_entry = {"Chat ID": new_channel, "notification_enable": True}
        existing_data.append(chat_entry)
        with open(json_file_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)

    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo='https://i.ibb.co/VSvjnLh/image.png',
                                 caption=text, parse_mode='Markdown')


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        return await context.bot.send_message(chat_id=update.effective_chat.id,
                                              text='Пожалуйста, укажите текстовый запрос.\n'
                                                   '/ask request')
    prompt = r' '.join(context.args)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    start_timer = time.time()
    text = await chatGPT.chat_response(prompt=prompt)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                                   reply_to_message_id=update.effective_message.id)
    end_timer = time.time()
    result = round(end_timer - start_timer, 2)
    if user_logger:
        print(f'{Fore.YELLOW + Style.BRIGHT}User {Fore.LIGHTBLUE_EX}{update.effective_user.name}{Fore.YELLOW}'
              f'requested:{Fore.CYAN + Style.NORMAL}\n'
              f'"{prompt}"\n'
              f'{Fore.YELLOW + Style.BRIGHT}Nekogram response: {Fore.LIGHTBLUE_EX}{result} seconds{Fore.CYAN}\n'
              f'"{text}"{Fore.RESET}')


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'User ID = {update.effective_user.id}\n'
                                                                          f'Chat ID = {update.effective_chat.id}')


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
        if chat_id.get('notification_enable'):
            try:
                await context.bot.send_message(chat_id=chat_id.get('Chat ID'), text=text)
                print(f'{Fore.YELLOW + Style.BRIGHT}Sending to ---> {Fore.CYAN + Style.NORMAL}'
                      f'{chat_id.get("Chat ID")}{Fore.GREEN} Done!{Fore.RESET}')
            except Exception as e:
                print(f'{Fore.RED + Style.BRIGHT}Sending to -x-> {Fore.CYAN + Style.NORMAL}'
                      f'{chat_id.get("Chat ID")}{Fore.RED} Error! ({e}){Fore.RESET}')


async def imagine(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        return await context.bot.send_message(chat_id=update.effective_chat.id,
                                              text='Пожалуйста, укажите текстовый запрос. на английском\n'
                                                   '/imagine request')
    words_prompt = context.args
    censor_words = ['NSFW', 'nude', 'naked',
                    'shota', 'loli', 'hentai',
                    'explicit', 'pornography', 'XXX',
                    'sex', 'nsfw', 'gore', 'fuck']
    censor = False
    censor_warning = 'safe✅'
    for word in words_prompt:
        if word in censor_words:
            censor = True
            censor_warning = '⚠️!!!NSFW!!!⚠️'
            break

    prompt = r' '.join(words_prompt)
    context.user_data['prompt'] = prompt
    context.user_data['censor'] = censor
    context.user_data['censor_warning'] = censor_warning
    context.user_data['current_user'] = update.effective_user.id

    keyboard = [
        [InlineKeyboardButton("🤖 Analog", callback_data="analog"),
         InlineKeyboardButton("💥 Anything diffusion (Good for anime)", callback_data="anything")],

        [InlineKeyboardButton("🌌 AbyssOrangeMix", callback_data="abyss"),
         InlineKeyboardButton("💪 Deliberate v2 (Anything you want, nsfw)", callback_data="deliberate")],

        [InlineKeyboardButton("🌌 Dreamlike", callback_data="dreamlike"),
         InlineKeyboardButton("🌌 Dreamshaper 5", callback_data="dreamsharper")],

        [InlineKeyboardButton("🌈 Elldreth vivid mix (Landscapes, Stylized characters, nsfw)", callback_data="vivild"),
         InlineKeyboardButton("🎼 Lyriel", callback_data="lyriel")],

        [InlineKeyboardButton("🌌 MeinaMix", callback_data="meinamix"),
         InlineKeyboardButton("👨‍🎨 Mechamix", callback_data="mechamix")],

        [InlineKeyboardButton("🌅 Openjourney (Midjourney alternative)", callback_data="openjourney"),
         InlineKeyboardButton("🏞️ Realistic (Lifelike pictures)", callback_data="realistic")],

        [InlineKeyboardButton("🌟 Rev animated (Illustration, Anime)", callback_data="revanimated"),
         InlineKeyboardButton("🌌 Stable Diffusion v15", callback_data="sd15")],

        [InlineKeyboardButton("🌌 Shonin's Beautiful People", callback_data="sbp"),
         InlineKeyboardButton("🌌 TheAlly's Mix II", callback_data="theallys")],

        [InlineKeyboardButton("🌌 Timeless", callback_data="timeless")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Choice a model', reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    prompt = context.user_data.get('prompt')
    censor = context.user_data.get('censor')
    censor_warning = context.user_data.get('censor_warning')
    current_user = int(context.user_data.get('current_user'))
    actual_user = int(update.effective_user.id)
    model = image_ai.Model[query.data]
    if actual_user != current_user:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='dont permission')
        return

    await query.answer()
    await query.delete_message()
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='upload_photo')
    start_timer = time.time()
    image = await image_ai.generate_image_prodia(prompt=prompt, model=model, neg=None)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image,
                                 caption=f'по запросу: "{prompt}"\n'
                                         f'rating: {censor_warning}\n'
                                         f'model: {query.data}',
                                 has_spoiler=censor)
    end_timer = time.time()
    result = round(end_timer - start_timer, 2)
    if user_logger:
        print(f'{Fore.YELLOW + Style.BRIGHT}User {Fore.LIGHTBLUE_EX}{update.effective_user.name}{Fore.YELLOW}'
              f'requested: {Fore.CYAN + Style.NORMAL}\n'
              f'"{prompt}"\n'
              f'{Fore.YELLOW + Style.BRIGHT}Necogram created the image in: {Style.NORMAL + Fore.LIGHTBLUE_EX}'
              f'{result} seconds{Fore.RESET}')


async def alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    try:
        with open(json_file_path, "r") as json_file:
            existing_data = json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        existing_data = []
    chat_entry = next((entry for entry in existing_data if entry.get("Chat ID") == chat_id), None)
    if chat_entry is None:
        await context.bot.send_message(chat_id=chat_id, text='Похоже вы не подключены к системе '
                                                             'уведомлений, пожалуйста пропишите '
                                                             '/start чтобы подключиться')
    else:
        chat_entry["notification_enable"] = not chat_entry.get("notification_enable")
        if chat_entry.get('notification_enable'):
            await context.bot.send_message(chat_id=chat_id, text='enabled')
        else:
            await context.bot.send_message(chat_id=chat_id, text='disabled')

    with open(json_file_path, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)


async def tts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        return await context.bot.send_message(chat_id=update.effective_chat.id,
                                              text='Пожалуйста, укажите текстовый запрос который нужно озвучить.\n'
                                                   '/tts request')
    text = r' '.join(context.args)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='record_voice')
    voice = await bot_tts.generate_speech(text=text)
    await context.bot.send_voice(chat_id=update.effective_chat.id, voice=voice,
                                 reply_to_message_id=update.effective_message.id)


def main():
    try:
        run_flask_in_thread()
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("ask", ask))
        app.add_handler(CommandHandler("msend", msend))
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help))
        app.add_handler(CommandHandler("alerts", alerts))
        app.add_handler(CommandHandler("imagine", imagine))
        app.add_handler(CommandHandler("get_id", get_id))
        app.add_handler(CommandHandler("tts", tts))
        app.add_handler(CallbackQueryHandler(button))

        print(f'{Fore.YELLOW}Слава Омниссии бот запустился!\n'
              f'Логи запросов: {Fore.RED}{user_logger}{Fore.RESET}')
        app.run_polling()
    except Exception as e:
        print(f'{Fore.YELLOW}Бот умер по причине\n'
              f'{Fore.RED}{e}{Fore.RESET}'
              f'Пожалуйста свяжитесь с администратором'
              f'https://t.me/Teodor_Guerra')


if __name__ == '__main__':
    main()
