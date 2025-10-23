from deep_translator import GoogleTranslator
from pathlib import Path
from pynput import keyboard
import pyperclip, requests, time, os


class QTranslator:
    def __init__(self):
        self.translator = GoogleTranslator(source='en', target='fa')
        self.output_file_path = Path('translated_text.txt')

        self.hotkey_ctrl_shift_e = keyboard.HotKey(
            keyboard.HotKey.parse('<ctrl>+<shift>+e'),
            self.clear_file
        )
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()

    def on_press(self, key):
        self.hotkey_ctrl_shift_e.press(self.listener.canonical(key))
    
    def on_release(self, key):
        self.hotkey_ctrl_shift_e.release(self.listener.canonical(key))

    def clear_file(self):
        os.remove(self.output_file_path)
        print('file removed successfully!')

    def write_text_in_file(self, main_text, transed_text):
        """write text and translated text in output file"""
        text = f'{main_text}\n{transed_text}\n{"-"*100}\n'

        with open(self.output_file_path, 'a', encoding='utf-8') as f:
            f.write(text)

    def translate(self, text):
        """translate text. if connection denied rases alarm."""
        instace = self.translator
        try:
            trased_text = instace.translate(text)
            return trased_text
        except requests.exceptions.ConnectionError:
            print('please connect to internet!\a')
        except Exception as e:
            print(f'unknown error acquired.')

    def run(self):
        last_text = ''
        while 1:
            current_text = pyperclip.paste().strip() # get text from clipboard
            if current_text and current_text != last_text:
                translated_text = self.translate(text=current_text)
                self.write_text_in_file(main_text=current_text, transed_text=translated_text)
                last_text = current_text
            time.sleep(.6)


if __name__ == '__main__':
    trans = QTranslator()
    trans.run()