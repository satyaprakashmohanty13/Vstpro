import numpy
from PIL import Image

def analyse(file):
    block_size = 100
    img = Image.open(file)
    (width, height) = img.size
    converted_data = img.convert("RGBA").getdata()

    lsb_r = []
    lsb_g = []
    lsb_b = []
    for height_for in range(height):
        for width_for in range(width):
            (r, g, b, a) = converted_data.getpixel((width_for, height_for))
            lsb_r.append(r & 1)
            lsb_g.append(g & 1)
            lsb_b.append(b & 1)

    lsb_r_avg = []
    lsb_g_avg = []
    lsb_b_avg = []
    for i in range(0, len(lsb_r), block_size):
        lsb_r_avg.append(numpy.mean(lsb_r[i:i + block_size]))
        lsb_g_avg.append(numpy.mean(lsb_g[i:i + block_size]))
        lsb_b_avg.append(numpy.mean(lsb_b[i:i + block_size]))

    detection = 0
    for i in range(0, 3):
        if lsb_b_avg[i] >= 0.50 and lsb_b_avg[i] < 0.52:
            detection = 1

    return detection

def analyze_frames(num_frames, file_type, file_location):
    steg_frames = []
    current = 0
    while current != num_frames:
        try:
            detection = analyse(f"{file_location}/{current}.{file_type}")
            if detection == 1:
                steg_frames.append(current)
            current += 1
        except Exception as e:
            print(e)
            break

    if not steg_frames:
        return "No Steganography Detected in the Frames Provided!"
    else:
        return f"Steganography Detected in Frame: {steg_frames}"
