# YT download and OCR

`yt-dl-ocr` is a tool to collect text strings that appears in YT videos.

First aim of this project is to help me learn linux commands by gathering the command lines used in a specific video on YT.

You can use it to extract all kind of texts by modifying the code (the reduceTexts method). My code may focus on other interests.

The process is (globally) as follow:
- Download specific video from its ID
- Extract characters using OCR

*Warning: Running OCR on each frame of a video is a long process*

fdsf


## Requirements
---

- [Ubuntu Linux 20.04 (Focal Fossa)](https://releases.ubuntu.com/20.04/)
  - [Poetry](https://python-poetry.org/)
  - [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract)
  - [Tor proxy](https://linuxconfig.org/install-tor-proxy-on-ubuntu-20-04-linux)
  - [Python 3.8+](https://www.python.org/)
    - [OpenCV](https://pypi.org/project/opencv-python-headless/)
    - [Pytesseract](https://pypi.org/project/pytesseract/)
    - [Youtube DL](https://pypi.org/project/youtube_dl/)

## Installation
---

Install system binaries
```shell
curl -sSL https://install.python-poetry.org | python3 -
sudo apt-get install tesseract-ocr
sudo apt-get install tor
```

Generate Tor hashed password
```shell
tor --hash-password YOUR_PASSWORD
```

Insert password in /etc/tor/torrc
```shell
SOCKSPort 9050
HashedControlPassword HASHED_PASSWORD
CookieAuthentication 1
```

Restart Tor service
```shell
sudo systemctl restart tor
```

Check Tor proxy listening port
```shell
ss -tulpn | grep 9050
```

Clone repository
```shell
git clone https://github.com/theh2oweb/yt-dl-ocr.git
cd yt-dl-ocr/
```

Create environment file or rename the sample to .env
```shell
cat <<EOF >.env
ANALYZED_FPS=0.1
PROXY_URL=socks5://127.0.0.1:9050
PUBLIC_IP_CHECKER_URL=http://ifconfig.me/ip
TESSERACT_PATH=/usr/bin/tesseract
EOF
```

Install python dependencies
```shell
poetry install
```

Run demo
```shell
poetry shell
python ./demo.py
```

# Notes
- Character recognition is not optimized (weird characters may appear)
- Video may contain fading transition mixing two different screens
- 