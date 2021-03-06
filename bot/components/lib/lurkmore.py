import re
import json
import requests

from bs4 import BeautifulSoup


class Lurkmore:
    def __init__(self):
        self.url = "https://ipv6.lurkmo.re/api.php"
        self.url2 = "https://ipv6.lurkmo.re"
        self.params = {"format": "json", "action": "query"}

    def _get(self, params):
        self.params = {**self.params, **params}

        r = requests.get(self.url, self.params)

        if not r.status_code == 200:
            return 404

        return json.loads(r.text)

    def search(self, query, limit=1):
        """
            https://lurkmore.to/api.php?action=query&format=json&list=search&srsearch=%D0%9F%D1%83%D1%82%D0%B8%D0%BD&srprop=size&srlimit=1
        """
        r = self._get({
                "list": "search",
                "srsearch": query,
                "srprop": "size",
                "srlimit": limit
            })

        results = []

        for item in r["query"]["search"]:
            results.append(item["title"])

        return results

    def opensearch(self, query, limit=1):
        """
            https://lurkmore.to/api.php?action=opensearch&search=%D0%BF%D1%83%D1%82%D0%B8%D0%BD
        """
        r = self._get({
                "action": "opensearch",
                "search": query,
                "limit": limit
            })

        results = []

        for item in r[1]:
            results.append(item)

        return results

    def getPage(self, title):
        r = self._get({
                "action": "parse",
                "page": title,
                "prop": "text",
                "redirects": True,
                "section": 0
            })

        return r["parse"]["text"]["*"]

    def getImagesList(self, title):
        r = self._get({
                "action": "parse",
                "page": title,
                "prop": "images",
                "redirects": True,
                "section": 0
            })

        images_list = []
        blocklist = ["St.jpg", "ZOG1.jpg", "Butthurt.png", "Politota.png", "SShA.jpg", "48ef4db2ad.png", "Hate_small.png", "BanCaptcha.jpg", "Magnify-clip.png", "Wrar64.png", "Warning_1.png", "Eri_x_Yakumo.jpg", "Slowpoke.png", "Drama.png", "Barbed_wire_new_flip.png", "Huy.png", "Bashorgrufavicon.png", "Nihuya-small.png", "Uvaga.gif", "Nohate.jpg", "Hypnotoad_1.gif", "Kapitan_ochevidnost'.jpg", "Tema_sm.jpg"]

        for item in r["parse"]["images"]:
            if item not in blocklist:
                images_list.append(item)

        return images_list

    def getImageFromFandomPage(self, page):
        p = BeautifulSoup(page, "lxml")

        try:
            for t in p.find("aside").findAll("h2"):
                t.replace_with("")
        except:
            pass

        try:
            i = p.find("aside").find("a", {"class": "image"}).find("img")

            return i["src"]
        except:
            return 404

    def getImage(self, filename):
        r = requests.get(self.url2, {
                    "search": f"Файл:{filename}"
                })

        soup = BeautifulSoup(r.text, 'lxml')

        return "https:" + soup.find("div", id="file").a.img["src"]

    def findImagesInPage(self, imagelist, div):
        url_list = []
        blocklist = ["//lurkmore.so/images/9/9f/St.jpg",
                     "//lurkmore.so/images/thumb/0/0a/ZOG1.jpg/64px-ZOG1.jpg",
                     "//lurkmore.so/images/thumb/4/41/Butthurt.png/64px-Butthurt.png",
                     "//lurkmore.so/images/c/ca/Politota.png",
                     "//lurkmore.so/images/thumb/f/f1/SShA.jpg/270px-SShA.jpg",
                     "/skins/common/images/magnify-clip.png",
                     "//lurkmore.so/images/thumb/e/e6/48ef4db2ad.png/32px-48ef4db2ad.png",
                     "//lurkmore.so/images/thumb/9/9c/Hate_small.png/64px-Hate_small.png"]

        for img in div.find_all("img"):
            if img["src"].find("/skins/") != -1:
                pass
            elif img["src"] in blocklist:
                pass
            else:
                url_list.append("https:" + img["src"])
        return url_list

    def parse(self, page):
        soup = BeautifulSoup(page, 'lxml')

        try:
            for t in soup.findAll("table", {"class": "lm-plashka"}):
                t.replace_with("")

            for t in soup.findAll("table", {"class": "lm-plashka-tiny"}):
                t.replace_with("")

            for t in soup.findAll("table", {"class": "tpl-quote-tiny"}):
                t.replace_with("")

            for t in soup.findAll("div", {"class": "gallerytext"}):
                t.replace_with("")

            for t in soup.findAll("aside"):
                t.replace_with("")

            for t in soup.findAll("table"):
                t.replace_with("")

            for t in soup.findAll("p"):
                if "Это статья об" in t.text:
                    t.replace_with("")
        except:
            pass

        bold_text = []

        for tag in soup.findAll("b"):
            bold_text.append(tag.text)

        try:
            page_text = first if (first := soup.find("p").text.strip()) \
                              else soup.findAll("p")[1] \
                                      .text \
                                      .strip()

            page_text = page_text.replace("<", "&lt;") \
                                 .replace(">", "&gt;") \
                                 .replace(" )", ")") \
                                 .replace("  ", " ")

            for bold in bold_text:
                try:
                    page_text = re.sub(bold, f"<b>{bold}</b>", page_text, 1)
                except re.error:
                    page_text = page_text.replace(bold + " ", f"<b>{bold}</b> ")

        except Exception as e:
            print(e)
            return "Не удалось распарсить"

        return page_text
