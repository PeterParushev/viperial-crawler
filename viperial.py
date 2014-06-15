import os
import time
import re
import urllib.request
import shutil
import datetime
import sys

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


GENRES = ['Rap', 'Hip-Hop', 'RB', 'Pop', 'Soul',
          'Fusion', 'Electro', '', 'Grime']


def parse_date(song_date):
    """
    A helper function to parse the multiple date formats used in the site.
    It could be either already a datetime object, or one of two types of string
    """
    if type(song_date) == tuple:
        return datetime.datetime(song_date[0], song_date[1], song_date[2])
    elif 'ago' in song_date:
        """
        If the song has been uploaded soon, instead of a date it
        has somehing along the lines of "uploaded 2 hours ago".
        """
        return datetime.datetime.now()
    else:
        """
        Otherwise it will be in the format
        "Jun 12, 2014" and has to be parsed
        """
        song_date = song_date.split()
        return datetime.datetime(int(song_date[2]),  #year
                                 MONTHS.index(song_date[0]) + 1,  #month
                                 int(song_date[1][0:-1]))  #day (slicing ',')


class Song:
    def __init__(self, viperial_id, title, date):
        self.title = title
        self.viperial_id = viperial_id
        self.date = parse_date(date)
        self.sharebeast_id = None
        self.download_url = None

    def get_song_directory(self):
        """
        Each song should be saved in a directory
        following the year/month format
        """
        return str(self.date.year) + "/" + MONTHS[self.date.month - 1]

    def download_song(self):
        os.makedirs(self.get_song_directory(), exist_ok=True)
        if not os.path.exists(self.get_song_directory() + '/'
                              + self.title + '.mp3'):

            print("        Starting download...")
            response = urllib.request.urlopen(self.download_url)

            out_file = open(self.get_song_directory() + '/' +
                            self.title + ".mp3", 'wb')

            shutil.copyfileobj(response, out_file)
            print("        Finished download!")
        else:
            print("        This song has already been downloaded")

    def get_sharebeast_id(self):
        pattern = r'="http://www.sharebeast.com/(.*?)" target'
        viperial_song_page = "http://www.viperial.com/tracks/view/{}/".format(
            self.viperial_id)
        html_request = urllib.request.urlopen(viperial_song_page)
        bytecode = html_request.read()
        htmlstr = bytecode.decode()
        sharebeast_id = re.search(pattern, htmlstr)
        try:
            result_id = sharebeast_id.groups()[0]
        except AttributeError:
            result_id = None
        self.sharebeast_id = result_id

    def get_download_url(self):
        if self.sharebeast_id is None:
            self.download_url = None
        else:
            pattern = r'mp3player.*?src="(.*?)".*?"audio/mpeg"'
            html_request = urllib.request.urlopen("http://www.sharebeast.com/"
                                                  + self.sharebeast_id)
            bytecode = html_request.read()
            htmlstr = bytecode.decode()
            result = re.findall(pattern, htmlstr)
            self.download_url = result[0]

    def is_song_wanted(self, time_period):
        song_wanted = False
        if(time_period[0] >= self.date >= time_period[1]):
            song_wanted = True
        return song_wanted


def crawl_entire_page(time_period, genre, current_page):
    #                       song_id    title       date
    pattern = r'hot(?:1|2).*?/(\d{5})/(.*?)".*?<i>(.*?)</i>'
    genre_url = str(GENRES.index(genre)+1) + '-' + genre
    list_url = "http://www.viperial.com/tracks/list/genre/{}/".format(genre_url)
    wanted_song_list = []
    html_request = urllib.request.urlopen(list_url + str(current_page))
    bytecode = html_request.read()
    htmlstr = bytecode.decode()
    page_song_list = re.findall(pattern, htmlstr)
    wanted_song_list = []
    for song in page_song_list:
        current_song = Song(*song)
        if current_song.is_song_wanted(time_period):
            wanted_song_list.append(current_song)
    if (Song(*page_song_list[-1]).date < time_period[1]
        and len(wanted_song_list) == 0):
        return None
    return wanted_song_list


def download_entire_page(wanted_songs_list):
    for song in wanted_songs_list:
        print("    Attempting to download {}.".format(song.title))
        song.get_sharebeast_id()
        song.get_download_url()
        if song.download_url == None:
            print("    This song has been removed from ShareBeast. Sorry!")
        else:
            song.download_song()


def input_genres():
    print("""To select genres, please type the genre id.
To do so type in a number that includes the
genres you want. For example for Rap and Hip-Hop type 12 or 21.
The genres are:
    1-Rap    2-Hip-hop    3-R&B    4-Pop    5-Soul    6-Fusion
             7-Electro    9-Grime    8- for all above""")
    wanted_genres = set()
    genres = input('-->')
    for genre_id in genres:
        genre_id = int(genre_id)
        if not int(genre_id) in range(0, 9):
            print("  Wrong input! You are going ot have to start over. Sorry!")
            return input_genres()

        if genre_id == 8:
            for i in range(0, 7):
                wanted_genres.add(GENRES[i])
            wanted_genres.add(GENRES[8])
        else:
            wanted_genres.add(GENRES[genre_id - 1])
    return wanted_genres


def input_period():
    print("""To select a time period, please type in a
time period in the format DD MM YYYY DD MM YYYY""")
    dates = input('-->')

    try:
        dates = dates.split()
        begin_date = datetime.datetime(int(dates[-1]),
                                       int(dates[-2]),
                                       int(dates[-3]))
        end_date = datetime.datetime(int(dates[-4]),
                                     int(dates[-5]),
                                     int(dates[-6]))
    except:
        print("    Something went wrong, try again!")
        return input_period()
    if(begin_date < end_date):
        begin_date, end_date = end_date, begin_date
    time_period = (begin_date, end_date)
    return time_period


def download_songs():
    wanted_genres = input_genres()
    time_period = input_period()
    print("Starting downloads!")
    for genre in wanted_genres:
        current_page = 1
        while True:
            wanted_song_list = crawl_entire_page(time_period,
                                                 genre,
                                                 current_page)
            if wanted_song_list is not None:
                print("    Now on page {} of {} songs:".format(current_page,
                                                               genre))
                download_entire_page(wanted_song_list)
            else:
                break
            current_page = current_page + 1
    print("All downloads finished!")


def main():
    print("Welcome to the viperial crawler!")
    download_songs()
    print("Bye!")


main()
