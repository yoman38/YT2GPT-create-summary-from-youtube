# YT2GPT (infinite liberty version)
 Retrieve transcriptions from youtube and convert it to ready to copy/paste chatGPT prompt

**YouTube Transcript - README**

**Description**

YT2GPT is an innovative application that uses AI to convert YouTube video content into easily digestible summaries. Usable on any AI language model and relying on YouTube's transcript API, it offers customized summaries based on user-defined or pre-set prompts. For instance, users can create prompts to develop an engineering report, a coding tutorial, or even a whole course outline from a YouTube video. Also, it can translate content into different languages, making it understable worldwide. Its user-friendly interface, built with PyQt5, keeps users updated on their requests' status. 

One of the significant advantages of GPT2YT is that it uses the information from the video to guide the AI's summarization. This can be seen as a form of fine-tuning the AI model, which is more effective than prompting the AI without any context. The AI isn't starting from scratch but uses the video's content as a foundation, filling in the gaps intelligently, ensuring the summary stays true to the original content.

**Installation**

INSTALL > COPY/PASTE folder YT2GPTX.X to the directory you want.
Go to DIST>YT2GPT.EXE to launch it. It should work on MAC but would be better with another compilation. That might come.
Create a shortcut if you need it. 

**Long description**

General Use:
1. Input the YouTube video link in the "Paste YouTube video link" field.
2. Enter the desired number of characters per chunk in the "Enter the number of characters per chunk" field. (recommended: 8000 for GPT-3, 15000 for GPT-4)
3. Specify the language for translation in the "Enter the language for translation" field.
4. Optionally, select a saved profile from the "Select a profile" dropdown list to load custom prompts or create a new profile.
5. If needed, enter a custom prompt in the "Enter your custom prompt (optional)" field and/or a custom ending prompt in the "Enter your custom ending prompt (optional)" field.
6. Click the "Get transcript" button to generate the prompts for the YouTube video transcript.
7. The application will provide a series of buttons to copy individual prompts for each chunk and a final button to copy a prompt for generating a comprehensive summary from all chunks.



**Changelog:**

###Version v1.1:

- Basic functionality with fixed chunk size and simple prompt for bullet lists.

###Version v1.2:

- Enhanced GUI with support for customizable chunk size and multilingual prompts.
- Improved GPT prompts for more accurate and coherent summarization.

###Version v1.3:

- Introduced a final button for generating a table of contents.
- Incorporated technical information in the prompts to ensure comprehensive summaries.
- Enhanced user guidance throughout the summarization process.

###Version v1.4:

- Complete redesign with PyQt5 for a graphical user interface (GUI).
- Added error handling for invalid inputs and user feedback through QMessageBox.
- Integrated clipboard functionality for easy prompt copying.
- Improved the final prompt to include recalling bullet lists from all previous sections.

###Version v2.0:

- Enhanced GUI with scrollable layout for better organization and usability.
- Added support for custom prompts and end prompts for generated prompts.
- Improved error handling for input validation.

###Version v2.1:

- Added support for an end prompt in the generated prompts.
- Introduced a "Clear" button to reset the form and clear all generated prompts.
- Optimized YouTube transcript retrieval for better accuracy.
- Improved code structure and layout for better readability.

###Version v3.0:

- Introduced the ability to save and load custom profiles.
- Added options to set a default chunk size and language in the settings.
- Enhanced user experience and flexibility in generating prompts.

###Version v4.0:

- Enhanced YouTube transcript retrieval to handle multiple languages and accents more effectively.
- Improved the default prompts to provide clearer instructions and guidance to users.
- Introduced "Note all the statistics and formulas separately" as a standard prompt.
- Changed the behavior of the "Copy final text" button to copy the final table of contents prompt.
- Fixed a bug causing the application to crash when deleting profiles.

###Version v4.1:

- Improved UI layout with dynamic spacing for better readability and usability.
- Added further instructions to the default prompts for clearer summarization guidance.
- Updated the "Remember to summarize key ideas in bullet points" prompt for better clarity.
- Optimized window icon loading for compatibility with executable files.

###Version v4.2:

- Enhanced YouTube transcript retrieval to handle both manually created and automatically generated transcripts.
- Improved overall application stability and error handling.
- Updated window title to "GPT2YT v4.2" for consistency and version tracking.

Upcoming improvements: turning the button to green once copied to clipboard.
---

If you have any further questions or need additional assistance, please feel free to reach out. Happy summarizing!
