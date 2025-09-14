import os
import gradio as gr
import subprocess
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types
from typing import Optional
from pydantic import BaseModel

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=GOOGLE_API_KEY)


class MotionLabel(BaseModel):
    label: Optional[str]


def save_temp_file(file_bytes, filename="temp.fbx", temp_dir="./temp/"):
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, filename)
    with open(temp_path, "wb") as f:
        f.write(file_bytes)
    return temp_path


def convert_fbx_to_mp4(fbx_path):
    subprocess.run(["uv", "run", "convert.py"], check=True)
    mp4_path = fbx_path.replace(".fbx", ".mp4")
    if os.path.exists(mp4_path):
        return mp4_path
    return None


def generate_motion_label_from_video(video_path, lang):
    video_bytes = open(video_path, "rb").read()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part(inline_data=types.Blob(data=video_bytes, mime_type="video/mp4")),
            f"You are an expert in motion labeling. Describe the action that the person in the given video file is performing in one sentence in {lang}. If you cannot identify the action, write null. Do not include a subject under any circumstances.",
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": MotionLabel,
            "temperature": 0.1,
        },
    )
    return response.parsed.label  # type: ignore


def generate_motion_label_from_action(action, lang):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            f"You are an expert in motion labeling. Write a one-sentence label in {lang} that starts with 'Doing {action}' and describes the motion style or manner of the action, without using any subject."
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": MotionLabel,
            "temperature": 0.1,
        },
    )
    return response.parsed.label  # type: ignore


def upload_to_api(fbx_path, label):
    files = [
        (
            "files",
            (os.path.basename(fbx_path), open(fbx_path, "rb"), "model/fbx"),
        )
    ]
    data = {"label": label}
    res = requests.post("http://bun:3000/docs", files=files, data=data)
    return res.status_code == 200, res.text


def handle_file(file, lang, use_filename):
    if file is None:
        return "ファイルがアップロードされていません", None, None

    filename = os.path.basename(file.name)
    action = os.path.splitext(filename)[0]

    binary_data = open(file, "rb").read()
    temp_input_path = save_temp_file(binary_data)

    try:
        if use_filename:
            final_label = generate_motion_label_from_action(action, lang)
            mp4_path = None
        else:
            mp4_path = convert_fbx_to_mp4(temp_input_path)
            if not mp4_path:
                return "動画変換に失敗しました。", None, None

            final_label = generate_motion_label_from_video(mp4_path, lang)
            if final_label == "null":
                return "ラベルの変換に失敗しました。", mp4_path, None

        success, api_msg = upload_to_api(temp_input_path, final_label)
        if success:
            return "アップロード完了", mp4_path, final_label
        else:
            return f"APIエラー: {api_msg}", mp4_path, final_label

    except Exception as e:
        return f"エラーが発生しました: {str(e)}", None, None


with gr.Blocks() as demo:
    gr.Markdown("# MRTalk-Motion Uploader")

    with gr.Row():
        with gr.Column():
            upload_btn = gr.UploadButton(
                "ファイルを選択（.fbx）",
                file_types=[".fbx"],
                file_count="single",
                variant="primary",
            )

            lang_dropdown = gr.Dropdown(
                ["日本語", "English"], value="English", label="ラベルの言語"
            )

            use_filename_checkbox = gr.Checkbox(
                label="ファイル名からラベルを生成する", value=False
            )

            output_text = gr.Textbox(
                label="処理結果",
                placeholder="ファイルをアップロードすると、ここに結果が表示されます",
                lines=2,
            )

            label_text = gr.Textbox(
                label="生成されたラベル",
                placeholder="モーションのラベルが表示されます",
                lines=2,
            )

        with gr.Column():
            output_video = gr.Video(label="変換後の動画", visible=True)

    upload_btn.upload(
        fn=handle_file,
        inputs=[upload_btn, lang_dropdown, use_filename_checkbox],
        outputs=[output_text, output_video, label_text],
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
