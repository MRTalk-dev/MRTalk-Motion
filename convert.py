from fbx2video.src.main import render_fbx_to_mp4
import os

temp_input_path = os.path.join("./temp/", "temp.fbx")
render_fbx_to_mp4(temp_input_path, "./temp/")
