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
def divide_transcript(transcript, chunk_size):
    sections = textwrap.wrap(transcript, chunk_size)
    return sections

# Step 3: Create the GPT prompts
def create_prompts(sections, chunk_size, language):
    prompts = []
    total_sections = len(sections)
    for i, section in enumerate(sections):
        start_marker = f"[START CHUNK {i+1}/{total_sections}]"
        end_marker = f"[END CHUNK {i+1}/{total_sections}], Remember to list all key points with a bullet list written in [{language}]"
        if i == 0:  # This is the first chunk
            prompts.append(f"From now, you will write in [{language}]. I will provide you with a transcription of spoken content, and I need your help to understand what was said. Please read carefully and provide a concise bullet-point summary of the main ideas and key points covered in the given text. Include the essential concepts, arguments, or findings, and emphasize any important details or supporting evidence. Make sure to mention the topics discussed in the text and organize your response in a coherent bullet list format. Your summary should condense the information while maintaining accuracy and provide a comprehensive overview of the text's content. Technical informations such as statistics should be added to the bullet list.\n{start_marker}\n{section}\n{end_marker}")
        else:
            prompts.append(f"{start_marker}\n{section}\n{end_marker}")
    return prompts

# Function to handle button click
def handle_click():
    video_link = entry.get()
    video_id = video_link.split("=")[-1]  # Extract the video ID from the link
    chunk_size = int(chunk_size_entry.get())  # Get the chosen chunk size
    language = language_entry.get()  # Get the chosen language

    transcript = get_transcript(video_id)
    sections = divide_transcript(transcript, chunk_size)
    prompts = create_prompts(sections, chunk_size, language)

    for i, prompt in enumerate(prompts):
        button = tk.Button(root, text=f"Copy chunk {i+1}/{len(prompts)}", command=lambda p=prompt: copy_to_clipboard(p))
        button.pack()

   # Add the final button
    final_text = f"Recall the bullet lists you have previously created, specifically from {1}/{len(prompts)} to {len(prompts)}/{len(prompts)}. Utilizing [{language}], craft a comprehensive table of contents for a report, incorporating bullet points under each title and subtitle to provide a complete list of their respective content. Don't forget to write in [{language}]"
    final_button = tk.Button(root, text="Copy final prompt", command=lambda: copy_to_clipboard(final_text))
    final_button.pack()

# Function to copy text to clipboard
def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo("Info", "Text copied to clipboard")

# Create the GUI
root = tk.Tk()

# Video Link
label_link = tk.Label(root, text="Paste YouTube video link:")
label_link.pack()
entry = tk.Entry(root)
entry.pack()

# Chunk Size
label_chunk_size = tk.Label(root, text="Enter the number of characters per chunk (recommended: 8000 for GPT-3, 15000 for GPT-4):")
label_chunk_size.pack()
chunk_size_entry = tk.Entry(root)
chunk_size_entry.pack()

# Language
label_language = tk.Label(root, text="Enter the language for translation:")
label_language.pack()
language_entry = tk.Entry(root)
language_entry.pack()

button = tk.Button(root, text="Get transcript", command=handle_click)
button.pack()

root.mainloop()
