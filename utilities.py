
import numpy as np 
from PIL import Image
from dotenv import load_dotenv 
import requests, json, os, io, random, cv2 
from moviepy.editor import AudioFileClip, concatenate_audioclips, concatenate_videoclips, ImageClip

load_dotenv() 
openai_api_key=os.getenv("OPENAI_API_KEY")
segmind_api_key=os.getenv("SEGMIND_API_KEY")
elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY")

## Setting up URLs
chatgpt_url = "https://api.openai.com/v1/chat/completions"
chatgpt_headers = {
    "content-type": "application/json",
    "Authorization":"Bearer {}".format(openai_api_key)}



def fetch_imagedescription_and_script(prompt:str):

    messages = [
        {"role": "system", "content": "You are an expert short form video script writer for Instagram Reels and Youtube shorts."},
        {"role": "user", "content": prompt}
    ]

    chatgpt_payload = {
        "model": "gpt-3.5-turbo-16k",
        "messages": messages,
        "temperature": 1.3,
        "max_tokens": 2000,
        "top_p": 1,
        "stop": ["###"]
    }

    # Make the request to OpenAI's API
    response = requests.post(chatgpt_url, json=chatgpt_payload, headers=chatgpt_headers)
    response_json = response.json()

    # Extract data from the API's response
    output = json.loads(response_json['choices'][0]['message']['content'].strip())

    image_prompts = [k['image_description'] for k in output]
    texts = [k['text'] for k in output]

    return image_prompts, texts


def generate_images(prompts, fname:str) -> str:

    url = "https://api.segmind.com/v1/sdxl1.0-txt2img"
    headers = {'x-api-key': segmind_api_key}

    # Create a folder for the UUID if it doesn't exist
    if not os.path.exists(fname):
        os.makedirs(fname)

    num_images = len(prompts)
    currentseed = random.randint(1, 1000000)

    for i, prompt in enumerate(prompts):

        final_prompt = "((perfect quality)), ((cinematic photo:1.3)), ((raw candid)), 4k, {}, no occlusion, Fujifilm XT3, highly detailed, bokeh, cinemascope".format(prompt.strip('.'))
        data = {
            "prompt": final_prompt,
            "negative_prompt": "((deformed)), ((limbs cut off)), ((quotes)), ((extra fingers)), ((deformed hands)), extra limbs, disfigured, blurry, bad anatomy, absent limbs, blurred, watermark, disproportionate, grainy, signature, cut off, missing legs, missing arms, poorly drawn face, bad face, fused face, cloned face, worst face, three crus, extra crus, fused crus, worst feet, three feet, fused feet, fused thigh, three thigh, fused thigh, extra thigh, worst thigh, missing fingers, extra fingers, ugly fingers, long fingers, horn, extra eyes, amputation, disconnected limbs",
            "style": "hdr",
            "samples": 1,
            "scheduler": "UniPC",
            "num_inference_steps": 30,
            "guidance_scale": 8,
            "strength": 1,
            "seed": currentseed,
            "img_width": 1024,
            "img_height": 1024,
            "refiner": "yes",
            "base64": False
                  }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200 and response.headers.get('content-type') == 'image/jpeg':
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))

            image_filename = os.path.join(fname, f"{i + 1}.jpg")
            image.save(image_filename)

            print(f"Image {i + 1}/{num_images} saved as '{image_filename}'")

        else:
            print (response.text)
            print(f"Error: Failed to retrieve or save image {i + 1}")

    return "Generated"


def generate_audio(texts:str, current_foldername:str, voice_id): 
    for i, text in enumerate(texts):
        output_filename= str(i + 1)
        generate_and_save_audio(text, current_foldername, output_filename, voice_id, elevenlabs_api_key)


def generate_and_save_audio(text, 
                            foldername, 
                            filename, 
                            voice_id, 
                            elevenlabs_apikey, 
                            model_id="eleven_multilingual_v2", 
                            stability=0.4, 
                            similarity_boost=0.80
                            ):

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elevenlabs_apikey
    }

    data = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        print(response.text)
    else:
        file_path = f"{foldername}/{filename}.mp3"
        with open(file_path, 'wb') as f:
            f.write(response.content)

    return "Generated"


def get_voice_id(): 
    url = "https://api.elevenlabs.io/v1/voices"

    headers = {
    "Accept": "application/json",
    "xi-api-key": "4d9fc19032ac200cf46430ab0daeae05"
    }

    response = requests.get(url, headers=headers)
    response = response.text
    response = json.loads(response)

    return response['voices'][0]['voice_id'] # currently taking the first voice id  


def create_combined_video_audio(mp3_folder, output_filename, output_resolution=(1080, 1920), fps=24):
    
    mp3_files = sorted([file for file in os.listdir(mp3_folder) if file.endswith(".mp3")])
    mp3_files = sorted(mp3_files, key=lambda x: int(x.split('.')[0]))

    audio_clips = []
    video_clips = []

    for mp3_file in mp3_files:
        audio_clip = AudioFileClip(os.path.join(mp3_folder, mp3_file))
        audio_clips.append(audio_clip)

        # Load the corresponding image for each mp3 and set its duration to match the mp3's duration
        img_path = os.path.join(mp3_folder, f"{mp3_file.split('.')[0]}.jpg")
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB format

        # Resize the original image to 1080x1080
        image_resized = cv2.resize(image, (1080, 1080))

        # Blur the image
        blurred_img = cv2.GaussianBlur(image, (0, 0), 30)
        blurred_img = cv2.resize(blurred_img, output_resolution)

        # Overlay the original image on the blurred one
        y_offset = (output_resolution[1] - 1080) // 2
        blurred_img[y_offset:y_offset+1080, :] = image_resized

        video_clip = ImageClip(np.array(blurred_img), duration=audio_clip.duration)
        video_clips.append(video_clip)

    final_audio = concatenate_audioclips(audio_clips)
    final_video = concatenate_videoclips(video_clips, method="compose")
    final_video = final_video.with_audio(final_audio)
    finalpath = mp3_folder+"/"+output_filename

    final_video.write_videofile(finalpath, fps=fps, codec='libx264',audio_codec="aac")

    return finalpath
