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

import audio2numpy as a2n

from prompts import PROMPTS, Prompt

import torch

from transformers import WhisperForConditionalGeneration
from transformers import WhisperFeatureExtractor
from transformers import WhisperTokenizer
from transformers import pipeline

from langchain.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, AutoModelForSeq2SeqLM, BitsAndBytesConfig

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


def format_answer(answer):
    pattern = re.compile(r'thank you', re.IGNORECASE)
    replaced_text = re.sub(pattern, 'Верно', answer)

    english_word_pattern = re.compile(r'\b[a-zA-Z]+\b')
    cleaned_text = re.sub(english_word_pattern, '', replaced_text)

    return cleaned_text


def transcribe_audio(upload_directory):
    json_array = []
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
            except:
                continue
        json_array.append(audio_dict)
    print(json_array)
    return json_array


app = FastAPI()


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
