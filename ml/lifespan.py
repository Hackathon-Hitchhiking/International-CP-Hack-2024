import pickle

import torch
import whisper
import imagebind
from loguru import logger
from transformers import GPT2Tokenizer, GPT2LMHeadModel


device = "cuda" if torch.cuda.is_available() else "cpu"

logger.debug("loading wisper")
whisper_model = whisper.load_model("tiny")
whisper_model.eval()
whisper_model.to(device)

logger.debug("loading imagebind")
imagebind_model = imagebind.model.imagebind_huge(True)
imagebind_model.eval()
imagebind_model.to(device)

logger.debug("loading bert")
tokenizer = GPT2Tokenizer.from_pretrained("sberbank-ai/rugpt3large_based_on_gpt2")
model = GPT2LMHeadModel.from_pretrained("sberbank-ai/rugpt3large_based_on_gpt2")
model.to(device)

with open("models/models.pkl", "rb") as f:
    catboost_models = pickle.load(f)
