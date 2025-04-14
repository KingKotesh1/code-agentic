from pydub import AudioSegment
import io

def convert_opus_to_wav(file_bytes):
    audio = AudioSegment.from_file(io.BytesIO(file_bytes), format="opus")
    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)
    return wav_io
