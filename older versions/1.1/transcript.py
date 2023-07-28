import tkinter as tk
from tkinter import messagebox
from youtube_transcript_api import YouTubeTranscriptApi
import textwrap

# Step 1: Get the transcript
def get_transcript(video_id):
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    try:
        transcript = transcript_list.find_manually_created_transcript(transcript_list._manually_created_transcripts.keys())
    except:
        transcript = transcript_list.find_generated_transcript(transcript_list._generated_transcripts.keys())
    transcript_data = transcript.fetch()
    transcript_text = " ".join([item['text'] for item in transcript_data])
    return transcript_text

# Step 2: Divide the transcript into sections
def divide_transcript(transcript):
    sections = textwrap.wrap(transcript, 15000)
    return sections

# Step 3: Create the GPT prompts
def create_prompts(sections):
    prompts = []
    total_sections = len(sections)
    for i, section in enumerate(sections):
        start_marker = f"[START CHUNK {i+1}/{total_sections}]"
        end_marker = f"[END CHUNK {i+1}/{total_sections}], now resume this chunk with a bullet list"
        if i == 0:  # This is the first chunk
            prompts.append(f"I will send you a transcription of someone speaking. Help me understand what he said; resume with a bullet list.\n{start_marker}\n{section}\n{end_marker}")
        else:
            prompts.append(f"{start_marker}\n{section}\n{end_marker}")
    return prompts

# Function to handle button click
def handle_click():
    video_id = entry.get()
    transcript = get_transcript(video_id)
    sections = divide_transcript(transcript)
    prompts = create_prompts(sections)
    for i, prompt in enumerate(prompts):
        button = tk.Button(root, text=f"Copy chunk {i+1}/{len(prompts)}", command=lambda p=prompt: copy_to_clipboard(p))
        button.pack()

# Function to copy text to clipboard
def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo("Info", "Text copied to clipboard")

# Create the GUI
root = tk.Tk()
label = tk.Label(root, text="Enter YouTube video ID:")
label.pack()
entry = tk.Entry(root)
entry.pack()
button = tk.Button(root, text="Get transcript", command=handle_click)
button.pack()
root.mainloop()
