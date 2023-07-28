from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
import textwrap

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def transcript_app():
    if request.method == 'POST':
        video_link = request.form.get('video_link')
        video_id = video_link.split("=")[-1]
        chunk_size = int(request.form.get('chunk_size', 0))
        language = request.form.get('language')
        prompt = request.form.get('prompt')
        end_prompt = request.form.get('end_prompt')

        try:
            transcript = get_transcript(video_id)
        except Exception as e:
            return str(e)

        sections = divide_transcript(transcript, chunk_size)
        prompts = create_prompts(sections, chunk_size, language, prompt, end_prompt)
        final_text = f"Retrieve and compile bullet lists created between {1}/{len(prompts)} to {len(prompts)}/{len(prompts)}. Generate a detailed table of contents for a report using [{language}] language. The table of contents should include titles and subtitles, with bullet points under each, encompassing all the topics discussed in the previous bullet points of this conversation. Ensure that the table of contents is written in [{language}]."

        return render_template('transcript.html', prompts=prompts, final_text=final_text)

    return render_template('index.html')


def get_transcript(video_id):
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = transcript_list.find_transcript(['en'])
    return " ".join([t['text'] for t in transcript.fetch()])


def divide_transcript(transcript, chunk_size):
    return textwrap.wrap(transcript, chunk_size)


def create_prompts(sections, chunk_size, language, prompt, end_prompt):
    prompts = []
    for i, section in enumerate(sections):
        prompts.append({
            "language": language,
            "prompt": prompt.format(section),
            "end_prompt": end_prompt.format(section)
        })
    return prompts


if __name__ == "__main__":
    app.run(debug=True)
