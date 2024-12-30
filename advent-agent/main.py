import requests
import argparse


def request_day(day: int, cookie: str) -> str:
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
        return response.text  # The HTML content of the page
    else:
        raise(Exception(f"Failed to fetch page: {response.status_code}"))

def main():
    parser = argparse.ArgumentParser(description="advent-agent")
    parser.add_argument("-c", "--cookie", required=False, help="Cookie for the session")
    args = parser.parse_args()

    try:
        print(request_day(1, args.cookie))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()