import subprocess
import tempfile

import librosa
import torch
from catboost import Pool
from imagebind.model import ModalityType
from imagebind.utils import data
from loguru import logger

from ml.lifespan import whisper_model, device, imagebind_model, catboost_models
from ml.constants import LABEL_NAMES, EMBEDDING_FEATURES


class MlService:
    def __init__(self):
        self._whisper_model = whisper_model
        self._imagebind_model = imagebind_model

        self._catboost_models = catboost_models
        self._label_names = LABEL_NAMES
        self._embedding_features = EMBEDDING_FEATURES

        self.device = device

    def transcript_video(self, video: bytes) -> str:
        """
        Расшифровывает видео и возвращает текстовую транскрипцию.

        Параметры
        ----------
        video : bytes
            Видео в формате байтов, представляющее содержимое видеофайла для расшифровки.

        Возвращает
        -------
        str
            Текстовая транскрипция содержимого видео.

        Примечания
        ---------
        - Функция сохраняет видео во временный файл формата MP4 для передачи его
          в модель распознавания речи.
        - Используется предварительно обученная модель для транскрипции.
        - После обработки временный файл сохраняется, но может быть удалён после использования.
        """
        logger.debug("ML - Service - transcribe")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_audio:
            temp_audio.write(video)
            temp_audio_path = temp_audio.name
            result = self._whisper_model.transcribe(temp_audio_path)

            transcribe = result["text"]

        return transcribe

    def get_ocean(self, video: bytes, transcript: str) -> dict[str, float]:
        answer = {}

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_audio:
            temp_audio.write(video)

            audio_embedding = self._extract_audio_embedding(temp_audio)

        text_embedding = self._extract_text_embedding(transcript)

        x = {
            "audio_embedding": audio_embedding,
            "text_embedding": text_embedding,
        }

        for label_name in self._label_names:
            model = self._catboost_models[label_name]

            sample_pool = Pool(
                data=x,
                embedding_features=self._embedding_features
            )

            y_pred = model.predict(sample_pool)[0]

            answer[label_name] = y_pred

        return answer

    def _extract_audio_embedding(self, video_path):
        """
        Извлекает аудиовектор из видео.

        Параметры
        ----------
        video_path : str
            Путь к видеофайлу, из которого необходимо извлечь аудиодорожку.

        Возвращаемое значение
        ----------------------
        tuple
            Кортеж, содержащий:
            - audio : numpy.ndarray
                Массив, представляющий аудиоданные, загруженные из временного файла.
            - sr : int
                Частота дискретизации аудиоданных.
            - audio_embeddings : torch.Tensor
                Векторное представление аудиоданных, извлеченное моделью ImageBind.

        Описание
        ---------
        Данная функция использует библиотеку ffmpeg для извлечения аудиодорожки из
        видеофайла и сохранения её во временном WAV-файле. Затем с помощью библиотеки
        librosa аудиоданные загружаются и преобразуются в массив. После этого аудиоданные
        обрабатываются моделью ImageBind, чтобы получить векторное представление аудио.
        Функция возвращает массив аудиоданных, частоту дискретизации и среднее значение
        векторных представлений аудио.

        Исключения
        ----------
        - subprocess.CalledProcessError
            Генерируется, если выполнение команды ffmpeg завершилось с ошибкой.
        - FileNotFoundError
            Генерируется, если ffmpeg или необходимые библиотеки не установлены.
        """
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as temp_audio_file:
            temp_audio_path = temp_audio_file.name
            subprocess.run(
                ["ffmpeg", "-y", "-i", video_path, temp_audio_path, "-loglevel", "error"],
                check=True
            )
            audio, sr = librosa.load(temp_audio_path, sr=None)

            inputs = {ModalityType.AUDIO: data.load_and_transform_audio_data([temp_audio_path], self.device)}
            with torch.inference_mode():
                audio_embeddings = self._imagebind_model(inputs)[ModalityType.AUDIO].mean(dim=0)

            return audio, sr, audio_embeddings

    def _extract_text_embedding(self, text):
        """
        Извлекает эмбеддинг для текста.

        Параметры
        ----------
        text : str
            Входной текст для извлечения эмбеддинга. Если строка пустая или не является строкой,
            будет использовано значение по умолчанию "<UNK>".

        Возвращает
        -------
        torch.Tensor
            Эмбеддинг текста, полученный с помощью модели ImageBind.

        Примечания
        ---------
        Функция использует метод `load_and_transform_text` для предварительной обработки текста,
        приводя его в формат, подходящий для обработки моделью. Затем эмбеддинг извлекается
        в режиме inference, что позволяет выполнять вычисления без сохранения промежуточных
        данных для обучения.

        Исключения
        ---------
        Проверка типа входных данных выполняется с целью обеспечения безопасности и предотвращения
        ошибок при передаче некорректного формата. Если переданный текст не соответствует
        ожидаемому типу, используется placeholder "<UNK>".
        """
        if not isinstance(text, str) or not text:
            text = "<UNK>"
        inputs = {ModalityType.TEXT: data.load_and_transform_text([text], self.device)}
        with torch.inference_mode():
            text_embedding = self._imagebind_model(inputs)[ModalityType.TEXT]
        return text_embedding