import json
import logging
import os
import re
import time

import cv2 as cv
import pytesseract
import youtube_dl
from dotenv import load_dotenv


class ytdlocr:

    _logger: logging.Logger = None
    _log_level = logging.INFO
    _log_filename = f'{__file__}.log'
    _log_format = '%(asctime)-15s [%(name)s][%(levelname)s] : %(message)s'
    _log_to_file = False

    _analyzed_fps: float
    _proxy_url: str
    _public_ip_checker_url: str
    _public_ip_checker_url_protocol: str
    _tesseract_path: str

    def __init__(self):
        if self._log_to_file:
            logging.basicConfig(
                level=self._log_level,
                format=self._log_format,
                filename=self._log_filename
            )
        else:
            logging.basicConfig(
                level=self._log_level,
                format=self._log_format
            )
        self._logger = logging.getLogger(__name__)

        self._logger.info(f"Loading {__package__}")

        load_dotenv()

        if (os.getenv('PUBLIC_IP_CHECKER_URL') is not None):
            self.set_public_ip_checker_url(
                str(os.getenv('PUBLIC_IP_CHECKER_URL'))
            )

        if (os.getenv('PROXY_URL') is not None):
            self.set_proxy_url(str(os.getenv('PROXY_URL')))

        if (os.getenv('TESSERACT_PATH') is not None):
            self.set_tesseract_path(str(os.getenv('TESSERACT_PATH')))

        if (os.getenv('ANALYZED_FPS') is not None):
            self.set_analyzed_fps(float(os.getenv('ANALYZED_FPS')))

    def __del__(self):
        del (self)

    def set_analyzed_fps(self, fps: float):
        if not isinstance(fps, float):
            raise TypeError(f"'fps' must be float, not {type(fps)}")
        self._analyzed_fps = fps
        self._logger.info(f"Analyzed FPS set ({fps})")

    def set_proxy_url(self, url: str):
        if not isinstance(url, str):
            raise TypeError(f"'url' must be string, not {type(url)}")
        if re.search(
            r"(socks5|https?)://.*",
            url
        ):
            self._proxy_url = url
            self._logger.info(f"Proxy URL set ({url})")
        else:
            self._logger.warning(
                "Proxy must be http[s]://IP:PORT or socks6://IP:PORT"
            )

    def set_public_ip_checker_url(self, url: str):
        if not isinstance(url, str):
            raise TypeError(f"'url' must be string, not {type(url)}")
        self._public_ip_checker_url = url
        self._public_ip_checker_url_protocol = re.search(
            r"(https?)://.*",
            url
        ).group(1)
        self._logger.info(f"Public IP checker URL set ({url})")

    def set_tesseract_path(self, path: str):
        if not isinstance(path, str):
            raise TypeError(f"'path' must be string, not {type(path)}")
        self._tesseract_path = path
        self._logger.info(f"Tesseract path set ({path})")

    def get_yt_video_by_id(self, video_id: str):
        if not isinstance(video_id, str):
            raise TypeError(f"'video_id' must be string, not {type(video_id)}")
        opts = {
            "proxy": self._proxy_url,
            "outtmpl": "videos/%(id)s.%(ext)s"
        }
        dl_url = ['https://www.youtube.com/watch?v=' + video_id]
        print(opts)
        print(dl_url)
        try:
            with youtube_dl.YoutubeDL(opts) as ytdl:
                ytdl.download(dl_url)
            self._logger.info(f"Downloaded video to (videos/{video_id}.mp4)")
        except youtube_dl.DownloadError as dle:
            self._logger.error(dle.msg)

    def ocr_video(self, video_id: str):
        if not isinstance(video_id, str):
            raise TypeError(f"'video_id' must be string, not {type(video_id)}")
        self._logger.info(f"Begin OCR (videos/{video_id}.mp4)")
        timer_video_start = time.time()
        all_texts = dict()

        # Open video file
        cap = cv.VideoCapture(cv.samples.findFile(f"videos/{video_id}.mp4"))
        if not cap.isOpened():
            self._logger.error(f"Cannot open 'videos/{video_id}.mp4'")
            return

        # Gather video infos
        v_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        v_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        v_fps = cap.get(cv.CAP_PROP_FPS)
        v_total_frames = cap.get(cv.CAP_PROP_FRAME_COUNT)
        v_duration = v_total_frames / v_fps

        # Display video information
        self._logger.info(f"Video dimensions: {v_width} by {v_height} pixels")
        self._logger.info(f"Video duration: {round(v_duration, 2)} seconds")
        self._logger.info(f"Video FPS: {round(v_fps, 2)} images/seconds")

        # Configure tesseract binary path in pytesseract
        pytesseract.pytesseract.tesseract_cmd = self._tesseract_path

        # Read video file
        self._logger.info("Reading video frames ...")
        while True:
            timer_frame_start = time.time()

            # Get frame
            ret, frame = cap.read()
            if not ret:
                self._logger.warning(
                    "Can't receive frame (stream end?)"
                )
                break

            # Skip frames
            v_frame = cap.get(cv.CAP_PROP_POS_FRAMES)
            if (v_frame % round(v_fps / self._analyzed_fps) != 0):
                continue

            # Display current position in video
            v_percent = int(round(v_frame / v_total_frames, 2) * 100)
            self._logger.debug(f"Video position : {v_percent} %", end="\r")

            # Operations on frame
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            # frame = cv.medianBlur(frame, 5)
            frame = cv.threshold(
                frame,
                0,
                255,
                cv.THRESH_BINARY + cv.THRESH_OTSU
            )[1]

            # Read text on frame
            text = pytesseract.image_to_string(frame).strip()

            # Add text to list of texts
            if text != "":
                all_texts[cap.get(cv.CAP_PROP_POS_MSEC)] = text

            self._logger.debug(
                f"Frame treatment in : {time.time() - timer_frame_start}"
            )

        self._logger.info(
            f"Video treatment in : {time.time() - timer_video_start}"
        )

        # When everything done, release the capture
        cap.release()

        # Write captured texts
        with open(f"videos/{video_id}.json", "w") as output:
            output.write(json.dumps(all_texts, indent=4))

    def prjson(self, j):
        print(json.dumps(j, indent=4))

    def reduceTexts(self, video_id: str):
        if not isinstance(video_id, str):
            raise TypeError(f"'video_id' must be string, not {type(video_id)}")
        with open(f"videos/{video_id}.json", "r") as input:
            file_content = input.read().encode()
        texts = json.loads(file_content)
        for aaa in texts:
            print(texts[aaa])
