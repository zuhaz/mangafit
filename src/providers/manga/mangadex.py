import requests
from typing import List, Dict, Optional
from urllib.parse import quote

import json
import aiohttp

def capitalize_first_letter(string: str) -> str:
    if not string:
        return string
    return string[0].upper() + string[1:]

def substring_before(string: str, delimiter: str) -> str:
    if delimiter in string:
        return string.split(delimiter)[0]
    return string

class MangaDex:
    def __init__(self):
        self.name = 'MangaDex'
        self.base_url = 'https://mangadex.org'
        self.logo = 'https://pbs.twimg.com/profile_images/1391016345714757632/xbt_jW78_400x400.jpg'
        self.class_path = 'MANGA.MangaDex'
        self.api_url = 'https://api.mangadex.org'
        self.client = requests.Session()

    async def fetch_manga_info(self, manga_id: str) -> Dict:
        try:
            response = self.client.get(f'{self.api_url}/manga/{manga_id}')
            data = response.json()

            # Get the primary title, falling back to first available title
            titles = data['data']['attributes']['title']
            title = titles.get('en') or next(iter(titles.values()))

            # Find cover art relationship and fetch image first
            find_cover_art = next(
                (rel for rel in data['data']['relationships'] if rel['type'] == 'cover_art'), 
                None
            )
            cover_art = await self.fetch_cover_image(
                find_cover_art['id'] if find_cover_art else None
            )
            
            # Create manga_info with reordered fields
            manga_info = {
                'id': data['data']['id'],
                'title': title,
                'image': f'{self.base_url}/covers/{data["data"]["id"]}/{cover_art}' if cover_art else None,
                'altTitles': data['data']['attributes']['altTitles'],
                'descriptions': data['data']['attributes']['description'],
                'genres': [
                    tag['attributes']['name']['en']
                    for tag in data['data']['attributes']['tags']
                    if tag['attributes']['group'] == 'genre'
                ],
                'themes': [
                    tag['attributes']['name']['en']
                    for tag in data['data']['attributes']['tags']
                    if tag['attributes']['group'] == 'theme'
                ],
                'status': capitalize_first_letter(data['data']['attributes']['status']),
                'releaseDate': data['data']['attributes']['year'],
                'chapters': []
            }

            manga_info['chapters'] = await self.fetch_all_chapters(manga_id, 0, None)
            return manga_info

        except requests.RequestException as err:
            if hasattr(err, 'response') and err.response.status_code == 400:
                raise ValueError(f'[{self.name}] Bad request. Make sure you have entered a valid query.')
            raise

    async def fetch_chapter_pages(self, chapter_id: str) -> List[Dict]:
        try:
            response = self.client.get(f'{self.api_url}/at-home/server/{chapter_id}')
            data = response.json()
            
            pages = [
                {
                    'img': f'{data["baseUrl"]}/data/{data["chapter"]["hash"]}/{image_name}',
                    'page': idx + 1
                }
                for idx, image_name in enumerate(data['chapter']['data'])
            ]
            return pages
        except requests.RequestException as err:
            raise

    async def search(
        self, query: str, page: int = 1, limit: int = 20
    ) -> List[Dict]:
        if page <= 0:
            raise ValueError('Page number must be greater than 0')
        if limit > 100:
            raise ValueError('Limit must be less than or equal to 100')
        if limit * (page - 1) >= 10000:
            raise ValueError('not enough results')

        try:
            response = self.client.get(
                f'{self.api_url}/manga?limit={limit}&title={quote(query)}&offset={limit * (page - 1)}&order[relevance]=desc'
            )
            data = response.json()
            
            if data['result'] == 'ok':
                results = {
                    'currentPage': page,
                    'results': []
                }

                for manga in data['data']:
                    find_cover_art = next(
                        (item for item in manga['relationships'] if item['type'] == 'cover_art'), None
                    )
                    cover_art_id = find_cover_art.get('id') if find_cover_art else None
                    cover_art = await self.fetch_cover_image(cover_art_id)

                    results['results'].append({
                        'id': manga['id'],
                        'title': list(manga['attributes']['title'].values())[0],
                        'altTitles': manga['attributes']['altTitles'],
                        'description': list(manga['attributes']['description'].values())[0],
                        'status': manga['attributes']['status'],
                        'releaseDate': manga['attributes']['year'],
                        'contentRating': manga['attributes']['contentRating'],
                        'lastVolume': manga['attributes']['lastVolume'],
                        'lastChapter': manga['attributes']['lastChapter'],
                        'image': f'{self.base_url}/covers/{manga["id"]}/{cover_art}',
                    })

                return results
            else:
                raise ValueError(data['message'])
        except requests.RequestException as err:
            if err.response.status_code == 400:
                raise ValueError('Bad request. Make sure you have entered a valid query.')
            raise

    async def fetch_random(self) -> List[Dict]:
        try:
            response = self.client.get(f'{self.api_url}/manga/random')
            data = response.json()

            if data['result'] == 'ok':
                results = {
                    'currentPage': 1,
                    'results': []
                }

                find_cover_art = next(
                    (item for item in data['data']['relationships'] if item['type'] == 'cover_art'), None
                )
                cover_art_id = find_cover_art.get('id') if find_cover_art else None
                cover_art = await self.fetch_cover_image(cover_art_id)

                results['results'].append({
                    'id': data['data']['id'],
                    'title': list(data['data']['attributes']['title'].values())[0],
                    'altTitles': data['data']['attributes']['altTitles'],
                    'description': list(data['data']['attributes']['description'].values())[0],
                    'status': data['data']['attributes']['status'],
                    'releaseDate': data['data']['attributes']['year'],
                    'contentRating': data['data']['attributes']['contentRating'],
                    'lastVolume': data['data']['attributes']['lastVolume'],
                    'lastChapter': data['data']['attributes']['lastChapter'],
                    'image': f'{self.base_url}/covers/{data["data"]["id"]}/{cover_art}',
                })

                return results
            else:
                raise ValueError(data['message'])
        except requests.RequestException as err:
            raise

    async def fetch_recently_added(self, page: int = 1, limit: int = 20) -> List[Dict]:
        if page <= 0:
            raise ValueError('Page number must be greater than 0')
        if limit > 100:
            raise ValueError('Limit must be less than or equal to 100')
        if limit * (page - 1) >= 10000:
            raise ValueError('not enough results')

        try:
            response = self.client.get(
                f'{self.api_url}/manga?includes[]=cover_art&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&order[createdAt]=desc&hasAvailableChapters=true&limit={limit}&offset={limit * (page - 1)}'
            )
            data = response.json()

            if data['result'] == 'ok':
                results = {
                    'currentPage': page,
                    'results': []
                }

                for manga in data['data']:
                    find_cover_art = next(
                        (item for item in manga['relationships'] if item['type'] == 'cover_art'), None
                    )
                    cover_art_id = find_cover_art.get('id') if find_cover_art else None
                    cover_art = await self.fetch_cover_image(cover_art_id)

                    results['results'].append({
                        'id': manga['id'],
                        'title': list(manga['attributes']['title'].values())[0],
                        'altTitles': manga['attributes']['altTitles'],
                        'description': list(manga['attributes']['description'].values())[0],
                        'status': manga['attributes']['status'],
                        'releaseDate': manga['attributes']['year'],
                        'contentRating': manga['attributes']['contentRating'],
                        'lastVolume': manga['attributes']['lastVolume'],
                        'lastChapter': manga['attributes']['lastChapter'],
                        'image': f'{self.base_url}/covers/{manga["id"]}/{cover_art}',
                    })

                return results
            else:
                raise ValueError(data['message'])
        except requests.RequestException as err:
            raise

    async def fetch_latest_updates(self, page: int = 1, limit: int = 20) -> List[Dict]:
        if page <= 0:
            raise ValueError('Page number must be greater than 0')
        if limit > 100:
            raise ValueError('Limit must be less than or equal to 100')
        if limit * (page - 1) >= 10000:
            raise ValueError('not enough results')

        try:
            response = self.client.get(
                f'{self.api_url}/manga?includes[]=cover_art&order[updatedAt]=desc&hasAvailableChapters=true&limit={limit}&offset={limit * (page - 1)}'
            )
            data = response.json()
            print(data)

            if data['result'] == 'ok':
                results = {
                    'currentPage': page,
                    'results': []
                }

                for manga in data['data']:
                    find_cover_art = next(
                        (item for item in manga['relationships'] if item['type'] == 'cover_art'), None
                    )
                    cover_art_id = find_cover_art.get('id') if find_cover_art else None
                    cover_art = await self.fetch_cover_image(cover_art_id)

                    results['results'].append({
                        'id': manga['id'],
                        'title': list(manga['attributes']['title'].values())[0],
                        'altTitles': manga['attributes']['altTitles'],
                        'description': list(manga['attributes']['description'].values())[0],
                        'status': manga['attributes']['status'],
                        'releaseDate': manga['attributes']['year'],
                        'contentRating': manga['attributes']['contentRating'],
                        'lastVolume': manga['attributes']['lastVolume'],
                        'lastChapter': manga['attributes']['lastChapter'],
                        'image': f'{self.base_url}/covers/{manga["id"]}/{cover_art}',
                    })

                return results
            else:
                raise ValueError(data['message'])
        except requests.RequestException as err:
            raise

    async def fetch_cover_image(self, cover_id: Optional[str]) -> Optional[str]:
        if cover_id:
            try:
                response = self.client.get(f'{self.api_url}/cover/{cover_id}')
                data = response.json()
                return data['data']['attributes']['fileName']
            except requests.RequestException as err:
                raise
        return None

    async def fetch_all_chapters(self, manga_id: str, offset: int = 0, prev_response: dict = None) -> list:
        try:
            # Base case: stop when we've fetched all chapters
            if prev_response and prev_response['offset'] + 96 >= prev_response['total']:
                return []

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/manga/{manga_id}/feed",
                    params={
                        'offset': offset,
                        'limit': 96,
                        'order[volume]': 'desc',
                        'order[chapter]': 'desc',
                        'translatedLanguage[]': 'en'
                    }
                ) as response:
                    data = await response.json()

                    # Ensure response data exists and contains required properties
                    if not data or 'data' not in data:
                        raise ValueError('Invalid API response format')

                    # Extract only the required fields from each chapter
                    chapters = [
                        {
                            'id': chapter['id'],
                            'chapter': chapter['attributes']['chapter'],
                            'title': chapter['attributes']['title'],
                            'pages': chapter['attributes']['pages']
                        }
                        for chapter in data['data']
                    ]

                    return chapters + await self.fetch_all_chapters(
                        manga_id, 
                        offset + 96, 
                        data
                    )

        except Exception as e:
            print(f"Error fetching chapters for manga {manga_id} at offset {offset}: {str(e)}")
            raise
