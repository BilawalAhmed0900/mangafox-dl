from __future__ import print_function, division

try:
	from urllib2 import urlopen, Request, HTTPError
except ImportError:
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError

import zlib
import sys
import os.path
import os
import re

if os.name == "nt":
    path_delim = "\\"
elif os.name == "posix":
    path_delim = "/"
    
download_all_ep = 1234567890
    
def main():
    from_ch = 1
    to_ch = download_all_ep
    
    print("mangafox-dl made by Dragneel1234")
    if len(sys.argv) == 1:
        pos_of_last_delim = len(sys.argv[0]) - sys.argv[0][::-1].find(path_delim)
        print("Usage: python {} Link-to-mangafox [[from]-[to]]".format(sys.argv[0][pos_of_last_delim : ]))
        sys.exit(0)
    elif len(sys.argv) > 2:
        if "-" in sys.argv[2]:
            _pos = sys.argv[2].find("-")
            from_ch_s = sys.argv[2][ :_pos]
            to_ch_s = sys.argv[2][_pos + 1: ]
            if from_ch_s != "":
                try:
                    from_ch = int(from_ch_s)
                    if from_ch == 0:
                        from_ch = 1
                except:
                    print("Not valid episode range. exiting...")
                    sys.exit(-1)
                
            if to_ch_s != "":
                try:
                    to_ch = int(to_ch_s)
                except:
                    print("Not valid episode range. exiting...")
                    sys.exit(-1)
                
                
    if "mangafox.me/manga/" in sys.argv[1]:
        print("[mangafox-dl] Detected a possibly series/chapter link")
        if ".html" in sys.argv[1]:
            try:
                download_chapter(sys.argv[1])
            except KeyboardInterrupt:
                print("\n\nKeyboard Interupt detected... exiting")
                sys.exit(-1)
        else:
            try:
                download_series(sys.argv[1], from_ch, to_ch)
            except KeyboardInterrupt:
                print("\n\nKeyboard Interupt detected... exiting")
                sys.exit(-1)
        
def download_series(url, from_ch, to_ch):
    url_http = url.replace("https://", "http://")
    print("[mangafox-dl] Requesting Webpage")
    print("[mangafox-dl] Reading Webpage")

    page = get_url_content(url_http)  
    truncated_for_name = page[page.find(b'og:title') + 19 : ]
    name = truncated_for_name[ : truncated_for_name.find(b' Manga"')]
    
    print("\n[mangafox-dl] Manga: {}".format(name.decode()))
    truncated_for_chapters = page[page.find((name.decode().upper() + " </a> Chapters").encode()) : ]
    print("[mangafox-dl] Getting Chapters")
    chapters = re.findall(b"//mangafox.me/manga/[a-z_]*/v[A-Z0-9]*/c[0-9]*/1.html", truncated_for_chapters)[::-1]
    if to_ch > len(chapters):
        to_ch = len(chapters)
        
    print("\n[mangafox-dl] Chapters: {}".format(len(chapters)))
    print("[mangafox-dl] Range: {}-{}".format(from_ch, to_ch))
    
    if not os.path.exists(name.decode()):
        os.makedirs(name.decode())
    
    range_list = list(range(from_ch - 1, to_ch))   
    for chap in range_list:
        print("\r[mangafox-dl] Downloading chapter: {:s}".format(str(chap + 1).zfill(3)), end="")
        sys.stdout.flush()
        
        Volume = chapters[chap][chapters[chap].find(b"/v") + 2 : ]
        Volume = Volume[ : Volume.find(b"/")]
        dir_name = name.decode() + path_delim + "Volume " + Volume.decode().zfill(2) + path_delim + "Chapter " + str(chap + 1).zfill(2)
        download_chapter("http:" + chapters[chap].decode().replace("1.html", ""), dir_name, chap + 1)
        
def download_chapter(url, dir_name = "Chapter", number = 0):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    first_page = get_url_content(url)
    find_str_I = b'<select onchange="change_page(this)" class="m">'
    find_str_II = b'class="btn next_page">'
    first_page = first_page[first_page.find(find_str_I) + len(find_str_I.decode()) : first_page.find(find_str_II)]
    urls = re.findall(b'<option value="[0-9]+" >', first_page)
    for i in range(0, len(urls)):
        NAME = dir_name + path_delim + "{}".format(i).zfill(3) + ".jpg"
        print("\r[mangafox-dl] Downloading chapter: {:s} | Panel: {:s}".format(str(number).zfill(3), str(i + 1).zfill(3)), end="")
        sys.stdout.flush()
        
        if os.path.isfile(NAME):
            continue
        
        urls[i] = urls[i][urls[i].find(b'"') + 1 : ]
        urls[i] = urls[i][ : urls[i].find(b'"')]
        
        page = get_url_content(url + urls[i].decode() + ".html")
        page = page[page.find(b'<div class="read_img">') +  22: ]
        page = page[page.find(b'<img src="') + 10 : ]
        page = page[ : page.find(b'"')]
        page.replace(b"https", b"http")
        
        img = get_url_content(page.decode())  
        file = open(NAME, "wb")
        file.write(img)
        file.close()
        
        
def get_url_content(url):
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        page_open = urlopen(req)
    except HTTPError as error:
        print("\n\n[mangafox-dl] Webpage({}) not found, Error code: {}".format(url, error.code))
        return b""
    
    try:
        is_encoded = page_open.info()["Content-Encoding"]
    except:
        is_encoded = "None"
        
    if is_encoded == "gzip":
        return zlib.decompress(page_open.read(), 16 + zlib.MAX_WBITS)
    elif is_encoded == "None" or is_encoded is None:
        return page_open.read()
    else:
        print(is_encoded)
        sys.exit(-1)
    
    
if __name__ == "__main__":
    main()
