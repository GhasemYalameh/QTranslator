from deep_translator import GoogleTranslator
from pathlib import Path
import pyperclip, keyboard, requests, time, os


class QTranslator:
    def __init__(self):
        self.translator = GoogleTranslator(source='en', target='fa')
        self.output_file_path = Path('translated_text.txt')

        keyboard.add_hotkey('ctrl shift a', self.clear_file)

    def clear_file(self):
        os.remove(self.output_file_path)
        print('file removed successfully!')

    def write_text_in_file(self, source_text, target_text):
        """write text and translated text in output file"""
        text = f'{source_text}\n{target_text}\n{"-"*100}\n'

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
                self.write_text_in_file(source_text=current_text, target_text=translated_text)
                last_text = current_text
            time.sleep(.6)


if __name__ == '__main__':
    trans = QTranslator()
    trans.run()