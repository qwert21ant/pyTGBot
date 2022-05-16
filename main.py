import telebot
from telebot import types
from printbot import EasyPrint
from PIL import Image

# Settings
bot = telebot.TeleBot('xxxx')
Printer = EasyPrint('C://TGbot', 4)
admin_id = 0000
# Settings


# Init

# Init


# Keyboard markup
markup_user = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup_user.row(types.KeyboardButton('Помощь'),
                types.KeyboardButton('Состояние'))

markup_admin = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup_admin.row(types.KeyboardButton('Помощь'),
                 types.KeyboardButton('Лог доступа'),
                 types.KeyboardButton('Лог ошибок'))
markup_admin.row(types.KeyboardButton('Состояние'),
                 types.KeyboardButton('Очистить логи'),
                 types.KeyboardButton('Вкл/Выкл принтер'))
# Keyboard markup


# On /start
@bot.message_handler(content_types=['text'], commands=['start'])
def onStart(msg):
    try:
        markup = {}
        if msg.from_user.id == admin_id:
            markup = markup_admin
        else:
            markup = markup_user

        bot.send_message(msg.from_user.id, 'Кидай картинку и я её распечатаю', reply_markup=markup)

    except Exception as e:
        bot.reply_to(msg, e)


# On text
@bot.message_handler(content_types=['text'])
def onHelp(msg):
    try:
        if msg.text == 'Помощь':
            bot.send_message(msg.from_user.id, 'Я принимаю изображения и '
                                               'файлы (.png/.jpg/...) и печатаю их')
        if msg.text == 'Состояние':
            res = Printer.status()
            if res:
                bot.send_message(msg.from_user.id, '🟢 Принтер включен')
            else:
                bot.send_message(msg.from_user.id, '🔴 Принтер выключен')

        if msg.from_user.id == admin_id:
            if msg.text == 'Лог доступа':
                log_data = Printer.access_log.get()
                if log_data:
                    bot.send_message(admin_id, log_data)
                else:
                    bot.send_message(admin_id, 'Пусто')

            if msg.text == 'Лог ошибок':
                log_data = Printer.error_log.get()
                if log_data:
                    bot.send_message(admin_id, log_data)
                else:
                    bot.send_message(admin_id, 'Пусто')

            if msg.text == 'Очистить логи':
                Printer.access_log.clear()
                Printer.error_log.clear()
                bot.send_message(admin_id, 'Очищено')

            if msg.text == 'Вкл/Выкл принтер':
                Printer.switch()
                bot.send_message(msg.from_user.id, 'Состояние изменено')
        else:
            bot.send_message(msg.from_user.id, 'У вас нет прав')
    except Exception as e:
        bot.reply_to(msg, e)


# Save + resize + print ...
def proc_image(msg, image):
    Printer.save(image)
    Printer.resize()

    res = Printer.status()
    if res == -1:
        Printer.error_log.log('couldn\'t get status')
        bot.send_message(msg.from_user.id, 'Не удалось получить статус принтера')
        return
    if res == 0:
        bot.send_message(msg.from_user.id, 'В данный момент принтер выключен')
        return

    res = Printer.print()
    if res:
        Printer.access_log.log('@' + msg.from_user.username + ' - ' + 'couldn\'t print the image')
        Printer.error_log.log('couldn\'t print the image')
        bot.send_message(msg.from_user.id, 'Возникла ошибка при печати')
    else:
        Printer.access_log.log('@' + msg.from_user.username + ' - ' + 'print the image')
        bot.send_message(msg.from_user.id, 'Изображение успешно распечатано')
        bot.send_message(admin_id, '@' + msg.from_user.username + ' распечатал изображение')
        bot.send_photo(admin_id, Printer.load())

    Printer.remove()


# On document
@bot.message_handler(content_types=['document'])
def onDoc(msg):
    try:
        file_info     = bot.get_file(msg.document.file_id)
        download_file = bot.download_file(file_info.file_path)

        proc_image(msg, download_file)

    except Exception as e:
        bot.reply_to(msg, e)


# On photo
@bot.message_handler(content_types=['photo'])
def onPhoto(msg):
    try:
        file_info     = bot.get_file(msg.photo[-1].file_id)
        download_file = bot.download_file(file_info.file_path)

        proc_image(msg, download_file)

    except Exception as e:
        bot.reply_to(msg, e)


# main
bot.polling(none_stop=True, interval=0)
# img = Image.open('C://TGbot/leon2.jpg')
# data = img.load()
# print(data[0, 0])
# print(data[-1, -1])