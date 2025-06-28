import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Union


class AsuraScans:
    def __init__(self):
        self.name = "AsuraScans"
        self.base_url = "https://asuracomic.net"
        self.logo = "https://asuracomic.net/images/logo.png"
        self.class_path = "MANGA.AsuraScans"

    def fetch_manga_info(self, manga_id: str) -> Dict:
        try:
            response = requests.get(f"{self.base_url}/series/{manga_id}")
            soup = BeautifulSoup(response.text, "html.parser")

            info = {
                "id": manga_id,
                "title": soup.select_one(
                    ".text-white.cursor-pointer.text-sm.shrink-0"
                ).text.strip(),
                "image": soup.select_one("img.rounded.mx-auto")["src"].strip(),
                "cover": soup.select("img")[2]["src"].strip(),
                "description": soup.select_one('meta[name="description"]')[
                    "content"
                ].strip(),
                "status": (
                    soup.select("div.px-2.py-2.flex.items-center.justify-between h3")[
                        1
                    ].text.strip()
                ),
                "serialization": (
                    soup.select(
                        ".grid.grid-cols-1.md\:grid-cols-2.gap-5.mt-8 > div:nth-child(1) > h3"
                    )[-1].text.strip()
                ),
                "authors": [
                    author.strip()
                    for author in (
                        soup.select_one(
                            ".grid.grid-cols-1.gap-5.mt-8 div:nth-child(2) h3:nth-child(2)"
                        )
                        .text.strip()
                        .split("/")
                        if soup.select_one(
                            ".grid.grid-cols-1.gap-5.mt-8 div:nth-child(2) h3:nth-child(2)"
                        )
                        else []
                    )
                ],
                "type": (
                    soup.select("div.px-2.py-2.flex.items-center.justify-between h3")[
                        -1
                    ].text.strip()
                ),
                "artist": (
                    soup.select_one(
                        ".grid.grid-cols-1.gap-5.mt-8 div:nth-child(3) h3:nth-child(2)"
                    ).text.strip()
                ),
                "genres": [
                    genre.text.strip()
                    for genre in soup.select('button[class*="bg-themecolor"]')
                ],
                "chapters": [
                    {
                        "id": chapter["href"].split("/")[-1],
                        "title": soup.select_one(
                            "h3.text-sm.text-white.font-medium a span"
                        ).text.strip(),
                        "chapter": chapter.text.replace("Chapter", "")
                        .strip()
                        .split()[0],
                        "date": chapter.find_next("h3", class_="text-xs").text.strip(),
                    }
                    for chapter in soup.select(
                        'div[class*="border rounded-md group"] h3.text-sm.text-white a'
                    )
                ],
                "related_series": [
                    {
                        "id": related_series["href"].split("/")[-1],
                        "title": related_series.select_one(
                            "div > h2.font-bold"
                        ).text.strip(),
                        "image": related_series.select_one("div > div > img")["src"],
                        "latestChapter": related_series.select_one(
                            "div > h2:nth-child(3)"
                        ).text.strip(),
                        "status": related_series.select_one(
                            "div > div:nth-child(1) > span"
                        ).text.strip(),
                        "rating": related_series.select_one(
                            "div > div.block > span > label"
                        ).text.strip(),
                    }
                    for related_series in soup.select(".grid.grid-cols-2.gap-3.p-4 > a")
                ],
            }

            return info
        except Exception as e:
            raise RuntimeError(f"Error fetching manga info: {str(e)}")

    def fetch_chapter_pages(self, chapter_id: str) -> List[Dict[str, Union[str, int]]]:
        try:
            response = requests.get(f"{self.base_url}/series/{chapter_id}")
            soup = BeautifulSoup(response.text, "html.parser")

            pages = [
                {
                    "img": img["src"],
                    "page": index + 1,
                }
                for index, img in enumerate(soup.select(".w-full.mx-auto.center > img"))
            ]

            return pages
        except Exception as e:
            raise RuntimeError(f"Error fetching chapter pages: {str(e)}")

    def search(self, query: str, page: int = 1) -> Dict:
        try:
            formatted_query = query.lower()
            response = requests.get(
                f"{self.base_url}/series?page={page}&name={formatted_query}"
            )
            soup = BeautifulSoup(response.text, "html.parser")

            results = [
                {
                    "id": result["href"].replace("series/", ""),
                    "title": result.select_one(
                        "div > div > div:nth-child(2) > span:nth-child(1)"
                    ).get_text(strip=True),
                    "image": result.select_one("div > div > div:nth-child(1) > img")[
                        "src"
                    ],
                    "status": result.select_one(
                        "div > div > div:nth-child(1) > span"
                    ).get_text(strip=True),
                    "latestChapter": result.select_one(
                        "div > div > div:nth-child(2) > span:nth-child(2)"
                    ).get_text(strip=True),
                    "rating": result.select_one(
                        "div > div > div:nth-child(2) > span:nth-child(3) > label"
                    ).get_text(strip=True),
                }
                for result in soup.select(".grid.grid-cols-2.gap-3.p-4 > a")
            ]

            search_results = {
                "currentPage": page,
                "hasNextPage": "pointer-events:auto"
                in soup.select_one(".flex.items-center.justify-center > a")["style"],
                "results": results,
            }

            return search_results
        except Exception as e:
            raise RuntimeError(f"Error performing search: {str(e)}")

