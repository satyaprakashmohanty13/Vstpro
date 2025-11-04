import streamlit as st
from video_utils import get_audio, get_frames, combine_audio_video
from audio_steg import hide_data, recover_data
from frame_steg import encode_frames, decode_frames
from analysis_utils import analyze_frames
import os
import tempfile
import zipfile
import shutil

# Helper function to unzip frames
def unzip_frames(zip_path):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    return temp_dir

# ---------------- Sidebar Navigation ----------------
st.sidebar.title("🔐 Steganography Toolkit")
page = st.sidebar.radio(
    "Select Tool",
    [
        "🎞️ Video Splitter & Combiner",
        "🎵 Hide Data in Audio",
        "📤 Recover Data from Audio",
        "🖼️ Hide Data in Frames",
        "📥 Recover Data from Frames",
        "🔍 Detect Steganography in Images",
    ],
)

st.title(page)

# ---------------- Page 1: Video Splitter and Combiner ----------------
if page == "🎞️ Video Splitter & Combiner":
    st.header("Extract or Combine Video Components")
    tab1, tab2, tab3 = st.tabs(["Get Audio", "Get Frames", "Combine Audio & Frames"])

    with tab1:
        video_file = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"])
        if st.button("Extract Audio") and video_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(video_file.read())
                audio_path = get_audio(tmp.name)
                st.audio(audio_path)

    with tab2:
        video_file2 = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"], key="frames")
        if st.button("Extract Frames") and video_file2:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(video_file2.read())
                frames_dir = get_frames(tmp.name)
                zip_path = shutil.make_archive(frames_dir, "zip", frames_dir)
                with open(zip_path, "rb") as f:
                    st.download_button("Download Frames (Zip)", f, file_name="frames.zip")

    with tab3:
        frames_zip = st.file_uploader("Upload Frames (Zip)", type=["zip"])
        audio_file = st.file_uploader("Upload Audio", type=["wav", "mp3"])
        og_video = st.file_uploader("Upload Original Video (for FPS)", type=["mp4", "mov"])
        if st.button("Combine"):
            if frames_zip and audio_file and og_video:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as fz, \
                     tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as fa, \
                     tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as fv:
                    fz.write(frames_zip.read())
                    fa.write(audio_file.read())
                    fv.write(og_video.read())
                    frames_dir = unzip_frames(fz.name)
                    video_out = combine_audio_video(frames_dir, fa.name, fv.name)
                    st.video(video_out)

# ---------------- Page 2: Hide Data in Audio ----------------
elif page == "🎵 Hide Data in Audio":
    st.header("Hide File in Audio")
    sound = st.file_uploader("Upload Audio", type=["wav", "mp3"])
    secret_file = st.file_uploader("Upload File to Hide")
    num_lsb = st.slider("Number of LSBs", 1, 8, 2)

    if st.button("Hide Data"):
        if sound and secret_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as sa, \
                 tempfile.NamedTemporaryFile(delete=False) as sf:
                sa.write(sound.read())
                sf.write(secret_file.read())
                output_audio, info = hide_data(sa.name, sf.name, num_lsb)
                st.audio(output_audio)
                st.info(info)

# ---------------- Page 3: Recover Data from Audio ----------------
elif page == "📤 Recover Data from Audio":
    st.header("Recover Hidden File from Audio")
    audio_in = st.file_uploader("Upload Stego Audio", type=["wav", "mp3"])
    num_lsb = st.slider("Number of LSBs", 1, 8, 2)
    bytes_to_recover = st.number_input("Bytes to Recover", min_value=1, step=1)

    if st.button("Recover Data"):
        if audio_in:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as fa:
                fa.write(audio_in.read())
                recovered = recover_data(fa.name, num_lsb, int(bytes_to_recover))
                with open(recovered, "rb") as f:
                    st.download_button("Download Recovered File", f, file_name="recovered.txt")

# ---------------- Page 4: Hide Data in Frames ----------------
elif page == "🖼️ Hide Data in Frames":
    st.header("Hide File in Frames")
    start_frame = st.number_input("Start Frame", min_value=0, step=1)
    end_frame = st.number_input("End Frame", min_value=1, step=1)
    frames_zip = st.file_uploader("Upload Frames (Zip)", type=["zip"])
    file_to_hide = st.file_uploader("File to Hide")

    if st.button("Hide Data in Frames"):
        if frames_zip and file_to_hide:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as fz, \
                 tempfile.NamedTemporaryFile(delete=False) as ff:
                fz.write(frames_zip.read())
                ff.write(file_to_hide.read())
                frames_dir = unzip_frames(fz.name)
                out_zip = encode_frames(int(start_frame), int(end_frame), ff.name, frames_dir)
                with open(out_zip, "rb") as f:
                    st.download_button("Download Encoded Frames (Zip)", f, file_name="encoded_frames.zip")

# ---------------- Page 5: Recover Data from Frames ----------------
elif page == "📥 Recover Data from Frames":
    st.header("Recover File from Frames")
    start_frame = st.number_input("Start Frame", min_value=0, step=1)
    end_frame = st.number_input("End Frame", min_value=1, step=1)
    frames_zip = st.file_uploader("Upload Encoded Frames (Zip)", type=["zip"])

    if st.button("Recover Data from Frames"):
        if frames_zip:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as fz:
                fz.write(frames_zip.read())
                frames_dir = unzip_frames(fz.name)
                recovered_file = decode_frames(int(start_frame), int(end_frame), frames_dir)
                with open(recovered_file, "rb") as f:
                    st.download_button("Download Recovered File", f, file_name="recovered.txt")

# ---------------- Page 6: Detect Steganography ----------------
elif page == "🔍 Detect Steganography in Images":
    st.header("Steganography Detection")
    num_frames = st.number_input("Number of Frames to Analyze", min_value=1, step=1)
    file_type = st.text_input("File Type (e.g. png, jpg)", value="png")
    frames_zip = st.file_uploader("Upload Frames (Zip)", type=["zip"])

    if st.button("Detect"):
        if frames_zip:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as fz:
                fz.write(frames_zip.read())
                frames_dir = unzip_frames(fz.name)
                result = analyze_frames(int(num_frames), file_type, frames_dir)
                st.text_area("Detection Result", result)
