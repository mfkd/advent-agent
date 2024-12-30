import requests
import argparse
from lxml import html


def request_day(day: int, cookie: str) -> bytes:
    url = f"https://adventofcode.com/2024/day/{day}"

    # Your session cookie (found after logging into the site via browser)
    cookies = {
        "session": cookie
    }

    # Send a GET requestes
    response = requests.get(url, cookies=cookies)

    # Check the response
    if response.status_code == 200:
        print("Page fetched successfully!")
        return response.content  # The HTML content of the page
    else:
        raise(Exception(f"Failed to fetch page: {response.status_code}"))
    
def parse_day(content: bytes) -> str:
    # Parse the content of the page
    tree = html.fromstring(content) # type: ignore
    articles = tree.xpath('//article[@class="day-desc"]')

    if not articles:
        raise(Exception("No articles found on the page"))
    
    return "".join([article.text_content().strip() for article in articles])

def main():
    parser = argparse.ArgumentParser(description="advent-agent")
    parser.add_argument("-c", "--cookie", required=False, help="Cookie for the session")
    args = parser.parse_args()

    try:
        all_arcticles = parse_day(request_day(1, args.cookie))
        print(all_arcticles)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()