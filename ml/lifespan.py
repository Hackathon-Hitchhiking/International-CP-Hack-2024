import torch
import whisper


device = 'cuda' if torch.cuda.is_available() else 'cpu'

whisper_model = whisper.load_model("tiny")
whisper_model.eval()
whisper_model.to(device)
