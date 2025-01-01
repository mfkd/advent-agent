import requests
import sys
import io
import argparse
from lxml import html
from openai import OpenAI
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
Write a Python solution to the given challenge. The code must be self-contained and executable directly with Python’s exec() function. It will have access to an input_data variable, which will be provided as input to the code. The solution should use input_data to compute the result and assign the integer result to a variable named result. Include no comments, explanations, or additional text—just the executable code snippet.
    """

    return f"{pre_prompt}\n{content}"


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

    # Initialize the OpenAI client
    client = OpenAI(api_key=api_key)

    # Define the tools to be used in the request
    tools = [
        {
            "type": "function",
            "function": {
                "name": "solve_coding_challenge",
                "description": "Solves a specified coding challenge and returns an integer result.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "required": ["code_block"],
                    "properties": {
                        "code_block": {
                            "type": "string",
                            "description": "The Python code snippet that returns an integer value.",
                        }
                    },
                    "additionalProperties": False,
                },
            },
        }
    ]

    try:
        # Send the request to the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            tools=tools,
            tool_choice="required",
        )

        tool_call = response.choices[0].message.tool_calls[0]
        arguments = json.loads(tool_call.function.arguments)
        return arguments.get("code_block")

    except AttributeError as e:
        raise Exception(
            f"An unexpected attribute error occurred: {e}. Check your OpenAI library version."
        ) from e
    except ValueError as ve:
        raise ve
    except KeyError as ke:
        raise ValueError("Unexpected API response structure.") from ke
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}") from e


def read_file_to_string(file_path: str) -> str:
    """
    Reads the content of a file and returns it as a string.

    Parameters:
        file_path (str): The path to the file to be read.

    Returns:
        str: The content of the file as a string.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "Error: File not found."
    except IOError:
        return "Error: An I/O error occurred."


def execute_code(code: str, input_data: str) -> str:
    """
    Executes the given Python code snippet and captures the result if defined.

    Args:
        code (str): The Python code snippet to execute.

    Returns:
        str: The 'result' variable if defined, or an error message if an exception occurs.
    """
    try:
        # Create an isolated execution environment
        exec_globals = {"input_data": input_data}

        # Execute the provided code snippet
        exec(code, exec_globals)

        # Return 'result' if defined
        if "result" in exec_globals:
            return str(exec_globals["result"])
        return "No result variable defined."
    except Exception as e:
        # Return the error message if execution fails
        return f"An error occurred: {str(e)}"


def split_parts(content: str) -> tuple[str, str]:
    parts = content.split("--- Part Two ---")
    if len(parts) > 2:
        raise (Exception("More than two parts found"))
    if len(parts) == 1:
        return content
    return parts[0], parts[1]


def main():
    parser = argparse.ArgumentParser(description="advent-agent")
    parser.add_argument("-c", "--cookie", required=False, help="Cookie for the session")
    parser.add_argument("-a", "--api-key", required=True, help="OpenAI API key")
    parser.add_argument("-d", "--day", required=True, help="Day to solve")
    parser.add_argument("-p", "--part", required=True, help="Part to solve")

    args = parser.parse_args()

    try:
        all_arcticles = parse_day(request_day(args.day, args.cookie))

        part_to_solve = ""
        if args.part == "1":
            part_to_solve = split_parts(all_arcticles)[0]
        if args.part == "2":
            part_to_solve = split_parts(all_arcticles)[1]
        else:
            raise (Exception("Invalid part"))

        prompt = create_prompt(part_to_solve)
        input_data = read_file_to_string(f"input_data/day0{args.day}.txt")
        code_block = chat_request(args.api_key, prompt)
        result = execute_code(code_block, input_data)
        print(f"result:\n{result}\n")
    except Exception as e:
        print(e)
    except ValueError as ve:
        print(ve)


if __name__ == "__main__":
    main()
