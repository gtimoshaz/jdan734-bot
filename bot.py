# -- coding: utf8 --

import json
import re
import hashlib
import requests
import math
import os
import traceback
import urllib
from random import choice, randint
from datetime import datetime

import telebot
from decimal import Decimal, getcontext
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup

import data as texts
from prettyword import prettyword

if "TOKEN_HEROKU" in os.environ:
    bot = telebot.TeleBot(os.environ["TOKEN_HEROKU"])
    heroku = True

elif "TOKEN" in os.environ:
    bot = telebot.TeleBot(os.environ["TOKEN"])
    heroku = True

else:
    with open("./token.txt") as token:
        heroku = False
        bot = telebot.TeleBot(token.read())

separator = "/" if os.name == "posix" or os.name == "macos" else "\\"
start_time = datetime.now()


@bot.message_handler(["status"])
def status(message):
    uptime = str(datetime.now() - start_time)
    wikiurl = ".wikipedia.org/w/api.php?action=query"
    uk = requests.get(f"https://uk{wikiurl}").status_code
    ru = requests.get(f"https://ru{wikiurl}").status_code
    de = requests.get(f"https://de{wikiurl}").status_code
    en = requests.get(f"https://en{wikiurl}").status_code
    lurkstatus = requests.get("https://ipv6.lurkmo.re").status_code

    s = "    "

    text = ""
    text += "status: work\n"
    text += f"uptime: {uptime}\n"
    text += f"heroku: {heroku}\n"
    text += f"osname: {os.name}\n"
    text += "services:\n"
    text += f"{s}wikipedia.org:\n"
    text += f"{s*2}uk: {uk}\n"
    text += f"{s*2}ru: {ru}\n"
    text += f"{s*2}en: {en}\n"
    text += f"{s*2}de: {de}\n"
    text += f"{s}lurkmo.re:\n"
    text += f"{s*2}ru: {lurkstatus}"

    text = text.replace("False", "❌") \
               .replace("True", "✅")

    bot.reply_to(message,
                 f"`{text}`",
                 parse_mode="Markdown")


@bot.message_handler(["title"])
def title(message):
    if len(message.text.split(maxsplit=1)) == 2:
        text = message.text.split(maxsplit=1)[1]

    elif hasattr(message.reply_to_message, "text"):
        text = message.reply_to_message.text

    else:
        bot.reply_to(message, "Ответь на сообщение")
        return

    bot.reply_to(message, text.title())


@bot.message_handler(["upper"])
def upper(message):
    if len(message.text.split(maxsplit=1)) == 2:
        text = message.text.split(maxsplit=1)[1]

    elif hasattr(message.reply_to_message, "text"):
        text = message.reply_to_message.text

    else:
        bot.reply_to(message, "Ответь на сообщение")
        return

    bot.reply_to(message, text.upper())


@bot.message_handler(["lower"])
def lower(message):
    if len(message.text.split(maxsplit=1)) == 2:
        text = message.text.split(maxsplit=1)[1]

    elif hasattr(message.reply_to_message, "text"):
        text = message.reply_to_message.text

    else:
        bot.reply_to(message, "Ответь на сообщение")
        return
    bot.reply_to(message, text.lower())


@bot.message_handler(["len"])
def len_(message):
    if len(message.text.split(maxsplit=1)) == 2:
        text = message.text.split(maxsplit=1)[1]

    elif hasattr(message.reply_to_message, "text"):
        text = message.reply_to_message.text

    else:
        bot.reply_to(message, "Ответь на сообщение")
        return
    bot.reply_to(message, len(text))


@bot.message_handler(["markdown"])
def md(message):
    if len(message.text.split(maxsplit=1)) == 2:
        text = message.text.split(maxsplit=1)[1]

    elif hasattr(message.reply_to_message, "text"):
        text = message.reply_to_message.text

    else:
        bot.reply_to(message, "Ответь на сообщение")
        return

    try:
        bot.reply_to(message, text, parse_mode="Markdown")

    except:
        bot.reply_to(message, "Невалидный markdown")


@bot.message_handler(["if"])
def if_(message):
    options = message.text.split()
    try:
        bot.reply_to(message, f"<code>{options[1]}</code> == <code>{options[2]}</code>: <b>{options[1] == options[2]}</b>", parse_mode="HTML")
    except:
        bot.reply_to(message, "Напиши аргументы :/")


# @bot.message_handler(["youtube"])
# def downloadYoutube(message):
#     try:
#         message.reply_to_message.text.replace(" ", "").replace(";", "")
#         print("Text")
#     except:
#         bot.reply_to(message, "Ответь на сообщение с ссылкой")
#         return

#     src = f"{os.path.dirname(os.path.abspath(__file__))}{separator}"

#     with youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s', "format": "18"}) as ydl:
#         video = ydl.download([message.reply_to_message.text])
#     print(src + "M1a2JBhacz8.mp4")
#     bot.send_video(message.chat.id, open(src + "M1a2JBhacz8.mp4" , "rb"))


@bot.message_handler(commands=["preview"])
def preview(message):
    try:
        try:
            bot.send_photo(message.chat.id, f"https://img.youtube.com/vi/{message.reply_to_message.text.replace('&feature=share', '').split('/')[-1]}/maxresdefault.jpg")
        except:
            bot.send_photo(message.chat.id,
                           f'https://img.youtube.com/vi/{urllib.parse.parse_qs(urllib.parse.urlparse(message.reply_to_message.text).query)["v"][0]}/maxresdefault.jpg')
    except Exception as e:
        print(e)
        bot.reply_to(message, "Не получилось скачать превью")


@bot.message_handler(commands=["resize"])
def resize(message):
    try:
        options = message.text.split()

        try:
            int(options[1])

        except ValueError:
            options.extend([100000])

        try:
            int(options[2])
        except ValueError:
            options.extend([100000])

        src = f"{os.path.dirname(os.path.abspath(__file__))}{separator}cache{separator}"

        try:
            photo = bot.get_file(message.reply_to_message.photo[-1].file_id)
            file_id = message.reply_to_message.photo[-1].file_id

        except:
            photo = bot.get_file(message.reply_to_message.document.file_id)
            file_id = message.reply_to_message.document.file_id

        file = bot.download_file(photo.file_path)

        try:
            os.remove(src + file_id)
        except FileNotFoundError:
            pass

        with open(src + file_id + ".jpg", "wb") as new_file:
            new_file.write(file)
        img = Image.open(src + file_id + ".jpg")
        img.thumbnail((int(options[1]), int(options[1])))
        img.save(src + file_id + "_saved.jpg")
        bot.send_photo(message.chat.id, open(src + file_id + "_saved.jpg", "rb"))
        os.remove(src + file_id + "_saved.jpg")
        os.remove(src + file_id + ".jpg")

    except Exception as e:
        bot.reply_to(message, f"`{e}`", parse_mode="Markdown")


@bot.message_handler(commands=["text"])
def text(message):
    params = message.text.split()
    print(params)
    # if True:

    try:
        int(params[3].split("x")[0])
        params = message.text.split(maxsplit=4)
        text = params[len(params) - 1]

    except (ValueError, IndexError):
        params = message.text.split(maxsplit=1)
        text = params[1]

    src = f"{os.path.dirname(os.path.abspath(__file__))}{separator}cache{separator}"

    try:
        try:
            photo = bot.get_file(message.reply_to_message.photo[-1].file_id)
            file_id = message.reply_to_message.photo[-1].file_id

        except:
            photo = bot.get_file(message.reply_to_message.document.file_id)
            file_id = message.reply_to_message.document.file_id

        file = bot.download_file(photo.file_path)

        try:
            os.remove(src + file_id + ".jpg")

        except FileNotFoundError:
            pass

        with open(src + file_id + "_copy.jpg", "wb") as new_file:
            new_file.write(file)

        with open(src + file_id + ".jpg", "wb") as new_file:
            new_file.write(file)

        img = Image.open(src + file_id + ".jpg")

        idraw = ImageDraw.Draw(img)

        # font = ImageFont.truetype("JetBrainsMono.ttf", size=28)
        # idraw.text((4, 4), text, font=font)

        # font = ImageFont.truetype("JetBrainsMono.ttf", size=27)
        # idraw.text((6, 6), text, font=font)
        try:
            xy = params[3].split("x")
        except IndexError:
            xy = [100, 100]

        try:
            x = int(xy[0])
        except IndexError:
            x = 100

        try:
            y = int(xy[1])
        except IndexError:
            y = 100

        try:
            size = int(params[1])
        except IndexError:
            size = 100

        if size > 1000:
            size = 1000

        # font = ImageFont.truetype("NotoSans-Regular.ttf", size=size)
        # font = ImageFont.truetype("Apple Color Emoji.ttf", size=size)
        # idraw.text((7, 10), text, font=font, fill=(0, 0, 0, 0))

        shadowcolor = "white"

        try:
            try:
                fillcolor = params[2].split(",")
                fillcolor = fillcolor.extend(["0"])
                fillcolor = [int(num) for num in fillcolor]
                fillcolor = tuple(fillcolor)
            except:
                fillcolor = params[2]

        except:
            fillcolor = "black"

        font = ImageFont.truetype("OpenSans-Bold.ttf", size=size)

        p = 3

        idraw.text((x-p, y), text, font=font, fill=shadowcolor)
        idraw.text((x+p, y), text, font=font, fill=shadowcolor)
        idraw.text((x, y-p), text, font=font, fill=shadowcolor)
        idraw.text((x, y+p), text, font=font, fill=shadowcolor)

        # thicker border
        idraw.text((x-p, y-p), text, font=font, fill=shadowcolor)
        idraw.text((x+p, y-p), text, font=font, fill=shadowcolor)
        idraw.text((x-p, y+p), text, font=font, fill=shadowcolor)
        idraw.text((x+p, y+p), text, font=font, fill=shadowcolor)

        try:
            idraw.text((x, y), text, font=font, fill=fillcolor)

        except NameError:
            idraw.text((x, y), text, font=font, fill="black")

        img.save(src + file_id + "_text.png", "PNG", dpi=[300, 300], quality=100)
        bot.send_photo(message.chat.id, open(src + file_id + "_text.png", "rb"))

        os.remove(src + file_id + "_text.png")
        os.remove(src + file_id + ".jpg")

    except Exception as e:
        bot.reply_to(message, e)


@bot.message_handler(commands=["rectangle"])
def rectangle(message):
    params = message.text.split(maxsplit=4)
    print(params)
    try:
        params[2]

        src = f"{os.path.dirname(os.path.abspath(__file__))}{separator}cache{separator}"

        try:
            photo = bot.get_file(message.reply_to_message.photo[-1].file_id)
        except:
            photo = bot.get_file(message.reply_to_message.document.thumb.file_id)
        file = bot.download_file(photo.file_path)

        try:
            os.remove(src + message.reply_to_message.photo[-1].file_id + ".jpg")
        except:
            pass

        with open(src + message.reply_to_message.photo[-1].file_id + "_copy.jpg", "wb") as new_file:
            new_file.write(file)

        with open(src + message.reply_to_message.photo[-1].file_id + ".jpg", "wb") as new_file:
            new_file.write(file)

        img = Image.open(src + message.reply_to_message.photo[-1].file_id + ".jpg")

        idraw = ImageDraw.Draw(img)

        try:
            optsize = params[2].split("x")
            optsize1 = params[3].split("x")

            size = (int(optsize[0]), int(optsize[1]))
            size1 = (int(optsize1[0]), int(optsize1[0]))

        except:
            optsize = params[2].split(".")
            optsize1 = params[3].split(".")

            size = (int(optsize[0]), int(optsize[1]))
            size1 = (int(optsize1[0]), int(optsize1[0]))

        idraw.rectangle((size, size1), fill=params[1])
        # except:
        #    idraw.text((x, y), text, font=font, fill="black")

        img.save(src + message.reply_to_message.photo[-1].file_id + "_text.png", "PNG", dpi=[300,300], quality=100)
        bot.send_photo(message.chat.id, open(src + message.reply_to_message.photo[-1].file_id + "_text.png", "rb"))

        os.remove(src + message.reply_to_message.photo[-1].file_id + "_text.png")
        os.remove(src + message.reply_to_message.photo[-1].file_id + ".jpg")

    except Exception as e:
        bot.reply_to(message, e)


@bot.message_handler(commands=["sqrt"])
def sqrt(message):
    try:
        num = float(message.text.split()[1])
        res = math.sqrt(num)

        try:
            res = float(res)

        except:
            res = int(res)

        bot.reply_to(message, f"`{res}`", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"`{e}`", parse_mode="Markdown")


@bot.message_handler(commands=["calc"])
def calc(message):
    options = message.text.split(maxsplit=1)[1].replace(" ", "").replace(",", ".").replace("pi", "3.141592653589793238462643383279")
    getcontext().prec = 25

    try:
        nums = re.split(r"\+", options)
        result = Decimal(nums[0]) + Decimal(nums[1])
    except:
        pass

    try:
        nums = re.split(r"/", options)
        result = Decimal(nums[0]) / Decimal(nums[1])
    except:
        pass

    try:
        nums = re.split(r"-", options)
        result = Decimal(nums[0]) - Decimal(nums[1])
    except:
        pass

    try:
        nums = re.split(r"\*", options)
        result = Decimal(nums[0]) * Decimal(nums[1])
    except:
        pass

    try:
        nums = re.split(r"%", options)
        result = Decimal(nums[0]) % Decimal(nums[1])
    except:
        pass

    try:
        nums = re.split(r"\*\*", options)
        result = Decimal(nums[0]) ** Decimal(nums[1])
    except:
        pass

    try:
        nums = re.split(r"\^", options)
        result = Decimal(nums[0]) ** Decimal(nums[1])
    except:
        pass

    try:
        # if int(result) == float(result):
        #     result = int(result)
        # else:
        #     result = float(result)

        bot.reply_to(message, f"`{str(result)}`", parse_mode="Markdown")

        # except Exception as e:
        #     operator = options[1]
        #     num = float(operator.replace("sqrt(", "").replace(")", ""))

        #     if num:
        #         bot.reply_to(message, math.sqrt(num))

        #     if

    except Exception as e:
        bot.reply_to(message, f"`{e}`", parse_mode="Markdown")


@bot.message_handler(["Math"])
def math_command(message):
    pass

# TODO: REWRITE


@bot.message_handler(commands=["wikiru", "wikiru2", "wru", "wiki"])
def wikiru(message):
    getWiki(message, "ru")


@bot.message_handler(commands=["wikien"])
def wikien(message):
    getWiki(message, "en")


@bot.message_handler(commands=["wikide"])
def wikide(message):
    getWiki(message, "de")


@bot.message_handler(commands=["wikipl"])
def wikipl(message):
    getWiki(message, "pl")


@bot.message_handler(commands=["wikiua", "wikiuk"])
def wikiua(message):
    getWiki(message, "uk")


@bot.message_handler(commands=["wikibe"])
def wikibe(message):
    getWiki(message, "be")


@bot.message_handler(commands=["wikies"])
def wikies(message):
    getWiki(message, "es")


def getWiki(message, lang="ru"):
    if len(message.text.split(maxsplit=1)) == 2:
        query = message.text.split(maxsplit=1)[1]

    else:
        bot.reply_to(message, f"Пожалуйста, напишите название статьи\nНапример так: `/wiki{lang} Название Статьи`", parse_mode="Markdown")
        return

    print(f"[Wikipedia {lang.upper()}] {query}")

    url = f"https://{lang}.wikipedia.org"

    # https://ru.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch=%D0%BA%D0%B0%D1%86&srlimit=1&srsort=relevance

    r = requests.get(f"{url}/w/api.php",
                     params={
                        "action": "query",
                        "format": "json",
                        "list": "search",
                        "srsearch": query,
                        "srlimit": 1,
                        "srprop": "size"
                     })

    if not r.status_code == 200:
        bot.reply_to(message, "Сервер не отвечает")
        return

    data = json.loads(r.text)

    if len(data["query"]["search"]) == 0:
        bot.reply_to(message, "Не удалось найти статью по вашему запросу")
        return

    title = data["query"]["search"][0]["title"]
    page_id = data["query"]["search"][0]["pageid"]

    # https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&titles=Albert%20Einstein&format=json

    # r = requests.get(page_url)

    r = requests.get(url + "/w/api.php",
                     params={
                        "action": "query",
                        "prop": "extracts",
                        "titles": title,
                        "format": "json",
                        "exintro": " "
                     })

    if not r.status_code == 200:
        bot.reply_to(message, "Не удалось загрузить статью")
        return

    soup = BeautifulSoup(json.loads(r.text)["query"]["pages"][str(page_id)]["extract"], "lxml")

    for tag in soup.find_all("p"):
        if re.match(r"\s", tag.text):
            tag.replace_with("")

    # semantics

    for t in soup.findAll("math"):
        t.replace_with("")

    for t in soup.findAll("semantics"):
        t.replace_with("")

    if len(soup.find_all("p")) == 0:
        bot.reply_to(message, "Не получилось найти статью")
        return
    else:
        p = soup.find_all("p")[0]

    bold_text = []

    for tag in p.find_all("b"):
        bold_text.append(tag.text)

    # bot.reply_to(message, bold_text)

    # bot.reply_to(message, p.text.find(":"))
    # bot.reply_to(message, soup)

    text = ""

    if p.text.find("означать:") != -1:
        for tag in soup.find_all("p"):
            text += tag.text

        text += "\n"

        for tag in soup.find_all("li"):
            ind = str(soup.find_all("li").index(tag) + 1)

            ind = ind.replace("0", "0️⃣") \
                     .replace("1", "1️⃣") \
                     .replace("2", "2️⃣") \
                     .replace("3", "3️⃣") \
                     .replace("4", "4️⃣") \
                     .replace("5", "5️⃣") \
                     .replace("6", "6️⃣") \
                     .replace("7", "7️⃣") \
                     .replace("8", "8️⃣") \
                     .replace("9", "9️⃣")

            text += ind + " " + tag.text + "\n"

    else:
        text = re.sub(r"\[.{,}\] ", "", p.text)

    for bold in bold_text:
        if text == f"{bold}:\n":
            text = ""
            for tag in soup.find_all("p"):
                text += tag.text

            text += "\n"

            for tag in soup.find_all("li"):
                ind = str(soup.find_all("li").index(tag) + 1)

                ind = ind.replace("0", "0️⃣") \
                         .replace("1", "1️⃣") \
                         .replace("2", "2️⃣") \
                         .replace("3", "3️⃣") \
                         .replace("4", "4️⃣") \
                         .replace("5", "5️⃣") \
                         .replace("6", "6️⃣") \
                         .replace("7", "7️⃣") \
                         .replace("8", "8️⃣") \
                         .replace("9", "9️⃣")

                text += ind + " " + tag.text + "\n"

    if text == "":
        bot.reply_to(message, "Не получилось найти статью")
        return

    text = text.replace("<", "&lt;") \
               .replace(">", "&gt;") \
               .replace(" )", ")") \
               .replace("  ", " ")

    for bold in bold_text:
        text = re.sub(bold, f"<b>{bold}</b>", text, 1)

    # https://ru.wikipedia.org/w/api.php?action=query&titles=%D0%9A%D0%B0%D1%86,%20%D0%9C%D0%B0%D0%BA%D1%81%D0%B8%D0%BC%20%D0%95%D0%B2%D0%B3%D0%B5%D0%BD%D1%8C%D0%B5%D0%B2%D0%B8%D1%87&prop=pageimages&format=json&pithumbsize=100

    r = requests.get(url + "/w/api.php",
                     params={
                         "action": "query",
                         "titles": title,
                         "prop": "pageimages",
                         "pithumbsize": 1000,
                         "pilicense": "any",
                         "format": "json"
                     })

    if not r.status_code == 200:
        bot.reply_to(message, "Не удалось загрузить статью")
        return

    image_info = json.loads(r.text)

    try:

        # https://en.wikipedia.org/w/api.php?action=query&titles=File:Albert_Einstein_(Nobel).png&prop=imageinfo&iiprop=url&format=json

        photo = image_info["query"]["pages"][str(page_id)]["thumbnail"]["source"]

        if photo == "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Flag_of_Belarus.svg/1000px-Flag_of_Belarus.svg.png":
            photo = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Flag_of_Belarus_%281918%2C_1991%E2%80%931995%29.svg/1000px-Flag_of_Belarus_%281918%2C_1991%E2%80%931995%29.svg.png"

        # bot.reply_to(message, photo)

        bot.send_photo(message.chat.id,
                       photo,
                       caption=text,
                       parse_mode="HTML",
                       reply_to_message_id=message.message_id)

        # https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&titles=Albert%20Einstein&format=json

    except:
        """
        try:
            ""1"

            https://ru.wikipedia.org/w/api.php?action=query&prop=images&titles=%D0%A3%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D1%81%D0%BA%D0%B0%D1%8F%20%D0%9D%D0%B0%D1%80%D0%BE%D0%B4%D0%BD%D0%B0%D1%8F%20%D0%A0%D0%B5%D1%81%D0%BF%D1%83%D0%B1%D0%BB%D0%B8%D0%BA%D0%B0&format=json

            ""1"

            r = requests.get(url + "/w/api.php",
                             params={
                                "action": "query",
                                "prop": "images",
                                "titles": title,
                                "format": "json"
                             })

            bot.reply_to(message, r.url)

            data = json.loads(r.text)

            print()

            list = ""

            for image in data["query"]["pages"][str(page_id)]["images"]:
                list += image["title"] + "\n"

            bot.reply_to(message, list)
        """

        #except:
        bot.reply_to(message, text, parse_mode="HTML")


@bot.message_handler(commands=["github"])
def github(message):
    try:
        url = message.text.split(maxsplit=1)[1]

    except:
        bot.reply_to(message, "Введи название аккаунта")
        return

    try:
        r = requests.get(f"https://api.github.com/users/{url}")
        repos = requests.get(f"https://api.github.com/users/{url}/repos")
        data = json.loads(r.text)
        repos_list = json.loads(repos.text)
        text = f'*{data["name"]}*\nFollowers `{data["followers"]}` Following `{data["following"]}`\n\n__{data["bio"]}__\n\nRepositories:'

        for repo in repos_list:
            print(repo["full_name"])
            text += f'\n[{repo["full_name"]}]({repo["html_url"]})'

        bot.send_photo(message.chat.id,
                       data["avatar_url"],
                       caption=text,
                       parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, e)


def getImageInfo(url, filename):
    r = requests.get(url + "index.php",
                     params={
                         "search": f"Файл:{filename}"
                     })

    soup = BeautifulSoup(r.text, 'lxml')

    return "https:" + soup.find("div", id="file").a.img["src"]


@bot.message_handler(commands=["lurk"])
def lurk(message, logs=False):
    try:
        name = message.text.split(maxsplit=1)[1]
    except:
        bot.reply_to(message, "Введите название статьи")
        return

    print(f"[Lurkmore] {name}")

    url = "https://ipv6.lurkmo.re/"
    # r = requests.get(url + "index.php",
    #                  params={"search": name})

    # https://lurkmo.re/api.php?action=query&format=json&list=search&srsearch=%D0%B1%D0%B0%D1%82%D1%8C%D0%BA%D0%B0&srprop=size

    timedata = ""
    time = datetime.now()

    r = requests.get(f"{url}api.php",
                     params={
                        "action": "query",
                        "format": "json",
                        "list": "search",
                        "srsearch": name,
                        "srlimit": 1,
                        "sprop": "size"
                     })

    if logs:
        timedata = str(datetime.now() - time) + "\n"
        # bot.reply_to(message, datetime.now() - time)

    data = json.loads(r.text)

    if len(data["query"]["search"]) == 0:
        bot.reply_to(message, "Не удалось найти ничего по вашему запросу")
        return

    name = data["query"]["search"][0]["title"]

    time = datetime.now()

    r = requests.get(url + "api.php",
                     params={
                        "action": "parse",
                        "format": "json",
                        "page": name,
                        "prop": "text|images"
                     })

    if logs:
        timedata += str(datetime.now() - time) + "\n"
        # bot.reply_to(message, datetime.now() - time)

    parse = json.loads(r.text)["parse"]
    soup = BeautifulSoup(parse["text"]["*"], 'lxml')

    div = soup

    if len(div.findAll("p")) == 0:
        redirect = soup.ol.li.a["title"]

        time = datetime.now()

        r = requests.get(url + "api.php",
                         params={
                             "action": "parse",
                             "format": "json",
                             "page": redirect,
                             "prop": "text|images"
                         })

        if logs:
            timedata += str(datetime.now() - time) + "\n"
            # bot.reply_to(message, datetime.now() - time)

        soup = BeautifulSoup(json.loads(r.text)["parse"]["text"]["*"], 'lxml')
        div = soup

    for t in div.findAll("table", {"class": "lm-plashka"}):
        t.replace_with("")

    for t in div.findAll("table", {"class": "lm-plashka-tiny"}):
        t.replace_with("")

    for t in div.findAll("table", {"class": "tpl-quote-tiny"}):
        t.replace_with("")

    for t in div.findAll("div", {"class": "gallerytext"}):
        t.replace_with("")

    bold_text = []

    for tag in div.findAll("b"):
        bold_text.append(tag.text)

    url_list = []

    for img in div.find_all("img"):
        if img["src"].find("/skins/") != -1:
            pass
        elif img["src"] == "//lurkmore.so/images/6/6b/Magnify-clip.png":
            pass
        else:
            url_list.append("https:" + img["src"])

    # for img in url_list:
    #     print(img)
    #     try:
    #         bot.send_photo(message.chat.id, f'https:{img}')
    #     except Exception as e:
    #         bot.reply_to(message, img)
    #     sleep(1)

    # bot.send_media_group(message.chat.id, [url_list[0], url_list[1], url_list[2], url_list[3], url_list[4], url_list[5]])
    # bot.send_media_group(message.chat.id, [telebot.types.InputMediaPhoto(url_list[0], "1"),
    #                                       telebot.types.InputMediaPhoto(url_list[1], "2")])

    # print(soup)
    # print(div.findAll("p", recursive=False))

    if logs:
        bot.reply_to(message, f"`{timedata}`", parse_mode="Markdown")
        return

    try:
        page_text = first if (first := div.find("p").text.strip()) \
                          else div.findAll("p", recursive=False)[1] \
                                  .text \
                                  .strip()

        page_text = page_text.replace("<", "&lt;") \
                             .replace(">", "&gt;") \
                             .replace(" )", ")") \
                             .replace("  ", " ")

        for bold in bold_text:
            page_text = re.sub(bold, f"<b>{bold}</b>", page_text, 1)

    except Exception as e:
        bot.reply_to(message, e)
        bot.reply_to(message, "Не удалось найти статью")
        return

    try:
        try:
            path = f'https:{div.find(id="fullResImage")["src"]}'
        except:
            path = url_list[0]

            try:
                img = div.find_all("img")[0]
                filename = img["src"].split("/")[-1].replace(f'{img["width"]}px-', "")
                path = getImageInfo(url, filename)

            except:
                filename = parse["images"][0]
                path = getImageInfo(url, filename)

    except Exception as e:
        # print(e)
        # bot.reply_to(message, e)
        # bot.reply_to(message, "Не удалось загрузить статью")
        print(e)
        path = ""

    try:
        try:
            bot.send_photo(message.chat.id,
                           path,
                           caption=page_text,
                           parse_mode="HTML",
                           reply_to_message_id=message.message_id)

        except:
            try:
                bot.send_photo(message.chat.id,
                               "https:" + div.find("img", class_="thumbborder")["src"],
                               caption=page_text,
                               parse_mode="HTML",
                               reply_to_message_id=message.message_id)

            except:
                bot.send_message(message.chat.id,
                                 page_text,
                                 parse_mode="HTML",
                                 reply_to_message_id=message.message_id)
    except Exception as e:
        bot.reply_to(message,
                     f"Статья недоступна\n<code>{e}</code>",
                     parse_mode="HTML")


@bot.message_handler(commands=["speedlurk"])
def speedlurk(message):
    lurk(message, True)


"""
@bot.message_handler(commands=["bashorg"])
def bashorg(message):
    num = int(message.text.replace("/bashorg@jDan734_bot ", "").replace("/bashorg ", ""))
    r = requests.get(f"https://bash.im/quote/{num}")
    soup = BeautifulSoup(r.text.replace("<br>", "БАН").replace("<br\\>", "БАН"), 'html.parser')

    print(soup.find("div", class_="quote__body").text.replace('<div class="quote__body">', "").replace("</div>", "").replace("<br\\>", "\n"))

    soup2 = BeautifulSoup(soup.find("div", class_="quote__body"), "lxml")
    bot.reply_to(message, soup2)
"""


@bot.message_handler(commands=["mrakopedia"])
def pizdec(message):
    try:
        name = message.text.split(maxsplit=1)[1]
    except:
        bot.reply_to(message, "Введите название статьи")
        return

    print(f"[Mrakopedia] {name}")

    url = "https://mrakopedia.net"
    r = requests.get(url + "/w/index.php",
                     params={"search": name})

    # print(r.text)

    soup = BeautifulSoup(r.text, 'lxml')

    if soup.find("div", class_="searchresults") is None:
        pass
    else:
        div = soup.find("div", class_="searchresults")
        try:
            div.find("p", class_="mw-search-createlink").replace_with("")
            r = requests.get(url + div.find("a")["href"])
            soup = BeautifulSoup(r.text, 'lxml')
        except:
            if div.find("p", class_="mw-search-nonefound").text == "Соответствий запросу не найдено.":
                bot.reply_to(message, "Не получилось найти статью")
                return

    # print(dir(soup.find("div", id="mw-content-text").find("table")))
    # soup.find("div", id="mw-content-text").find("table").remove()

    div = soup.find(id="mw-content-text")

    for t in div.findAll("table", {"class": "lm-plashka"}):
        t.replace_with("")

    for t in div.findAll("table", {"class": "tpl-quote-tiny"}):
        t.replace_with("")

    try:
        page_text = first if (first := div.find("p").text.strip()) else div.findAll("p", recursive=False)[1].text.strip()
    except Exception as e:
        bot.reply_to(message, "Не удалось найти статью")
        # bot.reply_to(message, e)
        return

    try:
        try:
            path = f'{url}{div.find(id="fullResImage")["src"]}'

        except:
            path = f'{url}{div.find("a", class_="image").find("img")["src"]}'
    except:
        pass

    try:
        try:
            bot.send_photo(message.chat.id,
                           path,
                           caption=page_text,
                           parse_mode="HTML",
                           reply_to_message_id=message.message_id)
        except:
            try:
                bot.send_photo(message.chat.id,
                               "https:" + div.find("img", class_="thumbborder")["src"],
                               caption=page_text,
                               parse_mode="HTML",
                               reply_to_message_id=message.message_id)
            except:
                bot.send_message(message.chat.id, page_text, parse_mode="HTML", reply_to_message_id=message.message_id)
    except Exception as e:
        bot.reply_to(message, f"Статья недоступна\n<code>{e}</code>", parse_mode="HTML")


@bot.message_handler(commands=["to_json"])
def to_json(message):
    bot.send_message(message.chat.id,
                     message.reply_to_message.text.replace("'", "\"")
                                                  .replace("False", "false")
                                                  .replace("True", "true")
                                                  .replace("None", '"none"')
                                                  .replace("<", '"<')
                                                  .replace(">", '>"'))


@bot.message_handler(commands=["sha256"])
def sha(message):
    try:
        if message.reply_to_message.text:
            bot.reply_to(message, hashlib.sha256(bytearray(message.reply_to_message.text.encode("utf-8"))).hexdigest())
        elif message.reply_to_message.document:
            file_id = message.reply_to_message.document.file_id

            document = bot.get_file(file_id)
            bot.reply_to(message, hashlib.sha256(bytearray(bot.download_file(document.file_path))).hexdigest())
        else:
            bot.reply_to(message, hashlib.sha256(bytearray(message.reply_to_message.text.encode("utf-8"))).hexdigest())
    except Exception as e:
        bot.reply_to(message, e)


@bot.message_handler(commands=["sticker_id"])
def get_sticker_id(message):
    try:
        bot.reply_to(message, message.reply_to_message.sticker.file_id)

    except:
        bot.reply_to(message, "Ответь на сообщение со стикером")


@bot.message_handler(commands=["delete"])
def delete(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    try:
        # bot.send_message(message.chat.id, message.reply_to_message)
        if message.reply_to_message.from_user.id == "1121412322":
            bot.delete_message(message.chat.id, message.reply_to_message.message_id)
    except:
        pass


"""
@bot.message_handler(commands=["delete_message"])
def delete(message):
    try:
        msgid = int(message.text.split(maxsplit=1)[1])
        bot.delete_message(message.chat.id, msgid)
        bot.reply_to(message, "Удалил")
    except:
        bot.reply_to(message, "Бан))")
"""


@bot.message_handler(commands=["generate_password"])
def password(message):
    if len(message.text.split(maxsplit=1)) == 1:
        bot.reply_to(message, "Укажите количество символов в пароле")
        return

    try:
        crypto_type = int(message.text.split(maxsplit=1)[1])
    except:
        bot.reply_to(message, "Введите число")
        return

    if crypto_type > 4096:
        bot.reply_to(message,
                     "Телеграм поддерживает сообщения длиной не больше `4096` символов",
                     parse_mode="Markdown")
        return

    elif crypto_type < 6:
        bot.reply_to(message,
                     "Пароли меньше `6` символов запрещены",
                     parse_mode="Markdown")
        return

    data = []
    password = ""
    # data.extend(list("абвгдеёжзийклмнопрстуфхцчшщъыьэюя"))
    # data.extend(list("абвгдеёжзийклмнопрстуфхцчшщъыьэюя".upper()))
    data.extend(list("abcdefghijklmnopqrstuvwxyz"))
    data.extend(list("abcdefghijklmnopqrstuvwxyz".upper()))
    data.extend(list('~!@#$%^&*()_+-=`[]\\{}|;\':"<>,./?'))
    data.extend(list("0123456789"))

    for num in range(0, crypto_type):
        password += choice(data)

    bot.reply_to(message, password)
    # print(data)


@bot.message_handler(commands=["start", "help"])
def start(message):
    # try:
    #     bot.delete_message(message.chat.id, message.message_id)
    # except:
    #     True
    try:
        bot.send_message(message.chat.id, texts.rules, reply_to_message_id=message.reply_to_message.message_id)
    except AttributeError:
        bot.send_message(message.chat.id, texts.rules)


@bot.message_handler(commands=["ban"])
def ban(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    msg = message.text.replace("/ban@jDan734_bot", "").replace("/ban", "")
    try:
        bot.send_message(message.chat.id, "Бан" + msg, reply_to_message_id=message.reply_to_message.message_id)
    except AttributeError:
        bot.send_message(message.chat.id, "Бан" + msg)


@bot.message_handler(commands=["bylo"])
def bylo(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    try:
        bot.send_message(message.chat.id, "Было", reply_to_message_id=message.reply_to_message.message_id)
    except AttributeError:
        bot.send_message(message.chat.id, "Было")


@bot.message_handler(commands=["ne_bylo"])
def ne_bylo(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    try:
        bot.send_message(message.chat.id, "Не было", reply_to_message_id=message.reply_to_message.message_id)
    except AttributeError:
        bot.send_message(message.chat.id, "Не было")


@bot.message_handler(commands=["pizda"])
def pizda(message):
    sendSticker(message,
                "CAACAgIAAx0CUDyGjwACAQxfCFkaHE52VvWZzaEDQwUC8FYa-wAC3wADlJlpL5sCLYkiJrDFGgQ")


@bot.message_handler(commands=["net_pizdy"])
def net_pizdy(message):
    sendSticker(message,
                "CAACAgIAAx0CUDyGjwACAQ1fCFkcDHIDN_h0qHDu7LgvS8SBIgAC4AADlJlpL8ZF00AlPORXGgQ")


@bot.message_handler(commands=["xui"])
def xui(message):
    sendSticker(message,
                "CAACAgIAAx0CUDyGjwACAQ5fCFkeR-pVhI_PUTcTbDGUOgzwfAAC4QADlJlpL9ZRhbtO0tQzGgQ")


@bot.message_handler(commands=["net_xua"])
def net_xua(message):
    sendSticker(message,
                "CAACAgIAAx0CUDyGjwACAQ9fCFkfgfI9pH9Hr96q7dH0biVjEwAC4gADlJlpL_foG56vPzRPGgQ")


@bot.message_handler(commands=["xui_pizda"])
def xui_pizda(message):
    sendSticker(message,
                choice(["CAACAgIAAx0CUDyGjwACAQ5fCFkeR-pVhI_PUTcTbDGUOgzwfAAC4QADlJlpL9ZRhbtO0tQzGgQ", "CAACAgIAAx0CUDyGjwACAQxfCFkaHE52VvWZzaEDQwUC8FYa-wAC3wADlJlpL5sCLYkiJrDFGgQ"]))


def sendSticker(message, sticker_id):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    try:
        bot.send_sticker(message.chat.id,
                         sticker_id,
                         reply_to_message_id=message.reply_to_message.message_id)
    except AttributeError:
        bot.send_sticker(message.chat.id, sticker_id)


@bot.message_handler(commands=["fake"])
def polak(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    try:
        bot.send_photo(message.chat.id, open("images/polak.jpg", "rb"), reply_to_message_id=message.reply_to_message.message_id)
    except AttributeError:
        bot.send_photo(message.chat.id, open("images/polak.jpg", "rb").read())


@bot.message_handler(commands=["rzaka"])
def rzaka(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    try:
        bot.send_message(message.chat.id,
                         texts.rzaka,
                         reply_to_message_id=message.reply_to_message.message_id)
    except AttributeError:
        bot.send_message(message.chat.id, texts.rzaka)


@bot.message_handler(commands=["rzaka_full"])
def rzaka_full(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

    try:
        bot.send_message(message.chat.id,
                         texts.rzaka_full,
                         reply_to_message_id=message.reply_to_message.message_id)
    except AttributeError:
        bot.send_message(message.chat.id, texts.rzaka_full)


@bot.message_handler(commands=["detect"])
def detect_boicot(message):
    if message.text.find("бойкот") != -1:
        bot.reply_to(message, "Вы запостили информацию о бойкоте, если вы бойкотировали, то к вам приедут с паяльником")
    else:
        bot.reply_to(message, "Бойкот не обнаружен")


@bot.message_handler(commands=["random_ban", "random"])
def random(message):
    bot.reply_to(message, f"Лови бан на {randint(1, 100)} минут")


@bot.message_handler(commands=["random_color", "color"])
def random_color(message):
    randlist = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, "A", "B", "C", "D", "E", "F"]

    color = ""
    for i in range(0, 6):
        color += str(choice(randlist))

    bot.reply_to(message, f"`#{color}`", parse_mode="Markdown")


@bot.message_handler(commands=["random_putin"])
def random_putin(message):
    number = randint(1, 500)
    date = choice(["дней", "месяцев", "лет"])

    if date == "дней":
        true_date = prettyword(number, ["день", "дня", "дней"])

    elif date == "месяцев":
        true_date = prettyword(number, ["месяц", "месяца", "месяцев"])

    elif date == "лет":
        true_date = prettyword(number, ["год", "года", "лет"])

    bot.reply_to(message, f'Путин уйдет через {number} {true_date}')


@bot.message_handler(commands=["random_lukash", "luk"])
def random_lukash(message):
    number = randint(0, 500)

    if number == 0:
        bot.reply_to(message, "Иди нахуй))")

    else:
        nedeli = number / 7
        date = choice(["дней", "месяцев"])

        if date == "дней":
            true_date = prettyword(number, ["день", "дня", "дней"])

        elif date == "месяцев":
            true_date = prettyword(number, ["месяц", "месяца", "месяцев"])

        if number % 7 == 0:
            bot.reply_to(message, f'Лукашенко уйдет через {int(nedeli)} {prettyword(int(nedeli), ["неделя", "недели", "недель"])}')
        else:
            print(number % 7)
            bot.reply_to(message, f'Лукашенко уйдет через {int(nedeli)} {prettyword(int(nedeli), ["неделя", "недели", "недель"])} и {int(number % 7)} {prettyword(int(number % 7), ["день", "дня", "дней"])}')    


@bot.message_handler(commands=["da_net"])
def da_net(message):
    bot.reply_to(message, choice(["Да", "Нет"]))


@bot.message_handler(content_types=['text'])
def detect(message):
    if message.text.find("бойкот") != -1:
        bot.reply_to(message, "Вы запостили информацию о бойкоте, если вы бойкотировали, то к вам приедут с паяльником")

    if message.text.find("когда уйдет путин") != -1:
        random_putin(message)


@bot.message_handler(content_types=["new_chat_members"])
def john(message):
    bot.reply_to(message, f'{choice(texts.greatings)}?')


@bot.message_handler(content_types=['document', 'video'],
                     func=lambda message: message.chat.id == -1001189395000)
def delete_w10(message):
    try:
        if message.video.file_size == 842295 or \
           message.video.file_size == 912607:
            bot.delete_message(message.chat.id, message.message_id)
    except:
        pass


try:
    bot.polling()
except:
    bot.send_message("795449748",
                     f"`{str(traceback.format_exc())}`",
                     parse_mode="Markdown")
