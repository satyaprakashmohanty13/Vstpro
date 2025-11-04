from PIL import Image
import math
import tempfile
import os

# Convert encoding data into 8-bit binary ASCII
def generateData(data):
    newdata = []
    for i in data:
        newdata.append(format(ord(i), '08b'))
    return newdata

# Pixels modified according to encoding data in generateData
def modifyPixel(pixel, data):
    datalist = generateData(data)
    lengthofdata = len(datalist)
    imagedata = iter(pixel)
    for i in range(lengthofdata):
        pixel = [value for value in imagedata.__next__()[:3] + imagedata.__next__()[:3] + imagedata.__next__()[:3]]
        for j in range(0, 8):
            if (datalist[i][j] == '0' and pixel[j]% 2 != 0):
                pixel[j] -= 1
            elif (datalist[i][j] == '1' and pixel[j] % 2 == 0):
                if(pixel[j] != 0):
                    pixel[j] -= 1
                else:
                    pixel[j] += 1
        if (i == lengthofdata - 1):
            if (pixel[-1] % 2 == 0):
                if(pixel[-1] != 0):
                    pixel[-1] -= 1
                else:
                    pixel[-1] += 1
        else:
            if (pixel[-1] % 2 != 0):
                pixel[-1] -= 1
        pixel = tuple(pixel)
        yield pixel[0:3]
        yield pixel[3:6]
        yield pixel[6:9]

def encoder(newimage, data):
    w = newimage.size[0]
    (x, y) = (0, 0)
    for pixel in modifyPixel(newimage.getdata(), data):
        newimage.putpixel((x, y), pixel)
        if (x == w - 1):
            x = 0
            y += 1
        else:
            x += 1

def encode_frames(start, end, filename, frame_loc):
    total_frame = end - start + 1
    with open(filename) as fileinput:
        filedata = fileinput.read()

    datapoints = math.ceil(len(filedata) / total_frame)
    counter = start
    output_dir = tempfile.mkdtemp()
    for convnum in range(0, len(filedata), datapoints):
        numbering = frame_loc + "/" + str(counter) + ".png"
        encodetext = filedata[convnum:convnum+datapoints]
        image = Image.open(numbering, 'r')
        newimage = image.copy()
        encoder(newimage, encodetext)
        new_img_name = f"{output_dir}/{counter}.png"
        newimage.save(new_img_name, str(new_img_name.split(".")[1].upper()))
        counter += 1

    zip_path = f"{output_dir}.zip"
    os.system(f"zip -r {zip_path} {output_dir}")
    return zip_path


def decode_frames(start, end, frame_loc):
    decoded_data = ""
    for i in range(start, end + 1):
        numbering = frame_loc + "/" + str(i) + ".png"
        image = Image.open(numbering, 'r')
        data = ''
        imgdata = iter(image.getdata())
        while (True):
            pixels = [value for value in imgdata.__next__()[:3] + imgdata.__next__()[:3] + imgdata.__next__()[:3]]
            binstr = ''
            for i in pixels[:8]:
                if (i % 2 == 0):
                    binstr += '0'
                else:
                    binstr += '1'
            data += chr(int(binstr, 2))
            if (pixels[-1] % 2 != 0):
                decoded_data += data
                break
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as tmpfile:
        output_path = tmpfile.name
        tmpfile.write(decoded_data)
    return output_path
