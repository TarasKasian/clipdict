import os
import tkinter as tk
import webbrowser
from functools import partial

import keyboard
import pyautogui
import pyperclip
import requests
from bs4 import BeautifulSoup

# TODO: - Handle errors and show it in popup
#       - Write readme

# TODO: move to settings.json:
RUN_SHORTCUT = 'ctrl+`'
QUIT_SHORTCUT = 'ctrl+q'
# PATH_TO_DICT_FILE = 'C:\\Users\\bameo\\iCloudDrive\\iCloud~md~obsidian\\mango-obsidian-vault\\English\\vocabulary.md'
DICT_FILE_PATH = 'D:\\tmp\\2\\vocabulary.md'

if not os.path.exists(DICT_FILE_PATH):
    print(f'File \'{DICT_FILE_PATH}\' does not exist, creating new file.')
    with open(DICT_FILE_PATH, 'a') as file:
        file.write('# Vocabulary\n\n')
    print('File created.')


def get_text_from_clipboard():
    try:
        return pyperclip.paste()
    except pyperclip.PyperclipException as e:
        print('Error accessing the clipboard:', e)


def get_url(word):
    return f'https://dictionary.cambridge.org/dictionary/english/{word.lower()}'


def fetch_definition(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        # Attempt to load the webpage with headers to mimic a web browser
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the element with the given class name
        element = soup.find(class_='def ddef_d db')
        if element is not None:
            return element.text.strip()
        else:
            raise ValueError(f'Element with definition not found.')
    except requests.exceptions.HTTPError as http_err:
        return f'HTTP error occurred: {http_err}'
    except requests.exceptions.RequestException as req_err:
        return f'Error fetching the page: {req_err}'
    except ValueError as val_err:
        return str(val_err)
    except Exception as err:
        return f'An unexpected error occurred: {err}'


def to_dictionary_record_format(word, definition, url):
    formatted_definition = definition
    # Remove ':' symbol from the exd of extracted definition if needed:
    if definition[-1] == ':':
        formatted_definition = definition[:-1]
    return f'[{word}]({url}) - {formatted_definition}'


def append_to_dictionary_file(text):
    with open(DICT_FILE_PATH, 'a') as dict_file:
        dict_file.write('\n\n' + text)


def save_to_dictionary(word, definition, url):
    print('Generating dictionary record.')
    dictionary_record = to_dictionary_record_format(word, definition, url)
    print('Dictionary record generated.')
    append_to_dictionary_file(dictionary_record)


def execute_workflow():
    word = get_text_from_clipboard()

    if word is None or word == '':
        print('Error: Clipboard is empty.')
        return

    if not word.strip().isalpha():
        print('Error: Clipboard contains multiple words, only one single word expected.')

    url = get_url(word.lower())

    print(f'Fetching definition for word \'{word}\'...')
    definition = fetch_definition(url)
    print(f'Definition fetched.')

    show_popup_window(word, definition, url)
    # save_to_dictionary(word, definition, url)


def on_open_url_pressed(def_window, url):
    webbrowser.open(url)
    def_window.destroy()


def position_window_near_cursor(window, width, height):
    x, y = pyautogui.position()
    screen_width, screen_height = pyautogui.size()
    new_x = min(x, screen_width - width)
    new_y = min(y, screen_height - height)
    window.geometry(f"{width}x{height}+{new_x}+{new_y}")


def show_popup_window(word, definition, url):
    def_window = tk.Toplevel()
    def_window.overrideredirect(True)  # Make the window borderless

    word_font = ('Helvetica', 14, 'bold')

    # Word label, with text aligned to the left
    word_label = tk.Label(def_window, text=word, font=word_font, anchor='w')
    word_label.pack(fill='x', padx=10, pady=(10, 0))

    # Definition and URL label, with text aligned to the left
    info_text = f'{definition}'
    info_label = tk.Label(def_window, text=info_text, justify='left', anchor='w', wraplength=280)
    info_label.pack(fill='x', padx=10, pady=(0, 10))

    # Buttons
    save_button = tk.Button(def_window, text="Save to Dictionary",
                            command=partial(save_to_dictionary, word, definition, url))
    save_button.pack(side=tk.LEFT, padx=(10, 5), pady=10)

    open_url_button = tk.Button(def_window, text="Open URL", command=partial(on_open_url_pressed, def_window, url))
    open_url_button.pack(side=tk.LEFT, padx=(5, 10), pady=10)

    dismiss_button = tk.Button(def_window, text="Dismiss", command=def_window.destroy)
    dismiss_button.pack(side=tk.RIGHT, padx=(5, 10), pady=10)

    # Automatically adjust window size based on content
    def_window.update_idletasks()
    width = def_window.winfo_reqwidth()
    height = def_window.winfo_reqheight()

    position_window_near_cursor(def_window, width, height)


def run():
    app = tk.Tk()
    app.withdraw()
    keyboard.add_hotkey(RUN_SHORTCUT, execute_workflow)
    # keyboard.wait(QUIT_SHORTCUT)
    app.mainloop()


if __name__ == '__main__':
    run()

