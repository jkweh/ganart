#!/usr/bin/env python3

from bs4 import BeautifulSoup
from concurrent.futures import as_completed, ThreadPoolExecutor
import re
import requests

from common import base_url, raw_path

styles = ["pop-art", "minimalism", "contemporary"]


def make_request(url: str):
    return requests.get(
        url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"}
    ).content


def scrape_style(style: str):
    print(f"starting scrape of {style}")
    artist_list_url = f"{base_url}/en/artists-by-art-movement/{style}/text-list"
    style_soup = BeautifulSoup(make_request(artist_list_url), "lxml")

    for li in style_soup.find("main").find_all("li"):
        born = died = 0
        for line in li.text.splitlines():  # get the date range
            if line.startswith(",") and "-" in line:
                parts = line.split("-")
                if len(parts) == 2:
                    born = int(re.sub("[^0-9]", "", parts[0]))
                    died = int(re.sub("[^0-9]", "", parts[1]))

        # look for artists who may have created work that could be in public domain
        artist = li.find("a").attrs["href"]
        if 0 < died:
            # if artist == "/en/salvador-dali": # skip Dali
            #     continue
            # get the artist's main page
            artist_soup = BeautifulSoup(make_request(f"{base_url}{artist}"), "lxml")
            print(f"{style}:{artist}:{str(born)}-{str(died)}")
            artist_work_soup = BeautifulSoup(
                make_request(f"{base_url}{artist}/all-works/text-list"),  # get the artist's web page for the artwork
                "lxml",
            )
            artist_name = artist.split("/")[2]
            for i, li in enumerate(artist_work_soup.find("main").find_all("li")):
                link = li.find("a")
                if not link:
                    continue

                try:
                    # print(f"trying {base_url}{link.attrs['href']}")
                    painting_soup = BeautifulSoup(
                        make_request(f"{base_url}{link.attrs['href']}"), "lxml"  # get the painting
                    )
                except:
                    # print("error retreiving painting page")
                    continue

                # if "public domain" not in painting_soup.text.lower():  # check the copyright
                #     # print("wasn't in public domain")
                #     continue

                style_matched = False
                for a in painting_soup.article.find_all("a"):
                    for style in styles:
                        if style in a.get("href").lower():
                            style_matched = True
                            # ignore the !Large.jpg at the end
                            image_url = painting_soup.find("meta", {"property": "og:image"})["content"].split("!")[0]
                            save_path = f"{raw_path}/{artist_name}_{str(i)}.jpg"
                            try:  # download the file
                                print(f"downloading {image_url} to {save_path}")
                                open(save_path, "wb").write(make_request(image_url))
                            except Exception as e:
                                print(f"failed to download {image_url}", e)
                    if style_matched:
                        break
    print(f"done scraping {style}")


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(scrape_style, style): style for style in styles}
        for future in as_completed(futures):
            style = futures[future]
            try:
                data = future.result()
            except Exception as exc:
                print(f"{style} scraper generated an exception: {exc}")
