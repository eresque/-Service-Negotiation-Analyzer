from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import os
import re
import json

from fastapi import FastAPI, UploadFile, File
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from pedalboard.io import AudioFile
from pedalboard import *
import noisereduce as nr
import audio2numpy as a2n

from prompts import PROMPTS, Prompt

import torch

from transformers import WhisperForConditionalGeneration
from transformers import WhisperFeatureExtractor
from transformers import WhisperTokenizer
from transformers import pipeline

from langchain.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, AutoModelForSeq2SeqLM, BitsAndBytesConfig

app = FastAPI()

origins = [
    'http://127.0.0.1:5173',
    'http://127.0.0.1:3000',
    'http://localhost:5173',
    'http://localhost:3000'
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
device = "cuda:0" if torch.cuda.is_available() else "cpu"

asr_model_id = "openai/whisper-large-v3"

feature_extractor = WhisperFeatureExtractor.from_pretrained(asr_model_id)
tokenizer = WhisperTokenizer.from_pretrained(asr_model_id, language="russian", task="transcribe")

model = WhisperForConditionalGeneration.from_pretrained(asr_model_id)
forced_decoder_ids = tokenizer.get_decoder_prompt_ids(language="russian", task="transcribe")

asr_pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    feature_extractor=feature_extractor,
    tokenizer=tokenizer,
    chunk_length_s=30,
    stride_length_s=(4, 2),
    device=device,
    # language='ru'
)

model_id = 'IlyaGusev/saiga_llama3_8b'
quantization_config = BitsAndBytesConfig(load_in_8bit=True,
                                         llm_int8_threshold=200.0)

tokenizer = AutoTokenizer.from_pretrained(model_id, )
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=quantization_config,
    device_map='auto',
)

pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
)

local_llm = HuggingFacePipeline(pipeline=pipeline)


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
        audio_dict = {"name": "",
                      "text": "",
                      "errors": []}
        transcribed_text = asr_pipe(inputs=upload_directory + audio)['text']
        transcribed_text_formated = format_answer(transcribed_text)

        audio_dict["name"], audio_dict["text"] = str(audio), transcribed_text_formated

        for prompt_components in PROMPTS:
            prompt = Prompt(
                llm_instructions=prompt_components["llm_instructions"],
                context=transcribed_text_formated,
                question=prompt_components["question"])
            answer = local_llm(prompt.prompt)[len(prompt.prompt):]

            try:
                error = eval(answer)
                print(transcribed_text_formated)
                print(error, type(error))
                audio_dict['errors'].append(error)
                audio_dict['errors'].append(error)
            except:
                continue
        json_array.append(audio_dict)
    print(json_array)
    clear_upload_directory(upload_directory)
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
