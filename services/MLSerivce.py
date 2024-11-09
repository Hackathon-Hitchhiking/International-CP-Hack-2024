import io
import tempfile

from loguru import logger

from ml.lifespan import whisper_model





class MlService:
    def __init__(self):
        self._whisper_model = whisper_model

    def transcript_video(self, video: bytes) -> str:
        logger.debug("ML - Service - transcribe")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_audio:
            temp_audio.write(video)
            temp_audio_path = temp_audio.name
            result = self._whisper_model.transcribe(temp_audio_path)

            transcribe = result["text"]

        return transcribe
