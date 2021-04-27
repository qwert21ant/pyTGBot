import os
import telebot
from telebot import types
from PIL import Image


# bot token
bot = telebot.TeleBot('1693054202:AAGlR75Fq4sh1L0PSwxzGGeg5hQpFXgEuLI')


# dir settings
main_dir    = '/TGbot'
save_dir    = 'images'
resize_dir  = 'resized'
save_path   = main_dir + '/' + save_dir + '/'
resize_path = main_dir + '/' + resize_dir + '/'


# resize to width:
pic_width = 500





markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.row(types.KeyboardButton('/help'),
           types.KeyboardButton('/remove'),
           types.KeyboardButton('/list'))
markup.row(types.KeyboardButton('/resize'),
           types.KeyboardButton('/get'))

@bot.message_handler(content_types=['text'], commands=['get'])
def onGet(msg):
    try:
        files = os.listdir(resize_path)
        bot.send_message(msg.from_user.id, 'Resize\'нутые изображения (' + str(len(files)) + '):', reply_markup=markup)
        for f in files:
            bot.send_photo(msg.from_user.id, photo=open(resize_path + f, 'rb'), caption=f)
    except Exception as e:
        bot.reply_to(msg, e)

@bot.message_handler(content_types=['text'], commands=['list'])
def onList(msg):
    try:
        files = os.listdir(save_path)
        text = 'Список загруженных изображений (' + str(len(files)) + '): \n'
        for f in files:
            text += '  ' + f + '\n'
        bot.send_message(msg.from_user.id, text, reply_markup=markup)
    except Exception as e:
        bot.reply_to(msg, e)

@bot.message_handler(content_types=['text'], commands=['help'])
def onHelp(msg):
    try:
        bot.send_message(msg.from_user.id, '/start - начать\n'
                                           '/help - этот текст \n'
                                           '/remove - удалить все изображения \n'
                                           '/list - список загруженных изображений \n'
                                           '/get - получить resize\'нутые изображения \n'
                                           '/resize - resize\'нуть все загруженные изображения \n'
                                           'Бот принимает только данные команды,'
                                           ' изображения и файлы (.png/.jpg/...)',
                                            reply_markup=markup)
    except Exception as e:
        bot.reply_to(msg, e)

@bot.message_handler(content_types=['text'], commands=['start'])
def onStart(msg):
    try:
        bot.send_message(msg.from_user.id, 'Кидай картинку', reply_markup=markup)
    except Exception as e:
        bot.reply_to(msg, e)

@bot.message_handler(content_types=['text'], commands=['resize'])
def onResize(msg):
    try:
        files = os.listdir(save_path)
        for f in files:
            img = Image.open(save_path + f)
            w, h = img.size
            size = (pic_width, int(h / w * pic_width))
            res = img.resize(size)
            res.save(resize_path + f)
        bot.send_message(msg.from_user.id, 'Все сохранённые изображения resize\'нуты', reply_markup=markup)
    except Exception as e:
        bot.reply_to(msg, e)

@bot.message_handler(content_types=['text'], commands=['remove'])
def onRemove(msg):
    try:
        files = os.listdir(save_path)
        for f in files:
            os.remove(save_path + f)

        files = os.listdir(resize_path)
        for f in files:
            os.remove(resize_path + f)
        bot.send_message(msg.from_user.id, 'Все изображения удалены', reply_markup=markup)
    except Exception as e:
        bot.reply_to(msg, e)

@bot.message_handler(content_types=['document'])
def onDoc(msg):
    try:
        file_info     = bot.get_file(msg.document.file_id)
        download_file = bot.download_file(file_info.file_path)

        fpath = file_info.file_path
        src = save_path + fpath[fpath.find('/')+1:]
        with open(src, 'wb') as new_file:
            new_file.write(download_file)
        bot.send_message(msg.from_user.id, 'Сохранил как ' + fpath[fpath.find('/') + 1:], reply_markup=markup)
    except Exception as e:
        bot.reply_to(msg, e)

@bot.message_handler(content_types=['photo'])
def onPhoto(msg):
    try:
        file_info     = bot.get_file(msg.photo[-1].file_id)
        download_file = bot.download_file(file_info.file_path)

        fpath = file_info.file_path
        src = save_path + fpath[fpath.find('/') + 1:]
        with open(src, 'wb') as new_file:
            new_file.write(download_file)
        bot.send_message(msg.from_user.id, 'Сохранил как ' + fpath[fpath.find('/') + 1:], reply_markup=markup)
    except Exception as e:
        bot.reply_to(msg, e)



bot.polling(none_stop=True, interval=0)