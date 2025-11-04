import os, math, struct, wave
import tempfile

def prepare(sound_path, num_lsb):
    sound = wave.open(sound_path, "r")

    params = sound.getparams()
    num_channels = sound.getnchannels()
    sample_width = sound.getsampwidth()
    n_frames = sound.getnframes()
    n_samples = n_frames * num_channels

    if (sample_width == 1):
        fmt = "{}B".format(n_samples)
        mask = (1 << 8) - (1 << num_lsb)
        smallest_byte = -(1 << 8)
    elif (sample_width == 2):
        fmt = "{}h".format(n_samples)
        mask = (1 << 15) - (1 << num_lsb)
        smallest_byte = -(1 << 15)
    else:
        raise ValueError("File has an unsupported bit-depth")

    return sound, params, n_frames, n_samples, fmt, mask, smallest_byte

def hide_data(sound_path, file_path, num_lsb):
    sound, params, n_frames, n_samples, fmt, mask, smallest_byte = prepare(sound_path, num_lsb)
    max_bytes_to_hide = (n_samples * num_lsb) // 8
    filesize = os.stat(file_path).st_size

    if (filesize > max_bytes_to_hide):
        required_LSBs = math.ceil(filesize * 8 / n_samples)
        raise ValueError("Input file too large to hide, "
                         "requires {} LSBs, using {}"
                         .format(required_LSBs, num_lsb))

    raw_data = list(struct.unpack(fmt, sound.readframes(n_frames)))
    sound.close()

    input_data = memoryview(open(file_path, "rb").read())

    data_index = 0
    sound_index = 0

    values = []
    buffer = 0
    buffer_length = 0
    done = False

    while(not done):
        while (buffer_length < num_lsb and data_index // 8 < len(input_data)):
            buffer += (input_data[data_index // 8] >> (data_index % 8)
                        ) << buffer_length
            bits_added = 8 - (data_index % 8)
            buffer_length += bits_added
            data_index += bits_added

        current_data = buffer % (1 << num_lsb)
        buffer >>= num_lsb
        buffer_length -= num_lsb

        while (sound_index < len(raw_data) and
               raw_data[sound_index] == smallest_byte):
            values.append(struct.pack(fmt[-1], raw_data[sound_index]))
            sound_index += 1

        if (sound_index < len(raw_data)):
            current_sample = raw_data[sound_index]
            sound_index += 1

            sign = 1
            if (current_sample < 0):
                current_sample = -current_sample
                sign = -1

            altered_sample = sign * ((current_sample & mask) | current_data)

            values.append(struct.pack(fmt[-1], altered_sample))

        if (data_index // 8 >= len(input_data) and buffer_length <= 0):
            done = True

    while(sound_index < len(raw_data)):
        values.append(struct.pack(fmt[-1], raw_data[sound_index]))
        sound_index += 1

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        output_path = tmpfile.name

    sound_steg = wave.open(output_path, "w")
    sound_steg.setparams(params)
    sound_steg.writeframes(b"".join(values))
    sound_steg.close()
    return output_path, "Using {} B out of {} B".format(filesize, max_bytes_to_hide)

def recover_data(sound_path, num_lsb, bytes_to_recover):
    sound, params, n_frames, n_samples, fmt, smallest_byte = prepare(sound_path, num_lsb)

    raw_data = list(struct.unpack(fmt, sound.readframes(n_frames)))
    mask = (1 << num_lsb) - 1

    data = bytearray()
    sound_index = 0
    buffer = 0
    buffer_length = 0
    sound.close()

    while (bytes_to_recover > 0):

        next_sample = raw_data[sound_index]
        if (next_sample != smallest_byte):
            buffer += (abs(next_sample) & mask) << buffer_length
            buffer_length += num_lsb
        sound_index += 1

        while (buffer_length >= 8 and bytes_to_recover > 0):
            current_data = buffer % (1 << 8)
            buffer >>= 8
            buffer_length -= 8
            data += struct.pack('1B', current_data)
            bytes_to_recover -= 1

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmpfile:
        output_path = tmpfile.name
        tmpfile.write(bytes(data))
    return output_path
