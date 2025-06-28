import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import json
class Bato:
    def __init__(self):
        self.name = "Bato"
        self.base_url = "https://bato.to"
        self.client = requests.Session()
        self.client.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def fetch_manga_info(self, manga_id: str) -> Dict:
        manga_info = {
            "id": manga_id,
            "title": "Unknown Title",
            "image": "No Image",
            "description": "No Description",
            "authors": ["Unknown Author"],
            "genres": ["Unknown Genre"],
            "publication_status": "Unknown",
            "original_language": "Unknown",
            "translated_language": "Unknown",
            "rating": 0.0,
            "upload_date": "Unknown",
            "alt_titles": [],
            "chapters": [],
        }

        url = f"{self.base_url}/title/{manga_id}"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            title_element = soup.select_one("h3.text-lg.md\\:text-2xl.font-bold a")
            if title_element:
                manga_info["title"] = title_element.text.strip()

            image_element = soup.select_one("img.w-full.not-prose")
            if image_element and "src" in image_element.attrs:
                manga_info["image"] = image_element["src"]

            description_element = soup.select_one("div.limit-html-p")
            if description_element:
                manga_info["description"] = description_element.text.strip()

            authors_element = soup.select_one("a[href*='v3x-search?word=']")
            if authors_element:
                manga_info["authors"] = [authors_element.text.strip()]

            genres_elements = soup.select("span.font-bold")
            if genres_elements:
                manga_info["genres"] = [genre.text.strip() for genre in genres_elements]

            chapters_elements = soup.select("a.link-hover.link-primary.visited\\:text-accent")
            if chapters_elements:
                manga_info["chapters"] = [
                    {
                        "id": el['href'].replace("/title", ""),
                        "title": el.text.strip(),
                    }
                    for el in chapters_elements
                ]

            alt_titles_elements = soup.select("div.mt-1.text-xs.md\\:text-base.opacity-80 span")
            if alt_titles_elements:
                manga_info["alt_titles"] = [title.text.strip() for title in alt_titles_elements]

            pub_status_element = soup.select_one("span.font-bold.uppercase.text-warning")
            if pub_status_element:
                manga_info["publication_status"] = pub_status_element.text.strip()

            lang_elements = soup.select("div.whitespace-nowrap.overflow-hidden span")
            if lang_elements and len(lang_elements) >= 2:
                manga_info["original_language"] = lang_elements[1].text.strip()
                manga_info["translated_language"] = lang_elements[0].text.strip()

            rating_element = soup.select_one("div.inline-flex.relative.text-xs.md\\:text-sm")
            if rating_element:
                rating_text = rating_element.text.strip()
                try:
                    manga_info["rating"] = float(rating_text.split()[0])
                except (ValueError, IndexError):
                    pass


            upload_date_element = soup.select_one("time")
            if upload_date_element and "time" in upload_date_element.attrs:
                manga_info["upload_date"] = upload_date_element["time"]

            return manga_info

        except requests.RequestException as e:
            raise SystemExit(f"Request failed: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing manga info: {e}")
            
    def fetch_chapter_pages(self, chapter_id: str) -> List[Dict]:
        try:
            url = f"{self.base_url}/title/{chapter_id}"
            response = self.client.get(url, headers={'Referer': url})
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            astro_island = soup.find("astro-island", {"uid": "Z1HVi0v"})
            if not astro_island:
                raise ValueError("Could not find the <astro-island> component.")

            props = astro_island.get("props")
            if not props:
                raise ValueError("Missing 'props' attribute.")

            props_data = json.loads(props)
            image_files = props_data.get("imageFiles", [])

            if not isinstance(image_files, list) or len(image_files) < 2:
                raise ValueError("Invalid imageFiles structure")

            image_entries_str = image_files[1]
            image_entries = json.loads(image_entries_str)

            image_urls = []
            for entry in image_entries:
                if isinstance(entry, list) and len(entry) >= 2:
                    img_url = entry[1]
                    image_urls.append(img_url)

            pages = [
                {
                    "img": img_url,
                    "title": f"Page {i + 1}",
                    "headerForImage": {"Referer": url}
                }
                for i, img_url in enumerate(image_urls)
            ]

            return pages

        except requests.HTTPError as e:
            raise ValueError(f"HTTP Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")
        
    def search(self, query: str, page=1) -> Dict:
        try:
            search_res = {"currentPage": page, "results": [], "hasNextPage": False}
            
            # Make the request to Batoto's search endpoint
            url = f"https://bato.to/search?word={query.replace(' ', '+')}&page={page}"
            response = self.client.get(url)
            response.raise_for_status()  # Check for HTTP errors
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, "html.parser")
            
            results = []
            for el in soup.select('div.series-list > div.item'):
                try:
                    # Extract basic info
                    item = {
                        "id": el.select_one('a.item-cover')['href'].split('/')[-1],
                        "title": el.select_one('a.item-title').get_text(strip=True),
                        "image": el.select_one('img')['src'],
                        "authors": [],
                        "last_updated": None,
                        "language": None
                    }

                    # Extract authors from item-alias divs
                    alias_divs = el.select('div.item-alias')
                    if len(alias_divs) >= 2:
                        authors = alias_divs[1].get_text(strip=True)
                        item["authors"] = [a.strip() for a in authors.split(',')]

                    # Extract language from flag
                    flag = el.select_one('em.eflag')
                    if flag and 'data-lang' in flag.attrs:
                        item["language"] = flag['data-lang']

                    # Extract last updated time
                    time_element = el.select_one('div.item-volch i')
                    if time_element:
                        item["last_updated"] = time_element.get_text(strip=True)

                    results.append(item)
                except Exception as e:
                    print(f"Error parsing item: {e}")
                    continue

            search_res["results"] = results

            # Pagination detection
            pagination = soup.select('ul.pagination')
            if pagination:
                page_items = pagination[0].select('li.page-item')
                last_page_item = page_items[-1]
                
                if 'disabled' not in last_page_item.get('class', []):
                    search_res["hasNextPage"] = True
                else:
                    current_page = None
                    for item in page_items:
                        if 'active' in item.get('class', []):
                            current_page = int(item.text.strip())
                            break
                    
                    if current_page:
                        search_res["hasNextPage"] = any(
                            int(li.text.strip()) > current_page 
                            for li in page_items 
                            if li.text.strip().isdigit()
                        )

            return search_res

        except requests.HTTPError as e:
            raise ValueError(f"HTTP Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")