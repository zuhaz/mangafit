import requests
from bs4 import BeautifulSoup
from typing import List, Dict

class Manganato:
    def __init__(self):
        self.name = "Manganato"
        self.base_url = "https://chapmanganato.to"
        self.logo = "https://techbigs.com/uploads/2022/1/mangakakalot-apkoptimized.jpg"
        self.headers = {
            "User-Agent": "Mozilla/5.0",
        }

    def _get_request(self, url: str) -> str:
        try:
            response = requests.get(
                url, 
                headers=self.headers,
                timeout=(5, 10)  # (connect timeout, read timeout)
            )
            response.raise_for_status()
            return response.text
        except requests.Timeout:
            raise ValueError(f"Connection timed out while accessing {url}. The server might be down or blocking requests.")
        except requests.ConnectionError:
            raise ValueError(f"Failed to connect to {url}. Please check your internet connection or the website might be down.")

    def fetch_manga_info(self, manga_id: str) -> Dict:
        manga_info = {
            "id": manga_id,
            "title": "",
        }
        url = manga_id if 'read' in manga_id else f'https://chapmanganato.to/{manga_id}'
        try:
            html_data = self._get_request(url)
            soup = BeautifulSoup(html_data, "html.parser")
            manga_info["title"] = soup.select_one('div.panel-story-info > div.story-info-right > h1').text
            manga_info["altTitles"] = soup.select_one('div.story-info-right > table > tbody > tr:nth-child(1) > td.table-value > h2').text.split(';')
            manga_info["description"] = soup.select_one('#panel-story-info-description').text.replace('Description :', '').replace('\n', '').strip()
            manga_info["image"] = soup.select_one('div.story-info-left > span.info-image > img')['src']
            manga_info["genres"] = [genre.text for genre in soup.select('div.story-info-right > table > tbody > tr:nth-child(4) > td.table-value > a')]
            
            status_text = soup.select_one('div.story-info-right > table > tbody > tr:nth-child(3) > td.table-value').text.strip()
            manga_info["status"] = {
                'Completed': 'COMPLETED',
                'Ongoing': 'ONGOING'
            }.get(status_text, 'UNKNOWN')
            manga_info["views"] = soup.select_one('div.story-info-right > div > p:nth-child(2) > span.stre-value').text.replace(',', '').strip()
            manga_info["authors"] = [author.text for author in soup.select('div.story-info-right > table > tbody > tr:nth-child(2) > td.table-value > a')]
            
            manga_info["chapters"] = [
                {
                    "id": el.select_one('a')['href'].split('/')[-1],
                    "title": el.select_one('a').text,
                    "views": el.select_one('span.chapter-view.text-nowrap').text.replace(',', '').strip(),
                    "releasedDate": el.select_one('span.chapter-time.text-nowrap')['title'],
                }
                for el in soup.select('div.container-main-left > div.panel-story-chapter-list > ul > li')
            ]

            return manga_info
        except requests.HTTPError as e:
            raise ValueError(f"HTTP Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")

    def fetch_chapter_pages(self, chapter_id: str) -> List[Dict]:
        try:
            url = f"{self.base_url}/{chapter_id}" if '$$READMANGANATO' not in chapter_id else f"https://readmanganato.com/{chapter_id.replace('$$READMANGANATO', '')}"
            print(url)
            html_data = self._get_request(url)
            soup = BeautifulSoup(html_data, "html.parser")
            with open("chapter_pages.html", "w", encoding="utf-8") as f:
                f.write(html_data)

            pages = [
                {
                    "img": el['src'],
                    "page": i+1,
                    "title": el['alt'].replace(' - Mangakakalot.com', '').replace(' - MangaNato.com', '').strip(),
                    "headerForImage": {"Referer": url}
                }
                for i, el in enumerate(soup.select('div.container-chapter-reader > img'))
            ]

            return pages
        except requests.HTTPError as e:
            raise ValueError(f"HTTP Error: {str(e)}")
        except Exception as e:
                raise ValueError(f"Error: {str(e)}")
    def search(self, query: str, page=1) -> Dict:
        try:
            search_res = {"currentPage": page, "results": [], "hasNextPage": False}
            html_data = self._get_request(f"https://manganato.com/search/story/{query.replace(' ', '_')}?page={page}")
            soup = BeautifulSoup(html_data, "html.parser")
            with open('search.html', 'w', encoding='utf-8') as f:
                f.write(html_data)
            
            results = []
            for el in soup.select('div.search-story-item'):
                authors_element = el.select_one('div.item-right > span.text-nowrap.item-author')
                authors = authors_element.text.split(',') if authors_element else []
                
                result = {
                    "id": el.select_one('a')['href'].split('/')[-1],
                    "title": el.select_one('a')['title'],
                    "image": el.select_one('img')['src'],
                    "authors": authors,
                    "last_updated": el.select('div.item-right > span.text-nowrap.item-time')[0].text.replace('Updated : ', ''),
                    "views": el.select('div.item-right > span.text-nowrap.item-time')[-1].text.replace(',', ''),
                }
                results.append(result)
            
            search_res["results"] = results

            page_numbers = soup.select('div.group-page a')
            if page_numbers:
                last_page = page_numbers[-1]
                if 'LAST' in last_page.text:
                    last_page_num = int(last_page.text.split('(')[-1].split(')')[0])
                    search_res["hasNextPage"] = page < last_page_num
                else:
                    search_res["hasNextPage"] = any(int(a.text) > page for a in page_numbers if a.text.isdigit())

            return search_res
        except requests.HTTPError as e:
            raise ValueError(f"HTTP Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")