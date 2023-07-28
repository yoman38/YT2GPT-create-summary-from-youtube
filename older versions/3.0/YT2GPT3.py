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
        self.setWindowIcon(QIcon('logo.png'))  # Set window icon

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
        self.scrollLayout.addWidget(self.profile_selector)

        self.load_profiles_button = QPushButton("Load selected profile")
        self.load_profiles_button.clicked.connect(self.load_profile)
        self.scrollLayout.addWidget(self.load_profiles_button)

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
        final_button = QPushButton("Copy final text")
        final_button.clicked.connect(partial(self.copy_to_clipboard, final_text))
        self.scrollLayout.addWidget(final_button)

    def handle_clear(self):
        while self.scrollLayout.count():
            item = self.scrollLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.createForm()

    def get_transcript(self, video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        except Exception as e:
            raise Exception(f"Failed to get transcript. {str(e)}")
        full_transcript = ""
        for part in transcript:
            full_transcript += part['text'] + ' '
        return full_transcript

    def divide_transcript(self, transcript, chunk_size):
        return textwrap.wrap(transcript, chunk_size)

    def create_prompts(self, sections, chunk_size, language, prompt, end_prompt):
        total_sections = len(sections)
        prompts = []
        for i, section in enumerate(sections):
            start_marker = f"[START CHUNK {i+1}/{total_sections}]> {prompt if prompt else f'Read the following excerpt from a lecture and summarize it in a bullet list in [{language}] language'}"
            end_marker = f"[END CHUNK {i+1}/{total_sections}]< {end_prompt if end_prompt else f'Remember to list all key points with a bullet list written in [{language}] language'}"
            prompts.append(f"{start_marker}\n{section}\n{end_marker}")
        return prompts

    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "Info", "Text copied to clipboard")

    def save_profile(self):
        name, ok = QInputDialog.getText(self, "Save Profile", "Enter profile name:")
        if ok:
            prompt = self.prompt_entry.toPlainText()
            end_prompt = self.end_prompt_entry.toPlainText()
            self.profile.save_profile(name, prompt, end_prompt)
            self.refresh_profiles()

    def delete_profile(self):
        name = self.profile_selector.currentText()
        if name in self.profile.profiles:
            reply = QMessageBox.question(self, 'Delete Confirmation', f"Are you sure you want to delete profile '{name}'?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.profile.delete_profile(name)
                self.refresh_profiles()

    def load_profile(self):
        name = self.profile_selector.currentText()
        if name in self.profile.profiles:
            profile = self.profile.profiles[name]
            self.prompt_entry.setText(profile["prompt"])
            self.end_prompt_entry.setText(profile["end_prompt"])

    def refresh_profiles(self):
        self.profile_selector.clear()
        self.profile_selector.addItems(self.profile.profiles.keys())


def main():
    app = QApplication(sys.argv)
    profile = Profile()
    settings = Settings()
    ex = TranscriptApp(profile, settings)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
