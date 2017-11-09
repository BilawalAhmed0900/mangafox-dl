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
            download_chapter(sys.argv[1])
        else:
            download_series(sys.argv[1], from_ch, to_ch)
        
def download_series(url, from_ch, to_ch):
    url_http = url.replace("https://", "http://")
    req = Request(url_http)
    if not req:
        print("[mangafox-dl] Page not found...")
        sys.exit(-1)
    
    print("[mangafox-dl] Requesting Webpage")
    page_open = urlopen(req)
    print("[mangafox-dl] Reading Webpage")
    
    try:
        is_encoded = page_open.info()["Content-Encoding"]
    except:
        is_encoded = "None"
        
    if is_encoded == "gzip":
        page = zlib.decompress(page_open.read(), 16 + zlib.MAX_WBITS)
    else:
        page = page_open.read()
        
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
    for chap in range(from_ch - 1, to_ch):
        print("[mangafox-dl] Downloading chapter: {:s}".format(str(chap + 1).zfill(3)), end="\r")
        Volume = chapters[chap][chapters[chap].find(b"/v") + 2 : ]
        Volume = Volume[ : Volume.find(b"/")]
        dir_name = name.decode() + path_delim + "Volume " + Volume.decode().zfill(2) + path_delim + "Chapter " + str(chap + 1).zfill(2)
        download_chapter("http:" + chapters[chap].decode().replace("1.html", ""), dir_name, chap + 1)
    
def download_chapter(url, dir_name = "Chapter", number = 0):
    page_number = 1
    previous_img_url = ""
    
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    while True:
        page_url = url + "{}.html".format(page_number)
        req = Request(page_url)
        if not req:
            return
        
        page_open = urlopen(req)
        
        try:
            is_encoded = page_open.info()["Content-Encoding"]
        except:
            is_encoded = "None"
        
        if is_encoded == "gzip":
            page = zlib.decompress(page_open.read(), 16 + zlib.MAX_WBITS)
        else:
            page = page_open.read()

        truncated_for_pic = page[page.find(b'<div class="read_img">') : ]
        truncated_for_pic = truncated_for_pic[truncated_for_pic.find(b'<img src="') + 10 : ]
        pic_url = truncated_for_pic[ : truncated_for_pic.find(b'"')]
        real_img_url = pic_url.decode()[ : pic_url.decode().find("?token")]
        if previous_img_url == real_img_url or pic_url == b"":
            return
            
        pic_url.replace(b"https", b"http")
        pic_page_req = Request(pic_url.decode())
        pic_page = urlopen(pic_page_req)
        Size = int(pic_page.info()["Content-Length"])
        NAME = dir_name + path_delim + "{:3d}".format(page_number) + ".jpg"
        
        print("\r[mangafox-dl] Downloading chapter: {:s} | Panel: {:s}".format(str(number).zfill(3), str(page_number).zfill(3)), end="")
        sys.stdout.flush()
        if (os.path.isfile(NAME) and os.path.getsize(NAME) == Size):
            previous_img_url = pic_url.decode()
            page_number += 1 
            continue
        pic = open(NAME, "wb")
        while True:
            block_size = 8192
            block = pic_page.read(block_size)
            if not block:
                break
            else:
                pic.write(block)
                
        pic.close()
        previous_img_url = real_img_url
        page_number += 1 
    
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nKeyboard Interupt detected... exiting")
        sys.exit(-1)