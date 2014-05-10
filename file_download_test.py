import urllib.request
import shutil

# Download the file from `url` and save it locally under `file_name`:


def download_song():
    url = "http://d1.sharebeast.com:80/d/wnvjpcerwsqy72oi355cmfwexaxwlzm4teyydevvsdqjxpajksbruvaq/qivpukrsi5o7.mp3"
    file_name = "da2.mp3"
    with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
