import yt_dl_ocr


def main():
    video_id = "0oTuH_xY3mw"  # Shorter video
    video_id = "XvoMwz9J6_I"  # Long video
    video_id = "hBjksyVmspY"  # IppSec - Academy intro - 12:48
    video_id = "2LNyAbroZUk"  # IppSec - Devel - 15:25
    video_id = "A4U3xiRWfsU"  # IppSec - Tenten - 14:50
    video_id = "93JnRTF5sQM"  # IppSec - Knife - 12:16

    ydo = yt_dl_ocr.ytdlocr()

    ydo.set_proxy_url("socks5://127.0.0.1:9050")
    ydo.set_public_ip_checker_url("http://wtfismyip.com/text")

    ydo.get_yt_video_by_id(video_id)

    ydo.set_analyzed_fps(0.01)
    ydo.ocr_video(video_id)
    ydo.reduceTexts(video_id)


if __name__ == "__main__":
    main()
