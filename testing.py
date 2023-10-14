import streamlit as st 


video_file = open("08aa745b-52bb-4915-82e8-99107be230b3/combined_video.mp4", 'rb')
video_bytes = video_file.read()

st.video(video_bytes)