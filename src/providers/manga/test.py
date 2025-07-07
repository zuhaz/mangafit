from bato import Bato
from chapmanganato import Manganato
from comick import Comick
from mangapill import MangaPill
from asurascans import AsuraScans
from mangapark import Mangapark
from flamecomics import FlameComics
from weebcentral import WeebCentral
import asyncio
import json


def main():
    # Initialize the MangaReader instance
    bato = Bato()
    manganato = Manganato()
    mangapill = MangaPill()
    comick = Comick()
    asurascans = AsuraScans()
    mangapark = Mangapark()
    flamecomics = FlameComics()
    weebcentral = WeebCentral()
    # # Test search functionality
    # print("Searching for 'one piece'...")
    # search_results = manga_reader.search("one piece")
    # print("Search Results:")
    # print(search_results)

    # if search_results["results"]:
    #     # Get the first result ID
    #     manga_id = "one-piece-3"
    #     print(f"\nFetching manga info for ID: {manga_id}...")
    #     manga_info = manga_reader.fetch_manga_info("one-piece-3")
    #     print("Manga Info:")
    #     print(manga_info)

    #     if manga_info["chapters"]:
    #         # Get the first chapter ID
    #         chapter_id = "one-piece-colored-edition-55493/en/chapter-1004"
    #         print(f"\nFetching chapter pages for chapter ID: {chapter_id}...")
    #         chapter_pages = manga_reader.fetch_chapter_pages(chapter_id)
    #         print("Chapter Pages:")
    #         print(chapter_pages)
    #     else:
    #         print("No chapters found.")
    # else:
    #     print("No manga results found.")

    # chapter_id = "the-overpowered-veteran-healer/iCqYxsfA-chapter-22-en"
    # manga_info = comick.fetch_manga_info("the-overpowered-veteran-healer")
    # search_term = comick.search("naruto")
    # chapter_pages = comick.fetch_chapter_pages("manga-ml989594/chapter-223")
    # print(search_term)
    # with open("search.json", "w", encoding="utf-8") as f:
    #     json.dump(search_term, f)
    # print(chapter_pages)
    # with open("chapter_pages.json", "w") as f:
    #     json.dump(chapter_pages, f)
    # print(manga_info)
    # with open("manga_info.json", "w", encoding="utf-8") as f:
    #     json.dump(manga_info, f)


    # chapter_id = "the-overpowered-veteran-healer/iCqYxsfA-chapter-22-en"
    # manga_info = asurascans.fetch_manga_info("a-villains-will-to-survive-5537")
    # search_term = asurascans.search("naruto")
    # chapter_pages = asurascans.fetch_chapter_pages("manga-ml989594/chapter-223")
    # print(search_term)
    # with open("search.json", "w", encoding="utf-8") as f:
    #     json.dump(search_term, f)
    # print(chapter_pages)
    # with open("chapter_pages.json", "w") as f:
    #     json.dump(chapter_pages, f)
    # print(manga_info)
    # with open("manga_info.json", "w", encoding="utf-8") as f:
    #     json.dump(manga_info, f)
    
    # chapter_id = "the-overpowered-veteran-healer/iCqYxsfA-chapter-22-en"
    # manga_info = mangapark.fetch_manga_info("77410-en-omniscient-reader")
    # search_term = mangapark.search("naruto")
    # chapter_pages = mangapark.fetch_chapter_pages("124815-en-the-steward-demonic-emperor/9710108-chapter-711")
    # print(search_term)
    # with open("search.json", "w", encoding="utf-8") as f:
    #     json.dump(search_term, f)
    # print(chapter_pages)
    # with open("chapter_pages.json", "w") as f:
    #     json.dump(chapter_pages, f)
    # print(manga_info)
    # with open("manga_info.json", "w", encoding="utf-8") as f:
    #     json.dump(manga_info, f)
    
    # # Test new Mangapark functions
    # print("\nTesting Mangapark Home Page...")
    # latest_releases = mangapark.get_latest_releases()
    # print(f"Found {len(latest_releases)} latest releases")
    # with open("latest_releases.json", "w", encoding="utf-8") as f:
    #     json.dump(latest_releases, f)
    
    # print("\nTesting Mangapark Genres...")
    # genres = mangapark.get_genres()
    # print(f"Found {len(genres)} genres")
    # print(genres)
    # with open("genres.json", "w", encoding="utf-8") as f:
    #     json.dump(genres, f)
    
    # # Test manga in different categories
    # if latest_releases:
    #     print("\nTesting a manga from latest releases...")
    #     latest_manga_id = latest_releases[0]["id"]
    #     latest_manga_info = mangapark.fetch_manga_info(latest_manga_id)
    #     print(f"Title: {latest_manga_info['title']}")

    # chapter_id = "the-overpowered-veteran-healer/iCqYxsfA-chapter-22-en"
    # manga_info = comick.fetch_manga_info("the-overpowered-veteran-healer")
    # search_term = comick.search("naruto")
    # chapter_pages = comick.fetch_chapter_pages("manga-ml989594/chapter-223")
    # print(search_term)
    # with open("search.json", "w", encoding="utf-8") as f:
    #     json.dump(search_term, f)
    # print(chapter_pages)
    # with open("chapter_pages.json", "w") as f:
    #     json.dump(chapter_pages, f)
    # print(manga_info)
    # with open("manga_info.json", "w", encoding="utf-8") as f:
    #     json.dump(manga_info, f)
    # manga_info = mangapill.fetch_manga_info("8760/guimi-zhi-zhu")
    # search_term = mangapill.search("naruto")
    # chapter_pages = mangapill.fetch_chapter_pages("4897-10063000/yondome-wa-iyana-shi-zokusei-majutsushi-chapter-63")
    # print(search_term)
    # with open("search.json", "w", encoding="utf-8") as f:
    #     json.dump(search_term, f)
    # print(chapter_pages)
    # with open("chapter_pages.json", "w") as f:
    #     json.dump(chapter_pages, f)
    # print(manga_info)
    # with open("manga_info.json", "w", encoding="utf-8") as f:
    #     json.dump(manga_info, f)

    # manga_info = flamecomics.fetch_manga_info("23")
    # chapter_pages = flamecomics.fetch_chapter_pages("series/104/6c9f524d1a74d3c3")
    # print(chapter_pages)
    # with open("chapter_pages.json", "w") as f:
    #     json.dump(chapter_pages, f)
    # print(manga_info)
    # with open("manga_info.json", "w", encoding="utf-8") as f:
    #     json.dump(manga_info, f)

    # manga_info = weebcentral.fetch_manga_info("01J76XYH3NP2PBAA7D0ASA1GA8/Auto-Hunting-With-My-Clones")
    search_term = weebcentral.search("bleach")
    # chapter_pages = weebcentral.fetch_chapter_pages("01JZJFVJTR5ZFZ0R3YFGYN6DSG")
    print(search_term)
    with open("search.json", "w", encoding="utf-8") as f:
        json.dump(search_term, f)
    # print(chapter_pages)
    # with open("chapter_pages.json", "w") as f:
    #     json.dump(chapter_pages, f)
    # print(manga_info)
    # with open("manga_info.json", "w", encoding="utf-8") as f:
    #     json.dump(manga_info, f)
    

if __name__ == "__main__":
    main()
