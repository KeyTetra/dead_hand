import yt_dlp
import srt
import json
import string
recon = []
URLS = [
    "https://www.youtube.com/watch?v=3h676810CKg",
    "https://www.youtube.com/watch?v=drjGxV32fns",
    "https://www.youtube.com/watch?v=FJ6uvFNc7gI",
    "https://www.youtube.com/watch?v=EtxeZqdc6wY",
    "https://www.youtube.com/watch?v=uiRS37ec_8g",
    "https://www.youtube.com/watch?v=hLC2yQ5JBuM",
    "https://www.youtube.com/watch?v=htGu9XpJy6o",
    "https://www.youtube.com/watch?v=kmZ58blYvaY",
    "https://www.youtube.com/watch?v=M2eLPjjTBbY",
    "https://www.youtube.com/watch?v=LV4nRsN1RoA",
    "https://www.youtube.com/watch?v=Fyodgbf8_1I",
    "https://www.youtube.com/watch?v=G76PWoS0odE",
    "https://www.youtube.com/watch?v=tz6nvJMnKq0",
    "https://www.youtube.com/watch?v=UoN9INB6bbw",
    "https://www.youtube.com/watch?v=BWy2s0My2Hc",
    "https://www.youtube.com/watch?v=BevhLS8jvtQ",
    "https://www.youtube.com/watch?v=_3nZB7-jTKI",
    "https://www.youtube.com/watch?v=u1JIVYWDu2U"
]

def srt_to_plain_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        subtitle_generator = srt.parse(f)
        transcript = ""
        for subtitle in subtitle_generator:
            # Add the content to the transcript, preserving internal line breaks
            transcript += subtitle.content + " "
    return transcript

def remove_punctuation(text):
    """
    Removes all common punctuation from a string.

    Args:
      text: The input string with potential punctuation.

    Returns:
      A new string with punctuation removed.
    """
    # Create a translation table that maps every punctuation character to None (effectively removing it)
    # The first two arguments are empty strings (no character mapping), and the third specifies characters to delete
    translator = str.maketrans('', '', string.punctuation)

    # Apply the translation table to the input string
    return text.translate(translator)

i_count = 0
for url in URLS:
    try:
        ydl_opts = {
            'writeautomaticsub': True,  # Download automatic subtitles (use 'writesubtitles': True for manually added)
            'subtitlesformat': 'srt',  # Specify format (srt, vtt, etc.)
            'skip_download': True,  # Only download subtitles, not the video
            'outtmpl': f'srts/{i_count}',  # Output filename template (e.g., 'aKEatGCJUGM.en.srt')
            'subtitleslangs': ['en']  # Specify language(s)
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        file_path = f'srts/{i_count}.en.srt'
        plain_text = srt_to_plain_text(file_path)
        recon.append({"plain_text": remove_punctuation(plain_text)})
        i_count += 1
    except Exception as e:
        print("didnt work")
        print(e)

with open('../debug_data.json', 'w', encoding='utf-8') as f:
    json.dump(recon, f, ensure_ascii=False, indent=4)