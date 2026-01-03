import yt_dlp
import srt

URL = 'https://www.youtube.com/watch?v=T_oJkFLnYAs'



with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([URL])
    print(ydl.download([URL]))

def srt_to_plain_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        subtitle_generator = srt.parse(f)
        transcript = ""
        for subtitle in subtitle_generator:
            # Add the content to the transcript, preserving internal line breaks
            transcript += subtitle.content + "\n\n"
    return transcript

# Example usage:
file_path = 'j.en.srt'
plain_text = srt_to_plain_text(file_path)
print(plain_text)

# Optionally, save to a .txt file
with open('output_transcript.txt', 'w', encoding='utf-8') as f:
    f.write(plain_text)