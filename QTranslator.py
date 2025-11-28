import time
import tkinter as tk
from pynput import keyboard

from arabic_reshaper import reshape
from bidi.algorithm import get_display

from deep_translator import GoogleTranslator
from gtts import gTTS
from playsound import playsound
import pygame

from pathlib import Path
import pyperclip, requests, os, sys
from termcolor import colored


class QTranslator:
    def __init__(self):
        self.root, self.popup,self.lable_en, self.play_sound_button, self.lable_fa, self.ok_button = None
        self.current_text = ''
        self.output_file_path = str(Path('translation_history.txt'))
        self.pronunciation_path = str(Path('pronunciation.mp3'))
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.mixer = pygame.mixer
        self.is_music_playing = False
        self.translator = GoogleTranslator(source='en', target='fa')

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
        print(colored('History file removed successfully!', 'green'))

    def shut_down(self):
        print(colored('shuting down...', 'green'))
        try:
            self.listener.stop()
            if hasattr(self, 'popup'):
                self.popup.destroy()
            if hasattr(self, 'root'):
                self.root.destroy()
        except Exception as e:
            print(colored(f'Error during shutdown: {str(e)}', 'red'))
        finally:
            sys.exit(0)

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

        self.lable_en = tk.Label(self.popup, text="", font=("Arial", 16, "bold"), bg="white", fg="#333")
        self.lable_en.pack(anchor='w')

        self.play_sound_button = tk.Button(self.popup, text='s',font=("Arial", 8), justify='left', command=lambda: Thread(target=self.play_pronunciation).start())
        self.play_sound_button.pack(anchor='w')

        tk.Frame(self.popup, height=1, bg="#ccc").pack(fill="x", pady=5)

        self.lable_fa = tk.Label(self.popup, text="", font=("Vazir", 16), bg="white", fg="#222", justify="right")
        self.lable_fa.pack(anchor='e', pady=(0, 20))

        self.ok_button = tk.Button(self.popup, text='Ok',font=("Arial", 14, "bold"), width=20, height=2, justify='center', command=self.hide_popup)
        self.ok_button.pack()

        self.popup.withdraw() # popup hided.
        self.popup.protocol('WM_DELETE_WINDOW', self.hide_popup)

    def hide_popup(self):
        self.popup.withdraw()
        self.remove_pronunc_file()

    def show_pop_up(self, en_text, fa_text):
        fa_text = get_display(reshape(fa_text))
        self.lable_en.config(text=en_text)
        self.lable_fa.config(text=fa_text)
        x, y = self.root.winfo_pointerx(), self.root.winfo_pointery()
        self.popup.geometry(f"+{x+10}+{y+10}")
        self.popup.deiconify()
        self.popup.lift()
        self.popup.focus_force()

    def translate(self, en_text):
        """translate text. if connection denied raises alarm."""
        instance = self.translator
        try:
            trased_text = instace.translate(text)
            return trased_text
            fa_text = instance.translate(en_text)
            self.queue.put(('show popup', en_text, fa_text))
        except requests.exceptions.ConnectionError:
            print(colored('please connect to internet!\a', 'red'))
            return None
        except Exception as e:
            print(colored(f'unknown error acquired.', 'red'))
            return None

    def remove_pronunc_file(self)->bool:
        if os.path.exists(self.pronunciation_path):
            os.remove(self.pronunciation_path)
            return True
        return False

    def play_pronunciation(self):
        if os.path.exists(self.pronunciation_path):
            self.play_audio(self.pronunciation_path)
            return 
        try:
            tts = gTTS(text=self.current_text, lang='en', slow=False)
            tts.save(self.pronunciation_path)
            self.play_audio(self.pronunciation_path)

        except Exception as e:
            print(colored('Error in pronunciation.', 'red'))
            print(f'error:{str(e)}')

    def play_audio(self, file_path=None):
        """playing an audio."""
        file_path = self.pronunciation_path if not file_path else file_path

        if self.mixer.music.get_busy(): # stop other sounds if is playing.
            self.mixer.music.stop()
            time.sleep(.1)

        try:
            self.mixer.music.load(file_path)
            self.mixer.music.play()
            while self.mixer.music.get_busy():
                time.sleep(0.1)
            self.mixer.music.unload()  # unload pronunciation file.

        except Exception as e:
            print('an error accorded in play audio.', str(e))

    def check_clipboard(self, last_text=''):
        self.clipboard_current_text = pyperclip.paste().strip() # get text from clipboard
        if self.clipboard_current_text and self.clipboard_current_text != last_text:
            print(colored("your text recognized.", 'blue'))
            Thread(target=self.translate, args=(self.clipboard_current_text,)).start()
            last_text = self.clipboard_current_text
        self.root.after(200, self.check_clipboard, last_text)

    def check_queue(self):
        if not self.queue.empty():
            trd_type, en_text, fa_text = self.queue.get()
            if trd_type == 'show popup' and fa_text:
                self.write_text_in_file(en_text, fa_text)
                self.en_text = en_text
                self.show_pop_up(en_text, fa_text)
            elif trd_type == 'shutdown':
                self.listener.stop()
                self.root.destroy()
                sys.exit(0)
        self.root.after(100, self.check_queue)

    def clear_terminal(self):
        if sys.platform == 'linux':
            os.system('clear')
        else:
            os.system('cls')

    def print_help_text(self):
        self.clear_terminal()
        print('='*75)
        print("Wellcome to QTranslator!".center(75))
        print(f"select any English word or sentence and copy it to show farsi translation.".center(75))
        print('='*75)
        print('Key List:')
        print(colored('Press "Ctrl+c" Show translation.', 'yellow'))
        print(colored('Press "Ctrl+Shift+e" to Erase(remove) History file.', 'yellow'))
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