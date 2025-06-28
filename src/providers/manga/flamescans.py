import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


class FlameScans:
    def __init__(self):
        self.name = "FlameScans"
        self.base_url = "https://flamecomics.xyz/"
        self.logo = "https://i.imgur.com/Nt1MW3H.png"
        self.class_path = "MANGA.FlameScans"
        self.headers = {
            "User-Agent": "Mozilla/5.0",
        }

    def _get_request(self, url: str) -> str:
        response = requests.get(f"{self.base_url}{url}", headers=self.headers)
        response.raise_for_status()
        return response.text

    def search(self, query: str) -> Dict:
        try:
            query = query.replace(" ", "%20")
            html_data = self._get_request(f"/series/?title={query}")
            soup = BeautifulSoup(html_data, "html.parser")

            search_manga_selector = (
                ".utao .uta .imgu, .listupd .bs .bsx, .listo .bs .bsx"
            )
            results = []
            for el in soup.select(search_manga_selector):
                link = el.select_one("a")
                img = el.select_one("img")
                results.append(
                    {
                        "id": (
                            link["href"].split("/series/")[1].replace("/", "")
                            if link
                            else ""
                        ),
                        "title": link["title"] if link else "",
                        "image": img["src"] if img else "",
                        "status": soup.select_one("div.status i").text.strip() if soup.select_one("div.status i") else None,
                        "rating": soup.select_one(".mobile-rt .numscore").text.strip() if soup.select_one(".mobile-rt .numscore") else None
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
            html_data = self._get_request(f"/series/{manga_id}")
            soup = BeautifulSoup(html_data, "html.parser")
            series_title_selector = "h1.entry-title"
            series_artist_selector = "div.tsinfo.bixbox div:nth-child(5) i"
            series_author_selector = "div.tsinfo.bixbox div:nth-child(4) i"
            series_description_selector = "[itemprop='description']"
            series_alt_name_selector = ".alternative"
            series_genre_selector = "div.wd-full span a"
            series_status_selector = "div.tsinfo.bixbox div:nth-child(2) i"
            series_thumbnail_selector = "[itemprop='image'] img"
            series_chapters_selector = "#chapterlist li"

            manga_info["title"] = soup.select_one(series_title_selector).text.strip()
            manga_info["altTitles"] = (
                [
                    alt.strip().replace("\n", " ")
                    for alt in soup.select_one(series_alt_name_selector).text.split("|")
                ]
                if soup.select_one(series_alt_name_selector)
                else []
            )
            manga_info["description"] = soup.select_one(
                series_description_selector
            ).text.strip()
            manga_info["headerForImage"] = {"Referer": self.base_url}
            manga_info["image"] = soup.select_one(series_thumbnail_selector)["src"]
            manga_info["releasedDate"] = soup.select_one(
                "div.tsinfo.bixbox div:nth-child(3) i"
            ).text.strip()
            manga_info["genres"] = [
                genre.text for genre in soup.select(series_genre_selector)
            ]
            manga_info["status"] = soup.select_one(series_status_selector).text.strip()
            manga_info["authors"] = (
                [
                    author.strip()
                    for author in soup.select_one(series_author_selector)
                    .text.replace("-", "")
                    .split(",")
                ]
                if soup.select_one(series_author_selector)
                else []
            )
            manga_info["artist"] = (
                soup.select_one(series_artist_selector).text.strip()
                if soup.select_one(series_artist_selector)
                else "N/A"
            )
            manga_info["serialization"] = soup.select_one(
                "div.tsinfo.bixbox div:nth-child(6) i"
            ).text.strip()
            manga_info["chapters"] = [
                {
                    "id": (
                        el.select_one("a")["href"].split("/")[3]
                        if el.select_one("a")
                        else ""
                    ),
                    "title": el.select_one(".lch a, .chapternum")
                    .text.strip()
                    .replace("\n", " "),
                    "releasedDate": el.select_one(".chapterdate").text,
                }
                for el in soup.select(series_chapters_selector)
            ]
            print(soup.select("div.listupd div div a"))
            manga_info["similar_series"] = []
            for el in soup.select(".listupd .bs .bsx a"):
                rating_el = el.select_one(".rt .numscore")
                rating = rating_el.text.strip() if rating_el else None
                
                status_el = el.select_one(".status i")
                status = status_el.text.strip() if status_el else None
                
                similar = {
                    "id": el.get("href", "").split("/series/")[1].replace("/", ""),
                    "title": el.select_one(".tt").text.strip() if el.select_one(".tt") else "",
                    "image": el.select_one("img").get("src", "") if el.select_one("img") else "",
                    "rating": rating,
                    "status": status
                }
                manga_info["similar_series"].append(similar)

            return manga_info
        except requests.HTTPError as e:
            raise ValueError(f"HTTP Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")

    def fetch_chapter_pages(self, chapter_id: str) -> List[Dict]:
        try:
            html_data = self._get_request(f"/{chapter_id}")
            soup = BeautifulSoup(html_data, "html.parser")

            page_selector = "div#readerarea img, #readerarea div.figure_container div.composed_figure"
            pages = [
                {
                    "img": el["src"],
                    "page": i+1,
                    "headerForImage": {"Referer": self.base_url},
                }
                for i, el in enumerate(soup.select(page_selector))
            ]

            return pages
        except requests.HTTPError as e:
            raise ValueError(f"HTTP Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")