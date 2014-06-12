import os
import time
import re
import urllib.request
import shutil
import datetime


MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

GENRES = ['Rap', 'Hip-Hop', 'RB', 'Pop', 'Soul',
          'Fusion', 'Electro', '', 'Grime']


def create_directories(today_year = time.strftime("%Y"),
                       today_month = time.strftime("%B")):
    os.makedirs("{}/{}".format(today_year, today_month))


class Date:
    def __init__(self, song_date):
        if type(song_date) == tuple:
            self.year = song_date[0]
            self.month = song_date[1]
            self.day = song_date[2]

        elif 'ago' in song_date:
            """
            If the song has been uploaded soon, instead of a date it
            has somehing along the lisnes of "uploaded 2 hours ago"
            """
            self.year = time.strftime("%Y")
            self.month = time.strftime("%b")
            self.day = time.strftime("%d")

        else:
            song_date = song_date.split()     
            self.year = song_date[2]
            self.month = song_date[0]
            self.day = song_date[1][0:-1] 


class Song:
    def __init__(self, viperial_id, title, date):
        self.title = title
        self.viperial_id = viperial_id
        self.date = Date(date)
        self.sharebeast_id = None
        self.download_url = None
        
    def get_song_directory(self):
        return self.date.year + "/" + self.date.month
    
    def download_song(self):
        with urllib.request.urlopen(self.download_url) as response, open(self.title + ".mp3", 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        #TODO OS shiz

    def get_sharebeast_id(self):
        pattern = r'="http://www.sharebeast.com/(.*?)" target'
        song_url = "http://www.viperial.com/tracks/view/{}/".format(self.viperial_id)
        html_request = urllib.request.urlopen(song_url)
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
            html_request = urllib.request.urlopen("http://www.sharebeast.com/" + self.sharebeast_id)
            bytecode = html_request.read()
            htmlstr = bytecode.decode()
            result = re.findall(pattern, htmlstr)
            self.download_url = result[0]
    
    def is_song_wanted(self, time_period):
        song_wanted = False
        if(time_period.date_is_in_time_period(self.date)):
            song_wanted = True
        return song_wanted


class TimePeriod:
    def __init__(self, begin_date=None, end_date=None):
        self.begin_date = begin_date
        self.end_date = end_date

    def date_is_before_period(self, song_date):
        if self.begin_date == None:
            return False
        else:
            if int(self.begin_date.year) > int(song_date.year):
                return True
            elif int(self.begin_date.year) == int(song_date.year):
                if MONTHS.index(self.begin_date.month) > MONTHS.index(song_date.month):
                    return True
                elif MONTHS.index(this.begin_date.month) == MONTHS.index(song_date.month):
                    if int(self.begin_date.day) > int(song_date.day):
                        return True
        return False

    def date_is_after_period(self, song_date):
        if self.end_date == None:
            if int(this.end_date.year) <= 2010 and MONTHS.index(this.date.month) <= 8:
                return True
            else:
                return False    
        else:
            if int(self.end_date.year) < int(song_date.year):
                return True
            elif int(self.end_date.year) == int(song_date.year):
                if MONTHS.index(self.end_date.month) < MONTHS.index(song_date.month):
                    return True
                elif MONTHS.index(self.end_date.month) == MONTHS.index(song_date.month):
                    if int(self.end_date.day) < int(song_date.day):
                        return True
        return False
    
    def date_is_in_time_period(self, song_date):
        if self.date_is_before_period(song_date) or self.date_is_after_period(song_date):
            return False
        return True


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
    wanted_genres = set()
    #test data
    begin_date = Date(('2014', 'Jun', '12'))
    time_period = TimePeriod(None, begin_date)
    genre = 'Rap'
    current_page = 1
    #TODO add user input
    #while True:
    wanted_songs_list = crawl_entire_page(time_period, genre, current_page)
    current_page = current_page + 1
    #if not len(wanted_songs_list) == 0:
        #last_song = wanted_songs_list.pop()
        #a = after_period(parse_date(last_song[2]), end_date)
        #if a:
            #break
            #pass
        #wanted_songs_list.append(last_song)
    download_entire_page(wanted_songs_list)
    print("All downloads finished")
    

main()
    
#a = get_wanted_songs_information(2)
