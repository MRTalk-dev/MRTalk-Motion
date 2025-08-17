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


def generate_label(path: str, lang: str):
    video_file_name = path
    video_bytes = open(video_file_name, "rb").read()

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part(inline_data=types.Blob(data=video_bytes, mime_type="video/mp4")),
            f"あなたは、モーションのラベル付けの専門家です。与えられた動画ファイルで示されている動きを、{lang}で詳細に説明してください。何の動きだかわからないときは、nullを入れてください。絶対に 動いている人の情報などはいりません。動きの情報のみを入れてください。",
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": MotionLabel,
            "temperature": 0.1,
        },
    )

    return response.parsed


def handle_file(file, lang):
    if file is None:
        return "ファイルがアップロードされていません", None, None

    with open(file, "rb") as f:
        binary_data = f.read()

    temp_input_path = os.path.join("./temp/", "temp.fbx")

    os.makedirs("./temp/", exist_ok=True)
    with open(temp_input_path, "wb") as f:
        f.write(binary_data)

    try:
        subprocess.run(["uv", "run", "convert.py"], check=True)

        mp4_path = temp_input_path.replace(".fbx", ".mp4")
        if os.path.exists(mp4_path):
            label = generate_label(mp4_path, lang)
            final_label = label.label

            if final_label != "null":
                files = [
                    (
                        "files",
                        (
                            "temp.fbx",
                            open(temp_input_path, "rb"),
                            "model/fbx",
                        ),
                    )
                ]
                data = {"label": final_label}
                res = requests.post(
                    "http://localhost:3000/docs", files=files, data=data
                )

                if res.status_code == 200:
                    return "アップロード完了", mp4_path, final_label
                else:
                    return f"APIエラー: {res.text}", mp4_path, final_label
            else:
                return "ラベルの変換に失敗しました。", mp4_path, None

        else:
            return "動画変換に失敗しました。", None, None

    except Exception as e:
        return f"エラーが発生しました: {str(e)}", None, None


with gr.Blocks() as demo:
    gr.Markdown("""
    # MRTalk-Motion Uploader
    """)

    with gr.Row():
        with gr.Column():
            upload_btn = gr.UploadButton(
                "ファイルを選択（.fbx）",
                file_types=[".fbx"],
                file_count="single",
                variant="primary",
            )

            lang_dropdown = gr.Dropdown(
                ["日本語", "English"], value="日本語", label="ラベルの言語"
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
        inputs=[upload_btn, lang_dropdown],
        outputs=[output_text, output_video, label_text],
    )

demo.launch()
