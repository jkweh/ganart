from bs4 import BeautifulSoup
from concurrent.futures import as_completed, ThreadPoolExecutor
import re
import requests

file_path = "art/wikiart"
base_url = "https://www.wikiart.org"
genres = ["pop-art", "minimalism", "contemporary", "kitsch"]


def make_request(url: str):
    return requests.get(
        url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"}
    ).content


def scrape_genre(genre: str):
    for _ in range(ord("a"), ord("z") + 1):  # Iterate through each artist in the genre, by last name.
        artist_list_url = f"{base_url}/en/artists-by-art-movement/{genre}/text-list"
        genre_soup = BeautifulSoup(make_request(artist_list_url), "lxml")
        artist_list_main = genre_soup.find("main")

        for li in artist_list_main.find_all("li"):
            born = died = 0
            for line in li.text.splitlines():  # get the date range
                if line.startswith(",") and "-" in line:
                    parts = line.split("-")
                    if len(parts) == 2:
                        born = int(re.sub("[^0-9]", "", parts[0]))
                        died = int(re.sub("[^0-9]", "", parts[1]))

            # look for artists who may have created work that could be in public domain
            if born > 1850 and died > 0 and (born < 1900 or died < 1950):
                artist = li.find("a").attrs["href"]

                # if artist == "/en/salvador-dali": # skip Dali
                #     continue

                # get the artist's main page
                artist_soup = BeautifulSoup(make_request(f"{base_url}{artist}"), "lxml")
                # page_body = artist_soup.text.lower()
                print(f"{artist}:{str(born)}-{str(died)}")
                url = f"{base_url}{artist}/all-works/text-list"  # get the artist's web page for the artwork
                artist_work_soup = BeautifulSoup(make_request(url), "lxml")

                # get the main section
                artist_main = artist_work_soup.find("main")
                artist_name = artist.split("/")[2]
                image_count = 0
                for li in artist_main.find_all("li"):
                    link = li.find("a")
                    if not link:
                        continue

                    url = f"{base_url}{link.attrs['href']}"  # get the painting
                    try:
                        painting_soup = BeautifulSoup(make_request(url), "lxml")
                    except:
                        print("error retreiving page")
                        continue

                    if "public domain" not in painting_soup.text.lower():  # check the copyright
                        continue

                    painting_genre = painting_soup.find("span", {"itemprop": "genre"})
                    if genre in painting_genre.text.lower():
                        # get the url
                        og_image = painting_soup.find("meta", {"property": "og:image"})
                        image_url = og_image["content"].split("!")[0]  # ignore the !Large.jpg at the end
                        save_path = f"{file_path}/{artist_name}_{str(image_count)}.jpg"
                        try:  # download the file
                            print(f"downloading {image_url} to {save_path}")
                            open(save_path, "wb").write(make_request(image_url))
                            image_count += 1
                        except Exception as e:
                            print(f"failed to download {image_url}", e)


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(scrape_genre, genre): genre for genre in genres}
        for future in as_completed(futures):
            genre = futures[future]
            try:
                data = future.result()
            except Exception as exc:
                print(f"{genre} scraper generated an exception: {exc}")
