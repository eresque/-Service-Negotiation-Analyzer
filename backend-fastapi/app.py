import os
import re

from typing import List

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from pedalboard import *
import noisereduce as nr
import audio2numpy as a2n
from pedalboard.io import AudioFile

from langfuse import Langfuse

from prompts import PROMPTS, Prompt
from models import asr_pipe, local_llm, digitization_pipeline

langfuse = Langfuse(
    secret_key="sk-lf-8b25f1cf-eb14-4676-85aa-ad163b91582c",
    public_key="pk-lf-dfb47137-da23-46fd-a273-e99deb59fb32",
    host="http://localhost:3000"
)

app = FastAPI()

origins = [
    'http://127.0.0.1:5138',
    'http://127.0.0.1:3000',
    'http://localhost:5138',
    'http://localhost:3000'
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

use_digitisation = False


def langfuse_tracing(prompt, answer, span):
    span.generation(
        name="generation",
        input={'question': prompt.question, 'contexts': prompt.context},
        output={'answer': answer}
    )


def get_audio_sample(path):
    x, sr = a2n.audio_from_file(path)

    return dict({
        'path': path,
        'array': x,
        'sampling_rate': sr
    })


def delete_noise(upload_directory):
    audio_files = [file for file in os.listdir(upload_directory) if file.endswith(".mp3")]

    for audio_name in audio_files:
        x, sr = a2n.audio_from_file(upload_directory + audio_name)
        with AudioFile(upload_directory + audio_name).resampled_to(sr) as f:
            audio = f.read(f.frames)

        reduced_noise = nr.reduce_noise(y=audio, sr=sr, stationary=True, prop_decrease=1.0)

        board = Pedalboard([
            NoiseGate(threshold_db=-30, ratio=3, release_ms=250),
            Compressor(threshold_db=-16, ratio=2.5),
            LowShelfFilter(cutoff_frequency_hz=700, gain_db=10, q=1),
            Gain(gain_db=10)
        ])

        effected = board(reduced_noise, sr)

        with AudioFile(upload_directory + audio_name, 'w', sr,
                       effected.shape[0]) as f:
            f.write(effected)


def clear_upload_directory(upload_directory):
    audio_files = [file for file in os.listdir(upload_directory) if file.endswith(".mp3")]

    for audio in audio_files:
        file_path = upload_directory + audio
        os.remove(file_path)


def format_answer(answer):
    pattern = re.compile(r'thank you', re.IGNORECASE)
    replaced_text = re.sub(pattern, 'Верно', answer)

    english_word_pattern = re.compile(r'\b[a-zA-Z]+\b')
    cleaned_text = re.sub(english_word_pattern, '', replaced_text)

    return cleaned_text


def transcribe_audio(upload_directory):
    json_array = []
    delete_noise(upload_directory)

    audio_files = [file for file in os.listdir(upload_directory) if file.endswith(".mp3")]

    for audio in audio_files:
        trace = langfuse.trace(name=audio)
        span = trace.span(
            name="Span",
        )

        audio_dict = {"name": "",
                      "text": "",
                      "errors": []}

        sample = get_audio_sample(upload_directory + audio) if use_digitisation else ""
        diarized_text = digitization_pipeline(sample) if use_digitisation else ""

        transcribed_text = asr_pipe(inputs=upload_directory + audio)['text']
        transcribed_text_formated = format_answer(transcribed_text)

        audio_dict["name"], audio_dict["text"] = str(audio), transcribed_text_formated
        print(transcribed_text_formated)

        for prompt_components in PROMPTS:
            prompt = Prompt(
                error_name=prompt_components["error_name"],
                llm_instructions=prompt_components["llm_instructions"],
                context=transcribed_text_formated,
                question=prompt_components["question"])
            answer = local_llm(prompt.prompt)[len(prompt.prompt):]

            langfuse_tracing(prompt, answer, span)

            if "correct" in answer:
                continue
            audio_dict["errors"].append({"name_error": prompt_components["error_name"],
                                         "text_error": answer})

        json_array.append(audio_dict)
    clear_upload_directory(upload_directory)
    langfuse.flush()
    return json_array


@app.post('/upload/')
async def create_upload_file(file_uploads: List[UploadFile] = File(...)):
    upload_directory = "uploaded_files"
    for file_upload in file_uploads:
        data = file_upload.file.read()
        save_to = "uploaded_files/" + file_upload.filename
        with open(save_to, 'wb') as f:
            f.write(data)

    return transcribe_audio("uploaded_files/")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
