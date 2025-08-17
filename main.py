import os
import gradio as gr
import subprocess


def handle_file(file, progress=gr.Progress()):
    if file is None:
        return "ファイルがアップロードされていません", None

    progress(0.2, desc="ファイルを読み込み中...")

    with open(file, "rb") as f:
        binary_data = f.read()

    temp_input_path = os.path.join("./temp/", "temp.fbx")

    progress(0.4, desc="ファイルを保存中...")

    with open(temp_input_path, "wb") as f:
        f.write(binary_data)

    progress(0.6, desc="MP4に変換中...")

    try:
        subprocess.run(["uv", "run", "convert.py"])
        progress(1.0, desc="完了！")

        mp4_path = temp_input_path.replace(".fbx", ".mp4")
        if os.path.exists(mp4_path):
            return "変換完了", mp4_path
        else:
            return "処理完了", None

    except Exception as e:
        return f"エラーが発生しました: {str(e)}", None


with gr.Blocks() as demo:
    gr.Markdown("""
    # FBX to MP4 Converter
    FBXファイルをMP4動画に変換します
    """)

    with gr.Row():
        with gr.Column():
            upload_btn = gr.UploadButton(
                "ファイルを選択（.fbx)",
                file_types=[".fbx"],
                file_count="single",
                variant="primary",
            )

            output_text = gr.Textbox(
                label="処理結果",
                placeholder="ファイルをアップロードすると、ここに結果が表示されます",
                lines=2,
            )

        with gr.Column():
            output_video = gr.Video(label="変換後の動画", visible=True)

    upload_btn.upload(
        fn=handle_file, inputs=upload_btn, outputs=[output_text, output_video]
    )

demo.launch()
