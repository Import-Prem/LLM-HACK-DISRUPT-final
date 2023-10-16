import openai 
openai.api_key = "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"


audio_file= open("383428ff-a9c6-4c60-be84-96604f831e09/combined_video.mp4", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)

print(transcript)