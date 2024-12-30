import requests
import argparse
from lxml import html
import openai
import json


def request_day(day: int, cookie: str) -> bytes:
    url = f"https://adventofcode.com/2024/day/{day}"

    # Your session cookie (found after logging into the site via browser)
    cookies = {"session": cookie}

    # Send a GET requestes
    response = requests.get(url, cookies=cookies)

    # Check the response
    if response.status_code == 200:
        return response.content  # The HTML content of the page
    else:
        raise (Exception(f"Failed to fetch page: {response.status_code}"))


def parse_day(content: bytes) -> str:
    # Parse the content of the page
    tree = html.fromstring(content)  # type: ignore
    articles = tree.xpath('//article[@class="day-desc"]')

    if not articles:
        raise (Exception("No articles found on the page"))

    return "".join([article.text_content().strip() for article in articles])


def create_prompt(content: str) -> str:
    pre_prompt = """
Solve the following coding challenge in Python. Ensure the solution only includes a single code block that directly returns an int value as the result. The code should have no comments, explanations, or additional context—strictly the code snippet.
    """

    return f"{pre_prompt}\n{content}"


import openai
import json


def chat_request(api_key: str, prompt: str) -> str:
    """
    Sends a request to OpenAI's API to generate an executable Python code snippet
    for a given coding problem statement.

    Args:
        api_key (str): Your OpenAI API key.
        prompt (str): The coding problem statement.

    Returns:
        str: The generated Python code snippet.

    Raises:
        ValueError: If the API response does not include the expected code snippet.
        Exception: For any other unexpected API errors.
    """
    # Set API key
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

    try:
        # Send the request to the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            functions=[function],
            function_call={
                "name": "generate_code_snippet"
            },  # Force the model to call the function
        )

        # Extract the function call arguments
        function_call = response["choices"][0]["message"]["function_call"]
        arguments = json.loads(function_call["arguments"])

        # Ensure the response contains the 'code' key
        if "code" not in arguments:
            raise ValueError(
                "The API response did not include the expected 'code' key."
            )

        # Return the generated Python code snippet
        return arguments["code"]

    except openai.error.OpenAIError as e:
        raise Exception(f"OpenAI API error: {e}")
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")


def execute_code(code: str) -> None:
    """
    Executes the given Python code snippet and prints the output.

    Args:
        code (str): The Python code snippet to execute.
    """
    try:
        # Execute the Python code snippet
        exec(code)
    except Exception as e:
        print(f"An error occurred while executing the code: {e}")


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
    except ValueError as ve:
        print(ve)


if __name__ == "__main__":
    main()
