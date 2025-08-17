import bpy
import os


def render_fbx_to_mp4(fbx_path, output_dir):
    """指定されたFBXファイルをレンダリングしてMP4として保存する"""

    # シーンをクリアする
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    # FBXファイルをインポート
    bpy.ops.import_scene.fbx(filepath=fbx_path)

    # カメラを追加（モデル全身が見える正面）
    bpy.ops.object.camera_add(location=(0, -4, 2.5))  # 少し前で少し下げる
    camera = bpy.context.object
    camera.rotation_euler = (1.2, 0, 0)  # 正面を向く
    bpy.context.scene.camera = camera

    # メインライト（正面右上）
    bpy.ops.object.light_add(type="SUN", location=(4, -4, 6))
    light = bpy.context.object
    light.data.energy = 10
    light.rotation_euler = (0.9, 0, 0.7)

    # 補助ライト（正面左上）
    bpy.ops.object.light_add(type="SUN", location=(-4, -4, 6))
    fill_light = bpy.context.object
    fill_light.data.energy = 2
    fill_light.rotation_euler = (0.9, 0, -0.7)

    # 出力設定
    filename = os.path.splitext(os.path.basename(fbx_path))[0]
    output_path = os.path.abspath(os.path.join(output_dir, filename + ".mp4"))
    print(f"出力パス: {output_path}")

    scene = bpy.context.scene

    # 高速レンダリングのための設定
    scene.render.engine = "BLENDER_EEVEE_NEXT"  # Eevee NextはCyclesより高速
    scene.eevee.taa_render_samples = 8  # サンプル数を大幅削減（デフォルト64→8）
    scene.render.resolution_x = 640  # 解像度を下げて高速化
    scene.render.resolution_y = 480
    scene.render.resolution_percentage = 100

    # 影を無効にして高速化
    scene.eevee.use_shadows = False

    # 出力設定
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.filepath = output_path

    # アニメーションの実際の長さを取得
    # インポートされたオブジェクトからアニメーションデータを確認
    animation_end_frame = 1

    for obj in bpy.context.scene.objects:
        if obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action
            if action.frame_range[1] > animation_end_frame:
                animation_end_frame = int(action.frame_range[1])

    # アニメーションが見つからない場合は、シーン全体の範囲を確認
    if animation_end_frame == 1:
        # シーンのフレーム範囲から推定
        scene_frame_end = scene.frame_end
        if scene_frame_end > 1:
            animation_end_frame = scene_frame_end
        else:
            # デフォルトとして短めの範囲を設定
            animation_end_frame = 30

    print(f"アニメーション長: {animation_end_frame} フレーム")

    # フレーム範囲を設定
    scene.frame_start = 1
    scene.frame_end = animation_end_frame

    # レンダリングを実行
    print(f"レンダリング開始: {fbx_path}")
    bpy.ops.render.render(animation=True)
    print(f"レンダリング完了: {output_path}")


if __name__ == "__main__":
    # FBXファイルが保存されているフォルダのパス
    fbx_folder = "./animations/"
    # MP4ファイルの出力先フォルダのパス
    output_folder = "./output_videos/"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # フォルダ内のFBXファイルをリストアップ
    fbx_files = [f for f in os.listdir(fbx_folder) if f.endswith(".fbx")]

    for fbx_file in fbx_files:
        full_path = os.path.join(fbx_folder, fbx_file)
        render_fbx_to_mp4(full_path, output_folder)
