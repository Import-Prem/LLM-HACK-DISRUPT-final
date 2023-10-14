__author__ = "Aravindan Ravi, Prem Khemani, and Griteja Reddy"
__copyright__ = "Copyright 2023, LLM JAM"
__version__ = "1.0.0"
__maintainers__ = "Aravindan ravi & Prem Khemani"
__email__ = "raravind.ds@gmail.com"
__status__ = "Production"



import uuid, shutil  
# from logger import logger
from celery import Celery

from utilities import * 
from prompt_template import * 


import streamlit as st 

# Set the page title
st.set_page_config(
    page_title="One Short Generation",page_icon="📸"
    #layout="wide",
)

 
# Add a title to your application
st.title("One Shot Video Generation 📸")
hide_streamlit_style = """
            <style>
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def complete_pipeline_function(topic, goal, unique_id): 

    ## temporary folder name
    current_foldername = str(uuid.uuid4())

    ## logger 
    # logger.info(f"Got the inptus: \ntopic:{topic}\ngoal:{goal}")
    # logger.info(f"current_foldername: {current_foldername}")

    ## Get the prompt template for image description generation
    prompt_template = imagedescription_and_script_prompt_tempalte(topic=topic, goal=goal)

    ## Get the imge descriptions
    image_prompts, texts = fetch_imagedescription_and_script(prompt_template)

    ## logger 
    # logger.info(f"Got the image_prompts and texts:\nImage_prompts:\n{image_prompts}\ntexts:\n{texts}")

    ## Generate the Images
    image_generation_result = generate_images(prompts=image_prompts, fname=current_foldername)

    ## logger 
    # logger.info("Image generated succesfully 😌")

    ## Get the voice id 
    voice_id = get_voice_id() # currently we are grabbing the first voice :) 

    ## Generate the audio 
    audio_generation_result = generate_audio(texts=texts, current_foldername=current_foldername, voice_id=voice_id)

    ## logger
    # logger.info("Audio generation done for each image ⭐")

    ## Combine audio and video 
    final_path = create_combined_video_audio(current_foldername, "combined_video.mp4")

    ## logger 
    # logger.info("Combined all the video and images, video sent succesfully to drive 🪄")
    # logger.info("Video sending to bubble, wait for the success message") 
    # logger.info(f"final_path: {final_path}")

    ## send_to_drive(final_path, current_foldername)
    # send_to_bubble(final_path,unique_id)


    ## logger 
    # logger.info("File succesfully sent to drive")

    # shutil.rmtree(current_foldername)

    ## logger 
    # logger.info("folder removed succesffully :) ")
    

    ## delete this 
    return final_path 



topic = st.text_input(label = "Enter your topic:")
description =  st.text_input(label = "Enter the desription:") 


unique_id = 1234 
# Define the desired width (you can choose any value, it will maintain a 1:1 aspect ratio)
video_width = 400

# Apply custom CSS to resize the video container while maintaining the aspect ratio
st.markdown(
    f"""
    <style>
    .stVideo > div > div {{
        width: {video_width}px !important;
        height: {video_width}px !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        overflow: hidden !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

if st.button("Submit"): 
    with st.spinner("Video is generating...."): 

        output = complete_pipeline_function(topic, description, unique_id)

        video_file = open(output, 'rb')
        video_bytes = video_file.read()

        st.balloons()
        st.video(video_bytes)

