import telebot
import lyricsgenius
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubepy import Video

bot = telebot.TeleBot('1763338570:AAH-6CSF7YSeBRu43b-rey2cHFwiYGeXC9I')
genius = lyricsgenius.Genius('9bDm8DpQlsRIZ7TKG76or_AuR_Y0Fkx1g5tjL5tzmG0lgKaSTF6iOT8cjVpL65Qn')
spotify = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials("614ac917f8fc4ac1b5d9ad1d4732b757", "805b79bb63d44b779e6052e0df2a5efa"))


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    # кнопки#
    if message.text == '/start':
        def setSong(message):
            global track
            track = message.text
            keyboard = telebot.types.InlineKeyboardMarkup()
            song_button = telebot.types.InlineKeyboardButton(text='Найти песню', callback_data='find_song')
            keyboard.add(song_button)
            video_button = telebot.types.InlineKeyboardButton(text='Найти клип', callback_data='find_video')
            keyboard.add(video_button)
            text_button = telebot.types.InlineKeyboardButton(text='Найти текст песни', callback_data='find_text')
            keyboard.add(text_button)
            bot.send_message(message.from_user.id, text='Что хочешь????', reply_markup=keyboard)

        def setAuthor(message):
            global author
            author = message.text
            bot.send_message(message.chat.id, "Введи название композиции")
            bot.register_next_step_handler(message, setSong)

        bot.send_message(message.chat.id, "Введи автора композиции")
        bot.register_next_step_handler(message, setAuthor)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "find_song":
        bot.send_message(call.message.chat.id, "cool joint")

    elif call.data == "find_video":
        bot.send_message(call.message.chat.id, "Идет поиск клипа " + author + "-" + track )
        clip_search = Video(author + ' ' + track)
        result = clip_search.search()
        bot.send_message(call.message.chat.id, result)

    elif call.data == "find_text":
        bot.send_message(call.message.chat.id, "Идет поиск текста " + author + "-" + track)
        artist = genius.search_artist(author, 0)
        song = artist.song(track)
        bot.send_message(call.message.chat.id, song.lyrics)


bot.polling()
