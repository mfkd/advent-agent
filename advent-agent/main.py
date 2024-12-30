import requests
import argparse
from lxml import html
import openai
import json


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

def create_prompt(content: str) -> str:
    pre_prompt = """
Provide a solution to the following coding challenge in Python. Return only the code snippet. Do not include explanations, comments, or additional context—only the code block:
    """

    return f"{pre_prompt}\n{content}"

def chat_request(api_key: str, prompt: str) -> str:
    openai.api_key = api_key
    # Define the function schema
    function = {
        "name": "generate_code_snippet",
        "description": "Generates an executable Python code snippet for the given problem statement.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The Python code snippet that solves the given problem.",
                }
            },
            "required": ["code"],
        },
    }

    # Send the request to the OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        functions=[function],
        function_call={"name": "generate_code_snippet"}, # Force the model to call the function
    )

    # Extract the function call arguments
    function_call = response["choices"][0]["message"]["function_call"]
    arguments = json.loads(function_call["arguments"])
    code_snippet = arguments["code"]
    return code_snippet

def main():
    parser = argparse.ArgumentParser(description="advent-agent")
    parser.add_argument("-c", "--cookie", required=False, help="Cookie for the session")
    parser.add_argument("-a", "--api-key", required=True, help="OpenAI API key")
    args = parser.parse_args()

    try:
        all_arcticles = parse_day(request_day(1, args.cookie))
        prompt = create_prompt(all_arcticles)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()