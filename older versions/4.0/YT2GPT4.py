import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox, QScrollArea, QSizePolicy, QTextEdit, QComboBox, QInputDialog, QSpacerItem
from PyQt5.QtGui import QIcon, QPixmap
from youtube_transcript_api import YouTubeTranscriptApi
import textwrap
import sys
from functools import partial


class Profile:
    def __init__(self, file_path="profiles.json"):
        self.file_path = file_path
        self.profiles = self.load_profiles()

    def load_profiles(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return json.load(file)
        else:
            return {}

    def save_profile(self, name, prompt, end_prompt):
        self.profiles[name] = {
            "prompt": prompt,
            "end_prompt": end_prompt
        }
        with open(self.file_path, 'w') as file:
            json.dump(self.profiles, file)

    def delete_profile(self, name):
        self.profiles.pop(name, None)
        with open(self.file_path, 'w') as file:
            json.dump(self.profiles, file)


class Settings:
    def __init__(self, file_path="settings.json"):
        self.file_path = file_path
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return json.load(file)
        else:
            return {}

    def save_setting(self, key, value):
        self.settings[key] = value
        with open(self.file_path, 'w') as file:
            json.dump(self.settings, file)

    def get_setting(self, key):
        return self.settings.get(key)


class TranscriptApp(QWidget):
    def __init__(self, profile, settings):
        super().__init__()
        self.profile = profile
        self.settings = settings
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Transcript App')  # Add window title

        self.layout = QVBoxLayout()
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget(self.scrollArea)
        self.scrollLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.createForm()
        self.layout.addWidget(self.scrollArea)
        self.setLayout(self.layout)

    def createForm(self):
        self.label_link = QLabel("Paste YouTube video link:")
        self.scrollLayout.addWidget(self.label_link)
        self.entry = QLineEdit()
        self.scrollLayout.addWidget(self.entry)

        self.label_chunk_size = QLabel("Enter the number of characters per chunk (recommended: 8000 for GPT-3, 15000 for GPT-4):")
        self.scrollLayout.addWidget(self.label_chunk_size)
        self.chunk_size_entry = QLineEdit()
        self.chunk_size_entry.setText(self.settings.get_setting("chunk_size"))
        self.scrollLayout.addWidget(self.chunk_size_entry)

        self.label_language = QLabel("Enter the language for translation:")
        self.scrollLayout.addWidget(self.label_language)
        self.language_entry = QLineEdit()
        self.language_entry.setText(self.settings.get_setting("language"))
        self.scrollLayout.addWidget(self.language_entry)

        self.label_profiles = QLabel("Select a profile (optional):")
        self.scrollLayout.addWidget(self.label_profiles)
        self.profile_selector = QComboBox()
        self.profile_selector.addItems(self.profile.profiles.keys())
        self.profile_selector.currentIndexChanged.connect(self.load_profile)  # Load profile when a profile is selected
        self.scrollLayout.addWidget(self.profile_selector)

        self.label_prompt = QLabel("Enter your custom prompt (optional):")
        self.scrollLayout.addWidget(self.label_prompt)
        self.prompt_entry = QTextEdit()
        self.scrollLayout.addWidget(self.prompt_entry)

        self.label_end_prompt = QLabel("Enter your custom ending prompt (optional):")
        self.scrollLayout.addWidget(self.label_end_prompt)
        self.end_prompt_entry = QTextEdit()
        self.scrollLayout.addWidget(self.end_prompt_entry)

        self.save_profile_button = QPushButton("Save current prompts as a new profile")
        self.save_profile_button.clicked.connect(self.save_profile)
        self.scrollLayout.addWidget(self.save_profile_button)

        self.delete_profile_button = QPushButton("Delete selected profile")
        self.delete_profile_button.clicked.connect(self.delete_profile)
        self.scrollLayout.addWidget(self.delete_profile_button)

        self.button = QPushButton("Get transcript")
        self.button.clicked.connect(self.handle_click)
        self.scrollLayout.addWidget(self.button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.handle_clear)
        self.scrollLayout.addWidget(self.clear_button)

        # Adding some space for better readability
        self.scrollLayout.addItem(QSpacerItem(20, 40))

    def handle_click(self):
        video_link = self.entry.text()
        video_id = video_link.split("=")[-1]
        try:
            chunk_size = int(self.chunk_size_entry.text())
            self.settings.save_setting("chunk_size", self.chunk_size_entry.text())  # save chunk size
        except ValueError:
            QMessageBox.warning(self, "Error", "Chunk size must be an integer.")
            return

        language = self.language_entry.text()
        self.settings.save_setting("language", language)  # save language
        prompt = self.prompt_entry.toPlainText()
        end_prompt = self.end_prompt_entry.toPlainText()

        try:
            transcript = self.get_transcript(video_id)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        sections = self.divide_transcript(transcript, chunk_size)
        prompts = self.create_prompts(sections, chunk_size, language, prompt, end_prompt)

        for i, prompt in enumerate(prompts):
            button = QPushButton(f"Copy chunk {i+1}/{len(prompts)}")
            button.clicked.connect(partial(self.copy_to_clipboard, prompt))
            self.scrollLayout.addWidget(button)
        
        final_text = f"Retrieve and compile bullet lists created between {1}/{len(prompts)} to {len(prompts)}/{len(prompts)}. Generate a detailed table of contents for a report using [{language}] language. The table of contents should include titles and subtitles, with bullet points under each, encompassing all the topics discussed in the previous bullet points of this conversation. Ensure that the table of contents is written in [{language}]."
        button = QPushButton(f"Copy final text")
        button.clicked.connect(partial(self.copy_to_clipboard, final_text))
        self.scrollLayout.addWidget(button)

    def handle_clear(self):
        while self.scrollLayout.count():
            item = self.scrollLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.createForm()

    def copy_to_clipboard(self, text):
        QApplication.clipboard().setText(text)

    def get_transcript(self, video_id):
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en'])
        return " ".join([t['text'] for t in transcript.fetch()])

    def divide_transcript(self, transcript, chunk_size):
        return textwrap.wrap(transcript, chunk_size)

    def create_prompts(self, sections, chunk_size, language, prompt, end_prompt):
        total_sections = len(sections)
        prompts = []
        for i, section in enumerate(sections):
            if prompt:
                start_prompt = f"{prompt}. Write in [{language}]."
            else:
                if i == 0:
                    start_prompt = f"From now, you will write in [{language}]. I will provide you with a transcription of spoken content, and I need your help to understand what was said. Please listen carefully and provide a concise bullet-point summary of the main ideas and key points covered in the given text. Include the essential concepts, arguments, or findings, and emphasize any important details or supporting evidence. Make sure to mention the topics discussed in the text and organize your response in a clear and coherent bullet list format. Your summary should condense the information while maintaining accuracy and provide a comprehensive overview of the text's content. Separatly, you will note all the stastictics and formulas."
                else:
                    start_prompt = f"Continue to listen and provide a concise bullet-point summary in [{language}]. Note all the stastictics and formulas separately."

            end_prompt_text = f"{end_prompt}. Write in [{language}]." if end_prompt else f"End of this chunk. Remember to note all the statistics and formulas in [{language}] separately."

            start_marker = f"{start_prompt} [START CHUNK {i+1}/{total_sections}]> "
            end_marker = f"[END CHUNK {i+1}/{total_sections}]< {end_prompt_text}"

            prompts.append(f"{start_marker}\n{section}\n{end_marker}")

        return prompts

    def save_profile(self):
        text, ok = QInputDialog.getText(self, 'Save profile', 'Enter a name for the profile:')
        if ok:
            self.profile.save_profile(text, self.prompt_entry.toPlainText(), self.end_prompt_entry.toPlainText())
            self.profile_selector.addItem(text)

    def delete_profile(self):
        current_profile = self.profile_selector.currentText()
        self.profile.delete_profile(current_profile)
        self.profile_selector.removeItem(self.profile_selector.currentIndex())

    def load_profile(self):
        current_profile = self.profile_selector.currentText()
        profile = self.profile.profiles.get(current_profile)
        if profile:
            self.prompt_entry.setPlainText(profile["prompt"])
            self.end_prompt_entry.setPlainText(profile["end_prompt"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('C:\\Users\\gbray\\Desktop\\myscripts\\logo.png'))  # Set window icon with absolute path
    profile = Profile()
    settings = Settings()
    ex = TranscriptApp(profile, settings)
    ex.show()
    sys.exit(app.exec_())
