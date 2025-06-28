import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


class MangaReader:
    def __init__(self):
        self.name = "MangaReader"
        self.base_url = "https://mangareader.to"
        self.logo = "https://pbs.twimg.com/profile_images/1437311892905545728/TO0hFfUr_400x400.jpg"
        self.class_path = "MANGA.MangaReader"
        self.headers = {
            "User-Agent": "Mozilla/5.0",
        }

    def _get_request(self, url: str) -> str:
        response = requests.get(f"{self.base_url}{url}", headers=self.headers)
        response.raise_for_status()
        return response.text

    def search(self, query: str) -> Dict:
        try:
            html_data = self._get_request(f"/search?keyword={query}")
            soup = BeautifulSoup(html_data, "html.parser")

            results = []
            for el in soup.select("div.manga_list-sbs div.mls-wrap div.item"):
                link = el.select_one("a.manga-poster")
                image = el.select_one("a.manga-poster img")
                genres = [
                    genre.text
                    for genre in el.select("div.manga-detail div.fd-infor span > a")
                ]

                results.append(
                    {
                        "id": link["href"].split("/")[1] if link else "",
                        "title": (
                            el.select_one(
                                "div.manga-detail h3.manga-name a"
                            ).text.strip()
                            if el.select_one("div.manga-detail h3.manga-name a")
                            else ""
                        ),
                        "image": image["src"] if image else "",
                        "genres": genres,
                    }
                )

            return {"results": results}
        except requests.HTTPError as e:
            raise ValueError(f"HTTP Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")

    def fetch_manga_info(self, manga_id: str) -> Dict:
        manga_info = {
            "id": manga_id,
            "title": "",
        }
        try:
            html_data = self._get_request(f"/{manga_id}")
            soup = BeautifulSoup(html_data, "html.parser")
            with open("data.html", "w", encoding="utf-8") as file:
                file.write(html_data)

            container = soup.select_one("div.ani_detail-stage div.container")
            manga_info["title"] = container.select_one(
                "div.anisc-detail h2.manga-name"
            ).text.strip()
            manga_info["image"] = container.select_one("img.manga-poster-img")["src"]
            manga_info["description"] = ' '.join(soup.select_one("div.description").text.split())
            manga_info["genres"] = [
                genre.text.strip()
                for genre in container.select("div.sort-desc div.genres a")
            ]

            manga_info["chapters"] = [
                {
                    "id": (
                        el.select_one("a")["href"].split("/read/")[1]
                        if el.select_one("a") and el.select_one("a").get("href")
                        else ""
                    ),
                    "title": (
                        el.select_one("a")["title"].strip()
                        if el.select_one("a") and el.select_one("a").get("title")
                        else ""
                    ),
                    "chapter": (
                        el.select_one("a span.name").text.split("Chapter ")[1].split(":")[0]
                        if el.select_one("a span.name") and "Chapter " in el.select_one("a span.name").text
                        else ""
                    ),
                }
                for el in soup.select("div.page-layout.page-detail div.container div.chapters-list-ul ul li")
            ]
            return manga_info
        except requests.HTTPError as e:
            raise ValueError(f"HTTP Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")

    def fetch_chapter_pages(self, chapter_id: str) -> List[Dict]:
        try:
            html_data = self._get_request(f"/read/{chapter_id}")
            soup = BeautifulSoup(html_data, "html.parser")

            reading_id = soup.select_one("div#wrapper")["data-reading-id"]
            if not reading_id:
                raise ValueError("Unable to find pages")

            ajax_url = f"https://mangareader.to/ajax/image/list/chap/{reading_id}?mode=vertical&quality=high"
            pages_data = requests.get(ajax_url, headers=self.headers).json()
            pages_html = pages_data["html"]
            soup_pages = BeautifulSoup(pages_html, "html.parser")

            pages_selector = soup_pages.select(
                "div#main-wrapper div.container-reader-chapter div.iv-card"
            )

            pages = [
                {
                    "img": el["data-url"].replace("&amp;", "&"),
                    "page": i + 1,
                }
                for i, el in enumerate(pages_selector)
            ]

            return pages
        except requests.HTTPError as e:
            raise ValueError(f"HTTP Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")


# Example usage
# manga_reader = MangaReader()
# search_results = manga_reader.search('one piece')
# manga_info = manga_reader.fetch_manga_info(search_results['results'][0]['id'])
# chapter_pages = manga_reader.fetch_chapter_pages(manga_info['chapters'][0]['id'])
# print(search_results, manga_info, chapter_pages)
