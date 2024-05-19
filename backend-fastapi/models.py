import torch

from transformers import WhisperForConditionalGeneration
from transformers import WhisperFeatureExtractor
from transformers import WhisperTokenizer

from langchain.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, AutoModelForSeq2SeqLM, BitsAndBytesConfig

device = "cuda:0" if torch.cuda.is_available() else "cpu"

# ASR model
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
)

# LLM
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

# Digitization model
from pyannote.audio import Pipeline

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1", use_auth_token="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"
)
from speechbox import ASRDiarizationPipeline

digitization_pipeline = ASRDiarizationPipeline(
    asr_pipeline=asr_pipe, diarization_pipeline=pipeline
)
