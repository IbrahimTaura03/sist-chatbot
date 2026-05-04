"""
scraper.py  —  SIST Tangier website scraper
Run from the backend/ folder:
    python scraper.py
Output: data/sist_info.txt
"""

import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL   = "https://www.sist.ac.ma/"
MAX_PAGES  = 60        # safety cap — won't crawl more than this
MAX_DEPTH  = 3         # don't go deeper than 3 links from home
DELAY      = 1.2       # seconds between requests (be polite, avoid bans)
OUTPUT     = "data/sist_info.txt"

# Tags whose content is useless noise — skip them entirely
SKIP_TAGS = {"script", "style", "noscript", "header", "footer",
             "nav", "aside", "form", "svg", "img", "button"}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

def extract_clean_text(soup: BeautifulSoup) -> str:
    """Extract meaningful text, skipping nav/footer/script noise."""
    # Remove noisy tags in-place
    for tag in soup(SKIP_TAGS):
        tag.decompose()

    # Try to find the main content area first
    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find(id="content")
        or soup.find(class_="content")
        or soup.find(class_="entry-content")
        or soup.body
    )

    if not main:
        return ""

    lines = []
    for text in main.stripped_strings:
        text = text.strip()
        if len(text) > 20:          # skip very short fragments like "›" or "Menu"
            lines.append(text)

    return "\n".join(lines)


def scrape():
    os.makedirs("data", exist_ok=True)

    visited   = set()
    # queue items: (url, depth)
    to_visit  = [(BASE_URL, 0)]
    all_text  = []
    pages_done = 0

    session = requests.Session()
    session.headers.update(HEADERS)

    while to_visit and pages_done < MAX_PAGES:
        url, depth = to_visit.pop(0)   # BFS — breadth-first

        # Normalise URL (strip fragments)
        url = url.split("#")[0].rstrip("/") + "/"
        if url in visited:
            continue
        visited.add(url)

        # Only crawl pages on the same domain
        if urlparse(url).netloc != urlparse(BASE_URL).netloc:
            continue

        print(f"[{pages_done+1}] depth={depth}  {url}")

        try:
            resp = session.get(url, timeout=12)
            if resp.status_code != 200:
                print(f"  ↳ skipped (HTTP {resp.status_code})")
                continue
            if "text/html" not in resp.headers.get("Content-Type", ""):
                continue
        except Exception as e:
            print(f"  ↳ error: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        # Get page title for context
        title = soup.title.string.strip() if soup.title else url
        text  = extract_clean_text(soup)

        if text:
            all_text.append(f"=== {title} ===\n{text}")
            pages_done += 1

        # Discover links — only go deeper if within depth limit
        if depth < MAX_DEPTH:
            for a in soup.find_all("a", href=True):
                href = urljoin(BASE_URL, a["href"]).split("#")[0]
                if href not in visited and BASE_URL in href:
                    to_visit.append((href, depth + 1))

        time.sleep(DELAY)

    # Save
    full_text = "\n\n".join(all_text)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"\n✅ Scraped {pages_done} pages → saved to {OUTPUT}")
    print(f"   Total characters: {len(full_text):,}")


if __name__ == "__main__":
    scrape()