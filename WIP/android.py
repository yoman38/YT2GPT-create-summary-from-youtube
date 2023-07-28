import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from youtube_transcript_api import YouTubeTranscriptApi
import textwrap

class MyApp(toga.App):
    def startup(self):
        main_box = toga.Box(style=Pack(direction=COLUMN))

        self.link_input = toga.TextInput(placeholder='Paste YouTube video link here')
        self.chunk_size_input = toga.NumberInput(min_value=1, placeholder='Enter the number of characters per chunk')
        self.language_input = toga.TextInput(placeholder='Enter the language for translation')

        self.button = toga.Button('Get transcript', on_press=self.get_transcript)
        self.transcript_output = toga.MultilineTextInput(readonly=True)

        main_box.add(self.link_input)
        main_box.add(self.chunk_size_input)
        main_box.add(self.language_input)
        main_box.add(self.button)
        main_box.add(self.transcript_output)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def get_transcript(self, widget):
        video_link = self.link_input.value
        video_id = video_link.split("=")[-1]
        chunk_size = int(self.chunk_size_input.value)
        language = self.language_input.value

        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            transcript = transcript_list.find_manually_created_transcript([language])
        except:
            transcript = transcript_list.find_generated_transcript([language])
        transcript_data = transcript.fetch()
        transcript_text = " ".join([item['text'] for item in transcript_data])

        sections = textwrap.wrap(transcript_text, chunk_size)
        prompts = self.create_prompts(sections, chunk_size, language)

        self.transcript_output.value = "\n\n".join(prompts)

    def create_prompts(self, sections, chunk_size, language):
        prompts = []
        total_sections = len(sections)
        for i, section in enumerate(sections):
            start_marker = f"[START CHUNK {i+1}/{total_sections}]"
            end_marker = f"[END CHUNK {i+1}/{total_sections}], Remember to list all key points with a bullet list written in [{language}]"
            if i == 0:  # This is the first chunk
                prompts.append(f"From now, you will write in [{language}]. I will provide you with a transcription of spoken content, and I need your help to understand what was said. Please listen carefully and provide a concise bullet-point summary of the main ideas and key points covered in the given text. Include the essential concepts, arguments, or findings, and emphasize any important details or supporting evidence. Make sure to mention the topics discussed in the text and organize your response in a clear and coherent bullet list format. Your summary should condense the information while maintaining accuracy and provide a comprehensive overview of the text's content.\n{start_marker}\n{section}\n{end_marker}")
            else:
                prompts.append(f"{start_marker}\n{section}\n{end_marker}")
        return prompts

def main():
    return MyApp('MyApp', 'org.beeware.myapp')

if __name__ == '__main__':
    main().main_loop()
