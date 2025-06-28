import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import cloudscraper
import json
class Comick:
    def __init__(self):
        self.name = "Comick"
        self.base_url = "https://comick.io"
        self.scraper = cloudscraper.create_scraper(
            browser={
            "browser": "firefox",
            "platform": "windows",
            }, 
            interpreter="nodejs"
        )

    def fetch_manga_info(self, manga_id: str) -> Dict:
        manga_info = {
            "id": manga_id,
            "title": "Unknown Title",
            "image": "No Image",
            "description": "No Description",
            "status": "Unknown",
            "translation_status": "Unknown",
            "publish_date": "Unknown",
            "type": "Unknown",
            "genres": ["Unknown Genre"],
            "authors": ["Unknown Author"],
            "alt_titles": [],
            "chapters": [],
        }

        url = f"{self.base_url}/comic/{manga_id}?lang=en"
        try:
            response = self.scraper.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            info_elem_one = soup.select("div.md\:col-span-2.text-sm.md\:text-base")
            info_elem_two = soup.select("div.col-span-3.md\:col-span-2.text-sm.md\:text-base.space-y-5")
            title_tag = soup.find("h1")
            if title_tag:
                manga_info["title"] = title_tag.text.strip()

            image_tag = soup.find("meta", property="og:image")
            if image_tag:
                manga_info["image"] = image_tag["content"]

            desc_tag = soup.find("div", class_="comic-desc")
            if desc_tag:
                manga_info["description"] = desc_tag.text.strip()

            status_tag = info_elem_one[0].select("div")[7]
            if status_tag:
                manga_info["status"] = status_tag.find_next_sibling().text.strip().split(" ")[-1]

            translation_status_tag = info_elem_one[0].select("div")[7]
            if translation_status_tag:
                manga_info["translation_status"] = translation_status_tag.text.strip().split(" ")[-1]

            publish_date_tag = info_elem_one[0].select("div")[6].text.split(" ")[-1]
            if publish_date_tag:
                manga_info["publish_date"] = publish_date_tag

            type_tag = info_elem_one[0].select("div")[4].select("span")[-1].text.split(" ")[-1]
            if type_tag:
                manga_info["type"] = type_tag

            genres_tag = info_elem_two[0].select("table tr")[2].select("td")[-1].select("span a")
            if genres_tag:
                genres = [gen_item.text.strip() for gen_item in genres_tag]
                manga_info["genres"] = genres
           
            authors_tag =  info_elem_two[0].select("table tr")[1].select("td")[-1].select("span a")
            if authors_tag:
                authors = [auth_item.text.strip() for auth_item in authors_tag]
                manga_info["authors"] = authors
           
            manga_info["alt_titles"] = soup.select("div.text-gray-500.dark\:text-gray-400.overflow-auto.mt-3")[0].text.split(" • ")

            chapters_tag = self.fetch_chapters(json.loads(soup.find("script", {"id": "__NEXT_DATA__"}).string)['props']['pageProps']['comic']['hid'], referer=url)
            if chapters_tag:
                chapters = []
                for chapter in chapters_tag['chapters']:
                    chapters.append(
                        {
                            "id": chapter["hid"] + "-" "chapter-"+ chapter["chap"] + "-" + "en",
                            "num": chapter["chap"]
                        },
                    
                    )
                manga_info["chapters"] = chapters

            return manga_info

        except requests.RequestException as e:
            raise SystemExit(f"Request failed: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing manga info: {e}")
    
    def fetch_chapters(self, id: str, referer: str) -> List[Dict]:
        try:
            url = "https://api.comick.io/comic/" + id + "/chapters"
            response = self.scraper.get(url, headers= {"Referer": referer})
            response.raise_for_status()
            data = response.json()
            return data
        except requests.HTTPError as e:
            raise ValueError(f"HTTP Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")
            
    def fetch_chapter_pages(self, chapter_id: str) -> List[Dict]:
        try:
            url = f"{self.base_url}/comic/{chapter_id}"
            response = self.scraper.get(url, headers= {"Host": "api.comick.io"})
            response.raise_for_status()
            pages = []
            soup = BeautifulSoup(response.text, "html.parser")
            with open("comick_chapters.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            exit()
            return pages

        except requests.HTTPError as e:
            raise ValueError(f"HTTP Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")

    def search(self, query: str, limit=100) -> Dict:
        try:
            search_res = {"results": []}
            
            url = f"https://api.comick.io/v1.0/search?limit={limit}&q={query.replace(' ', '+')}"
            response = self.scraper.get(url)
            response.raise_for_status() 
            
            data = response.json()
            results = [
                {
                    "id": item["slug"],
                    "title": item["title"],
                    "image": f"https://meo.comick.pictures/{item['md_covers'][0]['b2key']}",
                    "description": item["desc"] if item["desc"] != "" else "No Description",
                }
                for item in data
            ]
            search_res["results"] = results
            return search_res

        except requests.HTTPError as e:
            raise ValueError(f"HTTP Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")