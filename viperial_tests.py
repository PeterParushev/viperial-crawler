from urllib import request
import re

requested_songs_ids = []
list_url = "http://www.viperial.com/tracks/list/{}"
pattern = r'hot[1-2].*?/(\d{5})/.*?(\w{3}\s*\d{1,2},\s*\d{4}).*?(?:Hip-Hop|Rap)'
r = request.urlopen(list_url.format(2))
bytecode = r.read()
htmlstr = bytecode.decode()
a = re.findall(pattern, htmlstr)
