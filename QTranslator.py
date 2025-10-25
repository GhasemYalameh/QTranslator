import time
import tkinter as tk
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from deep_translator import GoogleTranslator
from pathlib import Path
from pynput import keyboard
import pyperclip, requests, os
from termcolor import colored


class QTranslator:
    def __init__(self):
        self.translator = GoogleTranslator(source='en', target='fa')
        self.output_file_path = Path('translated_text.txt')

        self.hotkey_ctrl_shift_e = keyboard.HotKey(
            keyboard.HotKey.parse('<ctrl>+<shift>+e'),
            self.clear_file
        )
        self.hotkey_exit= keyboard.HotKey(
            keyboard.HotKey.parse('<ctrl>+<shift>+q'),
            self.shut_down
        )
        
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()

    def on_press(self, key):
        self.hotkey_ctrl_shift_e.press(self.listener.canonical(key))
        self.hotkey_exit.press(self.listener.canonical(key))

    def on_release(self, key):
        self.hotkey_ctrl_shift_e.release(self.listener.canonical(key))
        self.hotkey_exit.release(self.listener.canonical(key))

    def clear_file(self):
        os.remove(self.output_file_path)
        print('file removed successfully!')

    def shut_down(self):
        print(colored('shuting down...', 'green'))
        time.sleep(1)
        self.listener.stop()
        self.popup.destroy()
        self.root.destroy()

    def write_text_in_file(self, main_text, transed_text):
        """write text and translated text in output file"""
        text = f'{main_text}\n{transed_text}\n{"-"*100}\n'

        with open(self.output_file_path, 'a', encoding='utf-8') as f:
            f.write(text)

    def make_withdraw_popup(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.popup = tk.Toplevel(self.root)

        self.popup.attributes("-topmost", True)
        self.popup.configure(bg="white", padx=10, pady=10, highlightthickness=1, highlightbackground="#aaa")

        self.lable_en = tk.Label(self.popup, text="", font=("Arial", 14, "bold"), bg="white", fg="#333")
        self.lable_en.pack(anchor='w')

        tk.Frame(self.popup, height=1, bg="#ccc").pack(fill="x", pady=5)

        self.lable_fa = tk.Label(self.popup, text="", font=("Vazir", 14), bg="white", fg="#222", justify="right")
        self.lable_fa.pack(anchor='e', pady=(0, 10))

        self.ok_button = tk.Button(self.popup, text='Ok',font=("Arial", 14, "bold"), width=20, height=2, justify='center', command=self.hide_popup)
        self.ok_button.pack()

        self.popup.withdraw() # popup hided.

    def hide_popup(self):
        self.popup.withdraw()

    def show_pop_up(self, main_text, transed_text):
        transed_text = get_display(reshape(transed_text))
        self.lable_en.config(text=main_text)
        self.lable_fa.config(text=transed_text)
        x, y = self.root.winfo_pointerx(), self.root.winfo_pointery()
        self.popup.geometry(f"+{x+10}+{y+10}")
        self.popup.deiconify()
        self.popup.lift()
        self.popup.focus_force()
        # self.popup.bind("<FocusOut>", lambda e: self.hide_popup())

    def translate(self, text):
        """translate text. if connection denied rases alarm."""
        instace = self.translator
        try:
            trased_text = instace.translate(text)
            return trased_text
        except requests.exceptions.ConnectionError:
            print(colored('please connect to internet!\a', 'red'))
        except Exception as e:
            print(colored(f'unknown error acquired.', 'red'))

    def check_clipboard(self, last_text=''):
        current_text = pyperclip.paste().strip() # get text from clipboard
        if current_text and current_text != last_text:
            translated_text = self.translate(text=current_text)
            self.write_text_in_file(main_text=current_text, transed_text=translated_text)
            self.show_pop_up(current_text, translated_text)
            last_text = current_text
        self.root.after(500, self.check_clipboard, last_text)

    def print_help_text(self):
        os.system('clear')
        print('='*75)
        print("Wellcome to QTranslator!".center(75))
        print(f"select any English word or sentence and copy it to show farsi translation.".center(75))
        print('='*75)
        print('Key List:')
        print(colored('Press "Ctrl+c" Show translation.', 'yellow'))
        print(colored('Press "Ctrl+Shift+e" to Erase(remove) output file.', 'yellow'))
        print(colored('Press "Ctrl+Shift+q" to quiet.\n', 'yellow'))
        print('-'*75, '\n')


    def run(self):
        self.print_help_text()
        self.make_withdraw_popup()
        self.check_clipboard()
        self.root.mainloop()


if __name__ == '__main__':
    trans = QTranslator()
    trans.run()