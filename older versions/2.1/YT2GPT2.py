from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox, QScrollArea, QSizePolicy, QTextEdit
from PyQt5.QtGui import QIcon, QPixmap
from youtube_transcript_api import YouTubeTranscriptApi
import textwrap
import sys
from functools import partial

class TranscriptApp(QWidget):
    def __init__(self):
        super().__init__()
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
        self.scrollLayout.addWidget(self.chunk_size_entry)

        self.label_language = QLabel("Enter the language for translation:")
        self.scrollLayout.addWidget(self.label_language)
        self.language_entry = QLineEdit()
        self.scrollLayout.addWidget(self.language_entry)

        self.label_prompt = QLabel("Enter your custom prompt (optional):")
        self.scrollLayout.addWidget(self.label_prompt)
        self.prompt_entry = QTextEdit()
        self.scrollLayout.addWidget(self.prompt_entry)

        self.label_end_prompt = QLabel("Enter the end prompt (optional):")  # New label for end prompt
        self.scrollLayout.addWidget(self.label_end_prompt)
        self.end_prompt_entry = QTextEdit()  # New entry for end prompt
        self.scrollLayout.addWidget(self.end_prompt_entry)

        self.button = QPushButton("Get transcript")
        self.button.clicked.connect(self.handle_click)
        self.scrollLayout.addWidget(self.button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.handle_clear)
        self.scrollLayout.addWidget(self.clear_button)

    def handle_click(self):
        video_link = self.entry.text()
        video_id = video_link.split("=")[-1]
        try:
            chunk_size = int(self.chunk_size_entry.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Chunk size must be an integer.")
            return

        language = self.language_entry.text()
        prompt = self.prompt_entry.toPlainText()
        end_prompt = self.end_prompt_entry.toPlainText()  # New: Fetch the end prompt

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
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = None

        for t in transcript_list:
            if not t.is_generated:
                transcript = t.fetch()
                break

        if not transcript:  # If no manually created transcript was found
            for t in transcript_list:
                if t.is_generated:
                    transcript = t.fetch()
                    break

        if not transcript:
            raise Exception("No transcript available.")

        transcript_text = " ".join([item['text'] for item in transcript])
        return transcript_text

    def divide_transcript(self, transcript, chunk_size):
        sections = textwrap.wrap(transcript, chunk_size)
        return sections

    def create_prompts(self, sections, chunk_size, language, prompt, end_prompt):  # New: end_prompt argument
        prompts = []
        total_sections = len(sections)
        for i, section in enumerate(sections):
            if prompt:  # If a custom prompt is provided
                start_marker = f"{prompt}. Write in [{language}]. >[START CHUNK {i+1}/{total_sections}]"
            else:  # If no custom prompt, use the default prompt
                start_marker = f"Make sure to mention the topics discussed in the text and organize your response in a coherent bullet list format. Your summary should condense the information while maintaining accuracy and provide a comprehensive overview of the text's content. SEPARATLY, you will note every formulas and statistics mentioned. >[START CHUNK {i+1}/{total_sections}]"
            if end_prompt:  # If a custom end prompt is provided
                end_marker = f"[END CHUNK {i+1}/{total_sections}]< {end_prompt}. Use [{language}]"
            else:  # If no custom end prompt, use the default prompt
                end_marker = f"[END CHUNK {i+1}/{total_sections}]< Remember to list all key points with a bullet list written in [{language}]"
            prompts.append(f"{start_marker}\n{section}\n{end_marker}")
        return prompts

    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "Info", "Text copied to clipboard")

def main():
    app = QApplication(sys.argv)

    ex = TranscriptApp()
    ex.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
