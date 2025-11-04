import gradio as gr
from video_utils import get_audio, get_frames, combine_audio_video
from audio_steg import hide_data, recover_data
from frame_steg import encode_frames, decode_frames
from analysis_utils import analyze_frames
import os
import tempfile
import zipfile

def unzip_frames(zip_path):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    return temp_dir

def split_and_combine_ui():
    with gr.Blocks() as interface:
        gr.Markdown("## Video Tools")
        with gr.Tabs():
            with gr.TabItem("Get Audio"):
                with gr.Row():
                    video_input = gr.Video(label="Input Video")
                    output_audio = gr.Audio(label="Extracted Audio")
                get_audio_btn = gr.Button("Get Audio")
                get_audio_btn.click(get_audio, inputs=video_input, outputs=output_audio)

            with gr.TabItem("Get Frames"):
                with gr.Row():
                    video_input_frames = gr.Video(label="Input Video")
                    output_frames = gr.File(label="Extracted Frames (Zip)")
                get_frames_btn = gr.Button("Get Frames")
                def get_frames_wrapper(video_path):
                    frames_dir = get_frames(video_path)
                    zip_path = f"{frames_dir}.zip"
                    os.system(f"zip -r {zip_path} {frames_dir}")
                    return zip_path
                get_frames_btn.click(get_frames_wrapper, inputs=video_input_frames, outputs=output_frames)


            with gr.TabItem("Combine Audio and Video"):
                with gr.Row():
                    frames_input = gr.File(label="Frames (Zip)")
                    audio_input = gr.Audio(label="Input Audio")
                    og_video_input = gr.Video(label="Original Video (for FPS)")
                    output_video = gr.Video(label="Combined Video")
                combine_btn = gr.Button("Combine")
                def combine_wrapper(frames_zip, audio_path, og_video_path):
                    frames_dir = unzip_frames(frames_zip.name)
                    return combine_audio_video(frames_dir, audio_path, og_video_path)
                combine_btn.click(combine_wrapper, inputs=[frames_input, audio_input, og_video_input], outputs=output_video)

    return interface

def hide_audio_ui():
    with gr.Blocks() as interface:
        gr.Markdown("## Hide Data in Audio")
        with gr.Row():
            sound_input = gr.Audio(label="Input Audio")
            file_input = gr.File(label="Text File to Hide")
            num_lsb = gr.Slider(1, 8, value=2, step=1, label="Number of LSBs")
        with gr.Row():
            output_audio = gr.Audio(label="Output Audio")
            info_output = gr.Textbox(label="Info")
        hide_btn = gr.Button("Hide Data")
        hide_btn.click(hide_data, inputs=[sound_input, file_input, num_lsb], outputs=[output_audio, info_output])
    return interface

def recover_audio_ui():
    with gr.Blocks() as interface:
        gr.Markdown("## Recover Data from Audio")
        with gr.Row():
            audio_input = gr.Audio(label="Input Audio")
            num_lsb = gr.Slider(1, 8, value=2, step=1, label="Number of LSBs")
            bytes_to_recover = gr.Number(label="Number of Bytes to Recover")
        with gr.Row():
            output_file = gr.File(label="Recovered Text File")
        recover_btn = gr.Button("Recover Data")
        def recover_data_wrapper(audio_path, num_lsb, bytes_to_recover):
            return recover_data(audio_path, int(num_lsb), int(bytes_to_recover))
        recover_btn.click(recover_data_wrapper, inputs=[audio_input, num_lsb, bytes_to_recover], outputs=output_file)
    return interface

def hide_frames_ui():
    with gr.Blocks() as interface:
        gr.Markdown("## Hide Data in Frames")
        with gr.Row():
            start_frame = gr.Number(label="Start Frame")
            end_frame = gr.Number(label="End Frame")
            frames_zip = gr.File(label="Frames (Zip)")
            file_to_hide = gr.File(label="File to Hide")
        with gr.Row():
            output_file = gr.File(label="Encoded Frames (Zip)")
        hide_btn = gr.Button("Hide Data")
        def hide_frames_wrapper(start, end, frames_zip, file_to_hide):
            frames_dir = unzip_frames(frames_zip.name)
            return encode_frames(int(start), int(end), file_to_hide.name, frames_dir)
        hide_btn.click(hide_frames_wrapper, inputs=[start_frame, end_frame, frames_zip, file_to_hide], outputs=output_file)

    return interface

def recover_frames_ui():
    with gr.Blocks() as interface:
        gr.Markdown("## Recover Data from Frames")
        with gr.Row():
            start_frame = gr.Number(label="Start Frame")
            end_frame = gr.Number(label="End Frame")
            frames_zip = gr.File(label="Frames (Zip)")
        with gr.Row():
            output_file = gr.File(label="Recovered Text File")
        recover_btn = gr.Button("Recover Data")
        def recover_frames_wrapper(start, end, frames_zip):
            frames_dir = unzip_frames(frames_zip.name)
            return decode_frames(int(start), int(end), frames_dir)
        recover_btn.click(recover_frames_wrapper, inputs=[start_frame, end_frame, frames_zip], outputs=output_file)
    return interface

def detect_steganography_ui():
    with gr.Blocks() as interface:
        gr.Markdown("## Steganography Detection in Images")
        with gr.Row():
            num_frames = gr.Number(label="Number of Frames")
            file_type = gr.Textbox(label="File Type (e.g. png)", value="png")
            frames_zip = gr.File(label="Frames (Zip)")
        with gr.Row():
            output_text = gr.Textbox(label="Detection Result")
        detect_btn = gr.Button("Detect Steganography")
        def detect_wrapper(num_frames, file_type, frames_zip):
            frames_dir = unzip_frames(frames_zip.name)
            return analyze_frames(int(num_frames), file_type, frames_dir)
        detect_btn.click(detect_wrapper, inputs=[num_frames, file_type, frames_zip], outputs=output_text)
    return interface

with gr.Blocks() as demo:
    gr.TabbedInterface(
        [
            split_and_combine_ui(),
            hide_audio_ui(),
            recover_audio_ui(),
            hide_frames_ui(),
            recover_frames_ui(),
            detect_steganography_ui(),
        ],
        [
            "Video Splitter and Combiner",
            "Hide Data in Audio",
            "Recover Data in Audio",
            "Hide Data in Frames",
            "Recover Data in Frames",
            "Steganography Detection in Images",
        ],
    )

if __name__ == "__main__":
    if not os.path.exists('output'):
        os.makedirs('output')
    demo.launch(share=False)
