import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


class FlameComics:
    def __init__(self):
        self.name = "FlameComics"
        self.base_url = "https://flamecomics.xyz/"
        self.logo = "https://i.imgur.com/Nt1MW3H.png"
        self.class_path = "MANGA.FlameComics"
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
        }
        try:
            html_data = self._get_request(f"/series/{manga_id}")
            soup = BeautifulSoup(html_data, "html.parser")
            
            title_meta = soup.select_one("meta[property='og:title']")
            manga_info["title"] = title_meta["content"] if title_meta else ""
            
            desc_meta = soup.select_one("meta[property='og:description']")
            manga_info["description"] = desc_meta["content"].strip() if desc_meta else ""
            
            image_meta = soup.select_one("meta[property='og:image']")
            manga_info["image"] = image_meta["content"] if image_meta else ""
            manga_info["headerForImage"] = {"Referer": self.base_url}
            
            # Disputed: too lazy to fix atp 
            # status_badge = soup.select_one("div.mantine-Badge-root span.mantine-Badge-label")
            # manga_info["status"] = status_badge.text.strip() if status_badge else "Unknown"
            
            genre_badges = soup.select(".SeriesPage_badge__2tZ7A")
            manga_info["genres"] = [badge.text.strip() for badge in genre_badges] if genre_badges else []
            
            info_fields = soup.select(".SeriesPage_infoField__NWzAH")
            info_values = soup.select(".SeriesPage_infoValue__Ty4ck")
            
            for i, field in enumerate(info_fields):
                field_text = field.text.strip().lower()
                if i < len(info_values):
                    value_text = info_values[i].text.strip()
                    
                    if "artist" in field_text:
                        manga_info["artist"] = value_text
                    elif "author" in field_text:
                        manga_info["authors"] = [value_text]
                    elif "publisher" in field_text:
                        manga_info["serialization"] = value_text
                    elif "release year" in field_text:
                        manga_info["releasedDate"] = value_text
                    elif "type" in field_text:
                        manga_info["type"] = value_text
            
            # Extract chapters
            chapter_links = soup.select(".ChapterCard_chapterWrapper__j8pBx")
            chapters = []
            
            for link in chapter_links:
                chapter_title = link.select_one("p[data-line-clamp='true']")
                chapter_date = link.select_one("p[data-size='xs']")
                
                if chapter_title and link.get("href"):
                    chapter_id = link["href"].split("/")[-1] if link.get("href") else ""
                    title = chapter_title.text.strip()
                    date = chapter_date.text.strip() if chapter_date else ""
                    
                    chapters.append({
                        "id": "series/" + manga_id + "/"+ chapter_id,
                        "title": title,
                        "releasedDate": date
                    })
            
            manga_info["chapters"] = chapters
            
            # Set default values for missing fields
            if "artist" not in manga_info:
                manga_info["artist"] = "N/A"
            if "authors" not in manga_info:
                manga_info["authors"] = []
            if "serialization" not in manga_info:
                manga_info["serialization"] = "N/A"
            if "releasedDate" not in manga_info:
                manga_info["releasedDate"] = "N/A"
            
            return manga_info
        except requests.HTTPError as e:
            raise ValueError(f"HTTP Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")

    def fetch_chapter_pages(self, chapter_id: str) -> List[Dict]:
        try:
            html_data = self._get_request(f"/{chapter_id}")
            soup = BeautifulSoup(html_data, "html.parser")
            page_selector = "div.m_6d731127.mantine-Stack-root img"
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