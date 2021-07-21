import telebot
import lyricsgenius, spotipy, YouTubeMusicAPI
from spotipy.oauth2 import SpotifyClientCredentials
import vk_audio
from youtubepy import Video
from yandex_music import Client
from telebot import types
import itunesmusicsearch

vk = vk_audio.VkAudio(login='логин вк', password='пароль вк')  # ВК авторизация
#client = Client()  # Клиент Яндекс.Музыки
bot = telebot.TeleBot('токен бота')  # API бота
genius = lyricsgenius.Genius('токен genius')  # Api Genius
spotify = spotipy.Spotify(  # API Spotify
    auth_manager=SpotifyClientCredentials("spotify", "token"))


class User:
    id: ''
    artist: ''
    track: ''

    # Функция, задающая песню
    def setSong(self, message):
        self.track = message.text.lower()
        init_keyboard(message, self)

    # Функция задающая автора
    def setArtist(self, message):
        self.artist = message.text.lower()
        bot.send_message(message.chat.id, "Введи название композиции")
        bot.register_next_step_handler(message, self.setSong)


# транслитерация
def transliterate(name):
    # Словарь с заменами
    dicktionary = {'а': 'a', 'б': 'b', 'в': 'w', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh',
                   'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
                   'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c',
                   'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'i', 'ь': '', 'э': 'e', 'ю': 'u',
                   'я': 'ya', 'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'e', 'f': 'f', 'g': 'g', 'h': 'h',
                   'i': 'i', 'j': 'j', 'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'o': 'o', 'p': 'p',
                   'q': 'q', 'r': 'r', 's': 's', 't': 't', 'u': 'u', 'v': 'v', 'w': 'w', 'x': 'x',
                   'y': 'y', 'z': 'z', ',': '', '?': '', ' ': ' ', '~': '', '!': '', '@': '', '#': '', 'Є': 'e',
                   '—': '',
                   '$': '', '%': '', '^': '', '&': '', '*': '', '(': '', ')': '', '-': '', '=': '', '+': '+',
                   ':': '', ';': '', '<': '', '>': '', '\'': '', '"': '', '\\': '', '/': '', '№': '',
                   '[': '', ']': '', '{': '', '}': '', 'ґ': '', 'ї': '', 'є': '', 'Ґ': 'g', 'Ї': 'i', }
    # Циклически заменяем все буквы в строке
    for key in dicktionary:
        name = name.replace(key, dicktionary[key])
    return name


# Обработка команды /start
@bot.message_handler(commands=['start'])
def get_text_messages(message):
    my_user = User()
    my_user.id = message.from_user.id
    bot.send_message(message.chat.id, 'Добро пожаловать, {0.first_name}!\nЯ - {1.first_name},'
                                      ' бот созданный для помощи с музыкой.'.format(message.from_user, bot.get_me()), )
    bot.send_message(message.chat.id, "Введи автора композиции")
    bot.register_next_step_handler(message, my_user.setArtist)


# Обработка команды /developers
@bot.message_handler(commands=['developers'])
def developers_info(message):
    bot.send_message(message.chat.id,
                     "Разработчики:\nАнтон Короткин @WindInMyHead\nАнтон Макотра @macktosha\nНикита Клейменов @gloomy_tenzor\nДмитрий Айдаров @dmitry_awesome\nВадим Непомнящий @not_remember1ng\nДмитрий Яций @rastvor01\nПо всем вопросам и предложениям обращаться и не стесняться!")


# Обработка команды /help
@bot.message_handler(commands=['help'])
def help_info(message):
    bot.send_message(message.chat.id, """Данный бот создан, чтобы облегчить жизнь всех любителей музыки\n\nЧтобы начать - выберите команду /start. Затем введите исполнителя
и название песни, далее вам будут предложены функции поиска трека на различных площадках, поиск клипа на YouTube и поиск текста песни.\n\nВыбрав команду /developers, вы найдете информацию для связи с
разработчиками.\nСпасибо за выбор Joint_bot!!!""")


# Инициализация клавиатуры с действиями
def init_keyboard(message, my_user):
    keyboard = telebot.types.InlineKeyboardMarkup()
    data = str(my_user.track) + '\n' + str(my_user.artist) + '\n' + str(my_user.id)
    song_button = telebot.types.InlineKeyboardButton(text='Найти песню', callback_data='find_song\n' + data)
    keyboard.add(song_button)
    video_button = telebot.types.InlineKeyboardButton(text='Найти клип', callback_data='find_video\n' + data)
    keyboard.add(video_button)
    text_button = telebot.types.InlineKeyboardButton(text='Найти текст песни', callback_data='find_text\n' + data)
    keyboard.add(text_button)
    bot.send_message(message.chat.id, text='Выбери действие', reply_markup=keyboard)


# КНОПКА ПОИСК ПЕСНИ
@bot.callback_query_handler(func=lambda call: call.data.startswith('find_song'))
def track_button(call):
    my_user = set_class(call)
    search_query = str(transliterate(my_user.artist + ' ' + my_user.track))  # Запрос в совмещенном виде
    markup = url_keyboard(search_query)
    image = image_spotify(search_query)
    bot.send_photo(call.message.chat.id, image['album']['images'][0]['url'],
               caption=f"Исполнитель: {image['artists'][0]['name']}\n"
                       f"Трек: {image['name']} \n"
                       f"Альбом: {image['album']['name']} \n"
                       f"Дата релиза: {image['album']['release_date']} ", reply_markup=markup)
    init_keyboard(call.message, my_user)


# КНОПКА ПОИСК ВИДЕО
@bot.callback_query_handler(func=lambda call: call.data.startswith('find_video'))
def button_video(call):
    my_user = set_class(call)
    bot.send_message(call.message.chat.id, "Идет поиск клипа " + my_user.artist + "-" + my_user.track)
    bot.send_message(call.message.chat.id, url_video_youtube(my_user))
    init_keyboard(call.message, my_user)


# КНОПКА ПОИСК ТЕСКТА
@bot.callback_query_handler(func=lambda call: call.data.startswith('find_text'))
def button_text(call):
    my_user = set_class(call)
    bot.send_message(call.message.chat.id, "Идет поиск текста " + my_user.artist + "-" + my_user.track)
    lyrics = text_from_genius(my_user)
    parts = [lyrics[i:i + 4096]
             for i in range(0, len(lyrics), 4096)]
    for part in parts:  # если строка длиннее 4096
        bot.send_message(call.message.chat.id, part)
    init_keyboard(call.message, my_user)


# URL-клавиатура с песней на каждом сервисе
def url_keyboard(search_query):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton(text='Spotify', url=url_spotify(search_query))
    #item2 = types.InlineKeyboardButton(text='Яндекс.Музыка', url=url_yandex(search_query))
    item3 = types.InlineKeyboardButton(text='Вконтакте', url=url_vk(search_query))
    item4 = types.InlineKeyboardButton(text='YouTube Music', url=url_youtube(search_query))
    item5 = types.InlineKeyboardButton(text='Apple Music', url=url_apple(search_query))
    markup.add(item1, item3, item4, item5)
    return markup


# Поиск ссылки на клип к треку
def url_video_youtube(my_user):
    query = transliterate(my_user.artist + ' ' + my_user.track)
    result = Video(query).search()
    return result


# Переопределение объекта класса
def set_class(call):
    my_user = User()
    my_user.track = call.data.splitlines()[1]
    my_user.artist = call.data.splitlines()[2]
    my_user.id = call.data.splitlines()[3]
    return my_user


# Поиск текста на Genius
def text_from_genius(my_user):
    artist = genius.search_artist(transliterate(my_user.artist), 0)
    song = artist.song(transliterate(my_user.track))
    return song.lyrics


# Поиск ссылки на Spotify
def url_spotify(search_query):
    songs = spotify.search(q=search_query, limit=1)
    return songs['tracks']['items'][0]['external_urls']['spotify']


# Поиск обложки на Spotify
def image_spotify(search_query):
    image = spotify.search(q=search_query, limit=1)
    return image['tracks']['items'][0]


# Поиск ссылки на Яндекс Музыке
def url_yandex(search_query):
    search_result = client.search(search_query)
    result = "https://music.yandex.ru/album/" + str(search_result.tracks.results[0].albums[0].id) + \
             "/track/" + str(search_result.tracks.results[0].id)
    return result


# Поиск ссылки на ВК
def url_vk(search_query):
    search_result = vk.search(query=search_query)
    result = "https://vk.com/music/album/" + str(search_result.Audios[00].Album.owner_id) + "_" + \
             str(search_result.Audios[00].Album.id) + "_" + \
             str(search_result.Audios[00].Album.access_hash)
    return result


# Поиск ссылки на YouTube Music
def url_youtube(search_query):
    result = YouTubeMusicAPI.getsonginfo(search_query)
    if result['song_name'] is None:
        return None
    return result['track_url']


# Поиск ссылки на Apple Music
def url_apple(search_query):
    track = itunesmusicsearch.search_track(search_query)
    return track[0].track_view_url


bot.polling(none_stop=True)
