from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox
from PyQt5.QtGui import QIcon
from youtube_transcript_api import YouTubeTranscriptApi
import textwrap
import sys
from functools import partial

class TranscriptApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Set the window icon
        self.setWindowIcon(QIcon('logo.ico'))

        self.layout = QVBoxLayout()

        self.label_link = QLabel("Paste YouTube video link:")
        self.layout.addWidget(self.label_link)
        self.entry = QLineEdit()
        self.layout.addWidget(self.entry)

        self.label_chunk_size = QLabel("Enter the number of characters per chunk (recommended: 8000 for GPT-3, 15000 for GPT-4):")
        self.layout.addWidget(self.label_chunk_size)
        self.chunk_size_entry = QLineEdit()
        self.layout.addWidget(self.chunk_size_entry)

        self.label_language = QLabel("Enter the language for translation:")
        self.layout.addWidget(self.label_language)
        self.language_entry = QLineEdit()
        self.layout.addWidget(self.language_entry)

        self.button = QPushButton("Get transcript")
        self.button.clicked.connect(self.handle_click)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def handle_click(self):
        video_link = self.entry.text()
        video_id = video_link.split("=")[-1]
        try:
            chunk_size = int(self.chunk_size_entry.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Chunk size must be an integer.")
            return

        language = self.language_entry.text()

        try:
            transcript = self.get_transcript(video_id)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        sections = self.divide_transcript(transcript, chunk_size)
        prompts = self.create_prompts(sections, chunk_size, language)

        for i, prompt in enumerate(prompts):
            button = QPushButton(f"Copy chunk {i+1}/{len(prompts)}")
            button.clicked.connect(partial(self.copy_to_clipboard, prompt))
            self.layout.addWidget(button)

        final_text = f"Remember all the bullet lists you wrote so far. Remember the bullet list from {0}/{len(prompts)} to last section/{len(prompts)}. Now write a 8000 character text summarizing the key points."
        final_button = QPushButton("Copy final text")
        final_button.clicked.connect(partial(self.copy_to_clipboard, final_text))
        self.layout.addWidget(final_button)

    def get_transcript(self, video_id):
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            transcript = transcript_list.find_manually_created_transcript(transcript_list._manually_created_transcripts.keys())
        except:
            transcript = transcript_list.find_generated_transcript(transcript_list._generated_transcripts.keys())
        transcript_data = transcript.fetch()
        transcript_text = " ".join([item['text'] for item in transcript_data])
        return transcript_text

    def divide_transcript(self, transcript, chunk_size):
        sections = textwrap.wrap(transcript, chunk_size)
        return sections

    def create_prompts(self, sections, chunk_size, language):
        prompts = []
        total_sections = len(sections)
        for i, section in enumerate(sections):
            start_marker = f"[START CHUNK {i+1}/{total_sections}]"
            end_marker = f"[END CHUNK {i+1}/{total_sections}], Remember to list all key points with a bullet list written in [{language}]"
            if i == 0:  # This is the first chunk
                prompts.append(f"From now, you will write in [{language}]. I will provide you with a transcription of spoken content, and I need your help to understand what was said. Please read carefully and provide a concise bullet-point summary of the main ideas and key points covered in the given text. Include the essential concepts, arguments, or findings, and emphasize any important details or supporting evidence. Make sure to mention the topics discussed in the text and organize your response in a coherent bullet list format. Your summary should condense the information while maintaining accuracy and provide a comprehensive overview of the text's content. Make sure to note the formulas and statistics mentionned. \n{start_marker}\n{section}\n{end_marker}")
            else:
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
