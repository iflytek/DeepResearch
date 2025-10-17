# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License
def colored_print(text, color='white', bg_color=None, bold=False, underline=False, end='\n'):
    """
    Function for printing colored text
    :param text: Content to be printed
    :param color: Text color (supports black/red/green/yellow/blue/purple/cyan/white/orange)
    :param bg_color: Background color (supports black/red/green/yellow)
    :param bold: Whether to use bold style
    :param underline: Whether to use underline style
    :param end: Print end
    """
    # Color mapping dictionary
    color_map = {
        'black': '\033[30m', 'red': '\033[31m', 'green': '\033[32m',
        'yellow': '\033[33m', 'blue': '\033[34m', 'purple': '\033[35m',
        'cyan': '\033[36m', 'white': '\033[37m', 'orange': '\033[38;5;208m',
    }
    bg_color_map = {
        'black': '\033[40m', 'red': '\033[41m', 'green': '\033[42m',
        'yellow': '\033[43m'
    }

    # Assemble styles
    style = color_map.get(color.lower(), color_map['white'])  # Default to white
    if bg_color:
        style += bg_color_map.get(bg_color.lower(), '')
    if bold:
        style += '\033[1m'
    if underline:
        style += '\033[4m'

    # Print and reset styles
    print(f"{style}{text}\033[0m", end=end)

# Usage examples
if __name__ == "__main__":
    colored_print("Error message: File not found", color="white", bold=True)
    colored_print("Success: Data loaded completely", color="green", bg_color="yellow")
    colored_print("Hint: Please check the configuration", color="blue", underline=True)
