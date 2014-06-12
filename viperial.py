import os
import time
import re
import urllib.request
import shutil
import datetime
import cmd


MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


GENRES = ['Rap', 'Hip-Hop', 'RB', 'Pop', 'Soul',
          'Fusion', 'Electro', '', 'Grime']


def create_directories(today_year = time.strftime("%Y"),
                       today_month = time.strftime("%B")):
    os.makedirs("{}/{}".format(today_year, today_month))


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
        return datetime.datetime(int(song_date[2]),#year
                                 MONTHS.index(song_date[0]) + 1,#month
                                 int(song_date[1][0:-1]))#day (slicing the ',')


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
        return self.date.year + "/" + self.date.month
    
    def download_song(self):
        with urllib.request.urlopen(self.download_url) as response, open(self.title + ".mp3", 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        #TODO OS shiz

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
        if self.sharebeast_id == None:
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
        if(time_period[1] >= self.date <= time_period[0]):
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
    #wanted_song_list = ([Song(*song) for song in page_song_list
    #                    if song.song_wanted(time_period)])
    for song in page_song_list:
        current_song = Song(*song)
        if current_song.is_song_wanted(time_period):
            wanted_song_list.append(current_song)
    return wanted_song_list


def download_entire_page(wanted_songs_list):
    for song in wanted_songs_list:
        print("    Attempting to download {}.".format(song.title))
        song.get_sharebeast_id()
        song.get_download_url()
        if song.download_url == None:
            print("    This song has been removed from ShareBeast. Sorry!")
        else:
            print("        Starting download...")
            song.download_song()
            print("        Finished download!")     



def main():
    wanted_genres = {'Rap'}
    #test data                   TODO add user input
    begin_date = datetime.datetime(2014, 6, 11)
    end_date = datetime.datetime(2014, 6, 10)
    time_period = (begin_date, end_date)
    
    print("Starting downloads!")
    current_page = 1
    for genre in wanted_genres:
        while True:
            print("    Now on page {}".format(current_page))
            wanted_song_list = crawl_entire_page(time_period,
                                                 genre,
                                                 current_page)
            date_passed = False
            download_entire_page(wanted_song_list)
            if not len(wanted_song_list) == 0:
                if wanted_song_list[-1].date <= time_period[1]:
                    date_passed = True
            else:
                print("No songs on this page match the period")
            current_page = current_page + 1
            if date_passed:
                break
    print("All downloads finished!")
    


main()
