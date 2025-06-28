import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Union


class MediaStatus:
    COMPLETED = "completed"
    ONGOING = "ongoing"


class VyvyMangaSearchResultData:
    def __init__(
        self,
        authors: List[Dict],
        completed: int,
        created_at: str,
        description: str,
        id: int,
        lastChapter: str,
        latest_chapter_id: int,
        main_manga_id: Union[int, None],
        name: str,
        name_url: str,
        scored: int,
        status: int,
        thumbnail: str,
        title: str,
        updated_at: str,
        viewed: int,
        voted: int,
    ):
        self.authors = authors
        self.completed = completed
        self.created_at = created_at
        self.description = description
        self.id = id
        self.lastChapter = lastChapter
        self.latest_chapter_id = latest_chapter_id
        self.main_manga_id = main_manga_id
        self.name = name
        self.name_url = name_url
        self.scored = scored
        self.status = status
        self.thumbnail = thumbnail
        self.title = title
        self.updated_at = updated_at
        self.viewed = viewed
        self.voted = voted


class VyvyManga:
    name = "Vyvymanga"
    base_url = "https://vyvymanga.net/api"
    logo = "https://vyvymanga.net/web/img/icon.png"
    class_path = "MANGA.VyvyManga"
    base_website_url = "https://vymanga.com"

    def __init__(self):
        self.session = requests.Session()

    def search(self, query: str, page: int = 1) -> Dict:
        if page < 1:
            raise ValueError("Page must be equal to 1 or greater")

        try:
            formatted_query = query.strip().lower().replace(" ", "+")
            response = self.session.get(
                f"{self.base_website_url}/search?search_po=0&q={formatted_query}&page={page}"
            )
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, "html.parser")
        
            manga_items = soup.select(".row.book-list .comic-item a")
            print("Manga items: ", manga_items[0])
            result = []
            for elem in manga_items:
                image_tag = elem.select("div.comic-image img")[0]
                
                image_url = image_tag['data-src']
                print("image url:", image_url)
                
                id_parts = image_url.split("cover/")
                manga_id = id_parts[1].split("/")[0] if len(id_parts) > 1 else ""
                
                title_tag = elem.select("div.comic-title")[0]
                title = title_tag.text.strip() if title_tag else ""
                
                last_chap_tag = elem.select("div.comic-image span.tray-item")[0]
                last_chapter = last_chap_tag.text.strip() if last_chap_tag else ""
                
                result.append({
                    "id": manga_id,
                    "title": title,
                    "image": image_url,
                    "lastChapter": last_chapter,
                })
            
            
            pagination = soup.select("ul.pagination > li")
            has_next_page = False
            total_pages = page  
            
            if pagination:
                last_page_li = pagination[-2]
                last_page = int(last_page_li.find("a").text.strip())
                total_pages = last_page
                has_next_page = page < last_page
            
            return {
                "currentPage": page,
                "hasNextPage": has_next_page,
                "totalPages": total_pages,
                "results": result,
            }
        except requests.RequestException as e:
            raise SystemExit(e)
        
    def fetch_manga_info(self, manga_id: str) -> Dict:
        try:
            response = self.session.get(
                f"{self.base_website_url}/manga/{manga_id}",
                headers={
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "Referer": f"{self.base_website_url}/",
                },
            )
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, "html.parser")

            with open("vyvy_manga_info.html", "w", encoding="utf-8") as f:
                f.write(data)

            div = soup.select_one('.col-md-7')
            if not div:
                raise ValueError("Could not find the main manga info div")

            title_element = div.select_one('.title')
            title = title_element.text.strip() if title_element else "Unknown Title"

            img_element = div.select_one('.img-manga img')
            img = img_element['src'] if img_element else "No Image"

            authors = [
                ele.text.strip()
                for ele in div.select('p:has(span.pre-title:contains("Authors")) a')
            ]

            status_element = div.select_one('p:has(span.pre-title:contains("Status")) span.text-ongoing')
            status = status_element.text.strip() if status_element else "Unknown Status"

            genres = [
                ele.text.strip()
                for ele in div.select('p:has(span.pre-title:contains("Genres")) a')
            ]

            description_element = soup.select_one('.summary > .content')
            description = description_element.text.strip() if description_element else "No Description"

            chapters = [
                {
                    "id": ele["href"],
                    "title": ele.text.replace(ele.find("p").text.strip(), "").strip(),
                    "releaseDate": ele.find("p").text.strip(),
                }
                for ele in soup.select(".list-group > a")
            ][::-1]

            return {
                "id": manga_id,
                "title": title,
                "img": img,
                "authors": authors,
                "status": status,
                "genres": genres,
                "description": description,
                "chapters": chapters,
            }
        except requests.RequestException as e:
            raise SystemExit(e)

    def fetch_chapter_pages(self, chapter_id: str) -> List[Dict]:
        try:
            response = self.session.get(chapter_id)
            response.raise_for_status()
            data = response.text
            soup = BeautifulSoup(data, "html.parser")

            images = [
                {"img": img["data-src"][:-5], "page": index + 1}
                for index, img in enumerate(
                    soup.select(".vview.carousel-inner > div > img")
                )
            ]
            return images
        except requests.RequestException as e:
            raise SystemExit(e)