import os
import cv2
from PIL import Image
from moviepy.editor import *
import tempfile

def get_video_filename_base(vf):
    """Returns filename and base filename"""
    return vf, os.path.splitext(os.path.basename(vf))[0]

def get_audio(video_path):
    """Returns the audio track only of a video clip"""
    video_object = VideoFileClip(video_path)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        output_path = tmpfile.name
    video_object.audio.write_audiofile(filename=output_path)
    return output_path

def combine_audio_video(video_path, audio_path, og_path):
    """Combines an audio and a video object together"""
    capture = cv2.VideoCapture(og_path) # Stores OG Video into a Capture Window
    fps = capture.get(cv2.CAP_PROP_FPS) # Extracts FPS of OG Video

    video_path_real = video_path + "/%d.png" # To Get All Frames in Folder

    with tempfile.NamedTemporaryFile(suffix=".mkv", delete=False) as tmpfile:
        combined_video_only_path = tmpfile.name

    with tempfile.NamedTemporaryFile(suffix=".mkv", delete=False) as tmpfile:
        output_path = tmpfile.name

    os.system("ffmpeg -framerate %s -i \"%s\" -codec copy %s" % (str(int(fps)), video_path_real, combined_video_only_path)) # Combining the Frames into a Video
    os.system("ffmpeg -i %s -i \"%s\" -codec copy %s" % (combined_video_only_path, audio_path, output_path)) # Combining the Frames and Audio into a Video
    return output_path

def get_frames(video_path):
    """Returns all frames in the video object"""
    base_filename = get_video_filename_base(video_path)[1]
    video_object = VideoFileClip(video_path)
    directory = tempfile.mkdtemp()
    for index, frame in enumerate(video_object.iter_frames()):
        img = Image.fromarray(frame, 'RGB')
        img.save(f'{directory}/{index}.png')
    return directory
