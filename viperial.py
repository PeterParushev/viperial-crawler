import os
import time
import re
import urllib.request
import shutil


def create_directories(this_year = time.strftime("%Y"),
                       this_month = time.strftime("%B")):
    os.makedirs("{}/{}".format(this_year, this_month))


def get_new_songs_information():
    #                       song_id    title       date           genre
    pattern = r'hot(?:1|2).*?/(\d{5})/(.*?)".*?<i>(.*?)</i>.*?(Hip-Hop|Rap|</li>)'
    list_url = "http://www.viperial.com/tracks/list/"
    before_period = True
    after_period = False
    #while before_period and not after_period:
    page_counter = 1
    html_request = urllib.request.urlopen(list_url + str(page_counter))
    bytecode = html_request.read()
    htmlstr = bytecode.decode()
    a = re.findall(pattern, htmlstr)
    a = [song for song in a if not song[3] == "</li>"]
    page_counter = page_counter + 1
    return a



def get_sharebeast_id(song_id):
    pattern = r'="http://www.sharebeast.com/(.*?)" target'
    song_url = "http://www.viperial.com/tracks/view/{}/".format(song_id)
    html_request = urllib.request.urlopen(song_url)
    bytecode = html_request.read()
    htmlstr = bytecode.decode()
    sharebeast_id = re.search(pattern, htmlstr)
    try:
        result_id = sharebeast_id.groups()[0]
    except AttributeError:
        result_id = None
    return result_id


def get_download_address(sharebeast_id):
    if sharebeast_id == None:
        return None
    else:
        pattern = r'mp3player.*?src="(.*?)".*?"audio/mpeg"'
        html_request = urllib.request.urlopen("http://www.sharebeast.com/"
                                              + sharebeast_id)
        bytecode = html_request.read()
        htmlstr = bytecode.decode()
        result = re.findall(pattern, htmlstr)
        return result[0]


def download_song(url, song_name, directory):
    song_name = song_name + '.mp3'
    with urllib.request.urlopen(url) as response, open(song_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)


def main():
    begin_date = ""
    end_date = ""
    wanted_songs_list = get_new_songs_information()
    for song in wanted_songs_list:
        print("Attempting to dowload {}.".format(song[1]))
        song_address = get_download_address(get_sharebeast_id(song[0]))
        if song_address == None:
            print("This song has been removed from ShareBeast. Sorry!")
        else:
            print("Starting download...".format(song[1]))
            download_song(song_address, song[1], 1)
            print("Finished download!")     
    print("Finished all downloads!")

#main()
    
a = get_new_songs_information()
a
