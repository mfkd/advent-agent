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
    
input_data = read_file_to_string("../input_data/day04.txt")

grid = [list(line) for line in input_data.splitlines()]
rows, cols = len(grid), len(grid[0])
directions = [((-1, -1), (1, 1)), ((-1, 1), (1, -1))]

def is_x_mas(r, c, dr1, dr2):
    try:
        return (
            grid[r][c] == 'A' and
            grid[r+dr1[0]][c+dr1[1]] == 'M' and
            grid[r+dr2[0]][c+dr2[1]] == 'M' and
            grid[r+2*dr1[0]][c+2*dr1[1]] == 'S' and
            grid[r+2*dr2[0]][c+2*dr2[1]] == 'S'
        )
    except IndexError:
        return False

result = sum(
    is_x_mas(r, c, dr1, dr2)
    for r in range(rows)
    for c in range(cols)
    for dr1, dr2 in directions
)

print(input_data)
print(result)