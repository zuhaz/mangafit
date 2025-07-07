import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


class WeebCentral:
    def __init__(self):
        self.name = "WeebCentral"
        self.base_url = "https://weebcentral.com/"
        self.logo = "NONE"
        self.class_path = "MANGA.WeebCentral"
        self.headers = {
            "User-Agent": "Mozilla/5.0",
        }

    def _get_request(self, url: str) -> str:
        response = requests.get(f"{self.base_url}{url}", headers=self.headers)
        response.raise_for_status()
        return response.text
    
    def fetch_manga_info(self, manga_id: str) -> Dict:
        manga_info = {
            "id": manga_id,
            "title": "",
            "description": "",
            "cover_url": "",
            "status": "",
            "type": "",
            "released": "",
            "authors": [],
            "tags": [],
            "chapters": []
        }
        try:
            html_data = self._get_request(f"/series/{manga_id}")
            soup = BeautifulSoup(html_data, "html.parser")

            # Extract title
            title_element = soup.select_one("h1.text-2xl.font-bold")
            if title_element:
                manga_info["title"] = title_element.text.strip()

            # Extract cover image
            cover_element = soup.select_one("section.flex.items-center.justify-center picture img")
            if cover_element and "src" in cover_element.attrs:
                manga_info["cover_url"] = cover_element["src"]

            # Extract description
            description_element = soup.select_one("li p.whitespace-pre-wrap")
            if description_element:
                manga_info["description"] = description_element.text.strip()

            # Extract status
            status_element = soup.select_one("li strong:-soup-contains('Status:') + a")
            if status_element:
                manga_info["status"] = status_element.text.strip()

            # Extract type
            type_element = soup.select_one("li strong:-soup-contains('Type:') + a")
            if type_element:
                manga_info["type"] = type_element.text.strip()

            # Extract released year
            released_element = soup.select_one("li strong:-soup-contains('Released:') + span")
            if released_element:
                manga_info["released"] = released_element.text.strip()

            # Extract authors
            author_elements = soup.select("li strong:-soup-contains('Author') + span a")
            if author_elements:
                manga_info["authors"] = [author.text.strip() for author in author_elements]

            # Extract tags
            tag_elements = soup.select("li strong:-soup-contains('Tags') ~ span a")
            if tag_elements:
                manga_info["tags"] = [tag.text.strip() for tag in tag_elements]

            # Extract chapters
            chapter_elements = soup.select("#chapter-list .flex.items-center a")
            chapters = []
            for chapter in chapter_elements:
                chapter_url = chapter.get("href", "")
                if chapter_url:
                    chapter_id = chapter_url.split("/")[-1]
                    chapter_title = chapter.select_one("span.grow span").text.strip() if chapter.select_one("span.grow span") else ""
                    chapter_time = chapter.select_one("time").get("datetime", "") if chapter.select_one("time") else ""
                    
                    chapters.append({
                        "id": chapter_id,
                        "title": chapter_title,
                        "date": chapter_time
                    })
            
            manga_info["chapters"] = chapters

            return manga_info
        except requests.HTTPError as e:
            raise ValueError(f"HTTP Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")

    def search(
        self, query: str) -> Dict:
        try:

            headers = {
                'Hx-Trigger': 'quick-search-input',
                'Hx-Trigger-Name': 'text',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Accept-Language': 'en-US,en;q=0.9',
                'Hx-Target': 'quick-search-result',
                'Hx-Current-Url': 'https://weebcentral.com/',
                'Sec-Ch-Ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Hx-Request': 'true',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://weebcentral.com',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': 'https://weebcentral.com/',
                'Priority': 'u=1, i',
            }

            params = {
                'location': 'main',
            }

            data = {
                'text': str(query),
            }

            html_data = requests.post(
                'https://weebcentral.com/search/simple',
                params=params,
                headers=headers,
                data=data,
                verify=False,
            ).text         
            soup = BeautifulSoup(html_data, "html.parser")

            results = []
            for el in soup.select("a.btn.join-item.h-20"):
                link = el['href']
                img = el.select_one("div.w-12.h-12.overflow-hidden picture img")['src']
                results.append(
                    {
                        "id": link.split("/series/")[-1] if link else "",
                        "title": (
                            el.select_one("div.flex-1.overflow-hidden.text-left.text-ellipsis.leading-normal.line-clamp-2").text.strip()
                            if el.select_one("div.flex-1.overflow-hidden.text-left.text-ellipsis.leading-normal.line-clamp-2")
                            else ""
                        ),
                        "image": img if img else "",
                        "headerForImage": {
                            "Referer": self.base_url
                        },
                    }
                )

            return {"results": results}
        except requests.HTTPError as e:
            raise ValueError(f"HTTP Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")

    def fetch_chapter_pages(self, chapter_id: str) -> List[Dict]:
        try:
            html_data = self._get_request(f"chapters/{chapter_id}/images?is_prev=False&current_page=1&reading_style=long_strip")
            soup = BeautifulSoup(html_data, "html.parser")
            page_selector = "img.maw-w-full.mx-auto"
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