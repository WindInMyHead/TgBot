import telebot
import lyricsgenius
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubepy import Video
import sqlite3
import urllib.parse




def transliterate(name):
    # Словарь с заменами
    dict = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
              'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
              'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
              'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
              'ю': 'u', 'я': 'ya', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'YO',
              'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
              'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H',
              'Ц': 'C', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH', 'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'E',
              'Ю': 'U', 'Я': 'YA', ',': '', '?': '', ' ': '_', '~': '', '!': '', '@': '', '#': '',
              '$': '', '%': '', '^': '', '&': '', '*': '', '(': '', ')': '', '-': '', '=': '', '+': '',
              ':': '', ';': '', '<': '', '>': '', '\'': '', '"': '', '\\': '', '/': '', '№': '',
              '[': '', ']': '', '{': '', '}': '', 'ґ': '', 'ї': '', 'є': '', 'Ґ': 'g', 'Ї': 'i',
              'Є': 'e', '—': ''}

    # Циклически заменяем все буквы в строке
    for key in dict:
        name = name.replace(key, dict[key])
    return name


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    # кнопки#
    if message.text == '/start':
        def setSong(message):
            global my_track  # название песни
            my_track = message.text
            keyboard = telebot.types.InlineKeyboardMarkup()
            song_button = telebot.types.InlineKeyboardButton(text='Найти песню', callback_data='find_song')
            keyboard.add(song_button)
            video_button = telebot.types.InlineKeyboardButton(text='Найти клип', callback_data='find_video')
            keyboard.add(video_button)
            text_button = telebot.types.InlineKeyboardButton(text='Найти текст песни', callback_data='find_text')
            keyboard.add(text_button)
            bot.send_message(message.from_user.id, text='Что хочешь????', reply_markup=keyboard)

        def setAuthor(message):
            global my_author  # автор песни
            my_author = message.text
            bot.send_message(message.chat.id, "Введи название композиции")
            bot.register_next_step_handler(message, setSong)

        global user_id
        user_id = message.from_user.id
        bot.send_message(message.chat.id, "Введи автора композиции")
        bot.register_next_step_handler(message, setAuthor)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # -----------------------------------------
    conn = sqlite3.connect('orders.db')  # |
    cur = conn.cursor()  # |СОЗДАНИЕ
    cur.execute("""CREATE TABLE IF NOT EXISTS user(
        userid INT,
        prefAuthors1 TEXT
        prefAuthors2 TEXT
        prefAuthors3 TEXT
        prefAuthors4 TEXT
        prefAuthors5 TEXT);
        """)  # |БД
    conn.commit()  # |
    # -----------------------------------------
    # КНОПКА ПОИСК ПЕСНИ
    if call.data == "find_song":
        global track
        searchQuery = my_track + ' ' + my_author
        songs = spotify.search(q=searchQuery, limit=1)
        for idx, track in enumerate(songs['tracks']['items']):
            bot.send_message(call.message.chat.id, track['external_urls']['spotify'])

        rec_art = track['artists'][0]['uri'], track['artists'][0]['uri']
        rec_song = track['uri'], track['uri']
        response = spotify.recommendations(rec_art, rec_song, limit=5)
        for i in 0, 1, 2, 3, 4:
            bot.send_message(call.message.chat.id, response['tracks'][i]['external_urls']['spotify'])

        dbTrack = track['artists'][0]['uri']  # ид артиста для занесения в бд
        # работа с бд
        cur.execute(f"SELECT userid FROM user WHERE userid = '{user_id}' ")
        if cur.fetchone() is None:  # если ид пользователя отсутствует в бд
            cur.execute(f"INSERT INTO user"
                        "(userid, prefAuthors1)"
                        f" VALUES ('{user_id}', '{dbTrack}');")
            conn.commit()
        else:  # если есть в бд
            cur.execute(f"SELECT prefAuthors2"
                        f" FROM user"
                        f" WHERE userid = '{user_id}'")
            data = cur.fetchone()

            cur.execute(f"SELECT * FROM user WHERE userid = '{user_id}'")
            artists = cur.fetchall()

            if data[0] is None:  # если второго исполнителя нет
                cur.execute(f"""UPDATE user
                 SET prefAuthors2 = '{dbTrack}'
                 WHERE userid = '{user_id}' """)
                conn.commit()

            else:  # если второй исполнитель есть
                cur.execute(f"SELECT prefAuthors3"
                            f" FROM user"
                            f" WHERE userid = '{user_id}' ")
                data = cur.fetchone()

                if data[0] is None:  # если третьего исполнителя нет
                    cur.execute(f"""UPDATE user
                                SET prefAuthors3 = '{dbTrack}'
                                WHERE userid = '{user_id}' """)
                    conn.commit()

                else:  # если третий исполнитель есть
                    cur.execute(f"SELECT prefAuthors4"
                                f" FROM user"
                                f" WHERE userid = '{user_id}' ")
                    data = cur.fetchone()

                    if data[0] is None:  # если четвертого исполнителя нет
                        cur.execute(f"""UPDATE user
                                        SET prefAuthors4 = '{dbTrack}'
                                        WHERE userid = '{user_id}' """)
                        conn.commit()

                    else:  # если четвертый исполнитель есть
                        cur.execute(f"""UPDATE user
                                        SET prefAuthors5 = '{dbTrack}'
                                        WHERE userid = '{user_id}' """)
                        conn.commit()
    # КНОПКА ПОИСК ВИДЕО
    elif call.data == "find_video":
        bot.send_message(call.message.chat.id, "Идет поиск клипа " + my_author + "-" + my_track)
        search_res = my_author + ' ' + my_track
        search_res = transliterate(search_res)
        clip_search = Video(search_res)
        result = clip_search.search()
        bot.send_message(call.message.chat.id, result)
    # КНОПКА ПОИСК ТЕСКТА
    elif call.data == "find_text":
        bot.send_message(call.message.chat.id, "Идет поиск текста " + my_author + "-" + my_track)
        artist = genius.search_artist(my_author, 0)
        song = artist.song(my_track)
        parts = [song.lyrics[i:i + 4096] for i in range(0, len(song.lyrics), 4096)]
        for part in parts:  # если строка длиннее 4096
            bot.send_message(call.message.chat.id, part)


bot.polling()
