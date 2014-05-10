import os
import time
import re
import urllib.request
import shutil


MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def create_directories(this_year = time.strftime("%Y"),
                       this_month = time.strftime("%B")):
    os.makedirs("{}/{}".format(this_year, this_month))


def get_song_directory(song_date):
    return str(song_date[0] + song_date[1])


def get_today_date():
    return (time.strftime("%Y"), time.strftime("%b"), time.strftime("%d"))


def before_period(song_date, begin_date = None):
    if begin_date == None:
        return False
    else:
        if int(begin_date[0]) > int(song_date[0]):
            return True
        elif int(begin_date[0]) == int(song_date[0]):
            if MONTHS.index(begin_date[1]) > MONTHS.index(song_date[1]):
                return True
            elif MONTHS.index(begin_date[1]) == MONTHS.index(song_date[1]):
                if int(begin_date[2]) > int(song_date[2]):
                    return True
    return False


def after_period(song_date, end_date = None):
    if end_date == None:
        if int(song_date[0]) <= 2010 and MONTHS.index(song_date[1]) <= 8 and int(song_date[2]) <= 8:
            return True
        else:
            return False    
    else:
        if int(end_date[0]) < int(song_date[0]):
            return True
        elif int(end_date[0]) == int(song_date[0]):
            if MONTHS.index(end_date[1]) < MONTHS.index(song_date[1]):
                return True
            elif MONTHS.index(end_date[1]) == MONTHS.index(song_date[1]):
                if int(end_date[2]) < int(song_date[2]):
                    return True
    return False


def parse_date(song_date):
    if 'ago' in song_date:
        return get_today_date()
    else:
        song_date = song_date.split()
        song_date[1] = song_date[1][0:-1]
        song_date[0] , song_date[1], song_date[2] = song_date[2] , song_date[0], song_date[1]
    return tuple(song_date)


def song_wanted(begin_date, end_date, song_date, genre):
    if genre == "</li>":
        return False
    else:
        song_date = parse_date(song_date)
        if (not before_period(song_date, begin_date)
            and after_period(song_date, end_date)):
            return True
    return False


def get_wanted_songs_information(current_page, begin_date, end_date):
    #                       song_id    title       date         genre
    pattern = r'hot(?:1|2).*?/(\d{5})/(.*?)".*?<i>(.*?)</i>.*?(Hip-Hop|Rap|</li>)'
    list_url = "http://www.viperial.com/tracks/list/"
    wanted_song_list = []
    html_request = urllib.request.urlopen(list_url + str(current_page))
    current_page = current_page + 1
    bytecode = html_request.read()
    htmlstr = bytecode.decode() 
    wanted_song_list = re.findall(pattern, htmlstr)
    wanted_song_list = ([song for song in wanted_song_list if
                         song_wanted(begin_date, end_date, song[2], song[3])])
    return wanted_song_list


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
    #TODO OS shiz


def download_entire_page(wanted_songs_list):
    for song in wanted_songs_list:
        print("    Attempting to download {}.".format(song[1]))
        song_address = get_download_address(get_sharebeast_id(song[0]))
        if song_address == None:
            print("    This song has been removed from ShareBeast. Sorry!")
        else:
            print("        Starting download...".format(song[1]))
            download_song(song_address, song[1], 1)
            print("        Finished download!")     


def main():
    begin_date = None
    end_date = ('2014', 'May', '06')
    current_page = 1
    #TODO add user input
    #while True:
    wanted_songs_list = get_wanted_songs_information(current_page,
                                                     begin_date, end_date)
    current_page = current_page + 1
    if not len(wanted_songs_list) == 0:
        last_song = wanted_songs_list.pop()
        a = after_period(parse_date(last_song[2]), end_date)
        if a:
            #break
            pass
        wanted_songs_list.append(last_song)
    download_entire_page(wanted_songs_list)
    print("All downloads finished")
    

#main()
    
#a = get_wanted_songs_information(2)
