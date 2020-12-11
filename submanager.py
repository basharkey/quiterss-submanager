#!/usr/bin/env python3
import re
import argparse
import sqlite3
from urllib.request import urlopen
from pathlib import Path

class QuiteDb():
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()

    def list_subs(self):
        self.c.execute('SELECT id FROM feeds WHERE text = "YouTube Subscriptions"')
        parent_id = str(self.c.fetchone()[0])
        self.c.execute('SELECT text FROM feeds WHERE parentId = ?', parent_id)
        subs = self.c.fetchall()
        self.conn.close()
    
        print("\nYoutube Subscriptions")
        print("---------------------")
        num = 1
        for channel in subs:
            print(f"{num}: {channel[0]}")
            num += 1
    
    def add_sub(self, url):
        self.c.execute('SELECT id FROM feeds WHERE text = "YouTube Subscriptions"')
        parent_id = int(self.c.fetchone()[0])
        print(parent_id)
    
        self.c.execute('SELECT id FROM feeds ORDER BY id DESC')
        new_id = int(self.c.fetchone()[0]) + 1
        print(new_id)
    
        self.c.execute('SELECT rowToParent FROM feeds ORDER BY rowToParent DESC')
        parent_row = int(self.c.fetchone()[0]) + 1
        print(parent_row)
    
        try:
            request = urlopen(url)
            response = request.read()
        except:
            print("Could not reach URL")
    
        if 'This video is restricted' in response.decode():
            print("Video is restricted")
            return
    
        try:
            channel_name = re.search('"name": "(.+)"', response.decode()).group(1)
        except:
            print("Channel name not found")
            return
        try:
            channel_id = re.search('"channelId" content="(.+)"', response.decode()).group(1)
        except:
            print("Channel ID not found")
            return
    
        xml_url = 'https://www.youtube.com/feeds/videos.xml?channel_id=' + channel_id
        html_url = 'https://www.youtube.com/channel/' + channel_id
    
        # youtube icon image
        image = 'AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAQAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/EAAA/0AAAP9AAAD/cAAA/4AAAP+AAAD/gAAA/4AAAP+AAAD/QAAA/0AAAP8QAAAAAAAAAAAAAAAAAAD/YAAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA/2AAAAAAAAD/MAAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD/MAAA/1AAAP//AAD//wAA//8AAP//AAD//wAA//8QEP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA/2AAAP+AAAD//wAA//8AAP//AAD//wAA//8AAP//4OD//1BQ//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP+AAAD/gAAA//8AAP//AAD//wAA//8AAP//AAD/////////////wMD//yAg//8AAP//AAD//wAA//8AAP//AAD/gAAA/4AAAP//AAD//wAA//8AAP//AAD//wAA/////////////7Cw//8gIP//AAD//wAA//8AAP//AAD//wAA/4AAAP+AAAD//wAA//8AAP//AAD//wAA//8AAP//4OD//0BA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP+AAAD/UAAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD/YAAA/zAAAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA/zAAAAAAAAD/YAAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA/2AAAAAAAAAAAAAAAAAAAP8QAAD/QAAA/0AAAP+AAAD/gAAA/4AAAP+AAAD/gAAA/4AAAP9AAAD/QAAA/xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//8AAP//AADAAwAAgAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAEAAMADAAD//wAA//8AAA=='
        print(xml_url)
        print(html_url)
        self.c.execute('INSERT INTO feeds (id, text, xmlUrl, htmlUrl, image, parentId, rowToParent) VALUES (?, ?, ?, ?, ?, ?, ?)', (new_id, channel_name, xml_url, html_url, image, parent_id, parent_row))
        self.conn.commit()
        self.conn.close()
        print(f'Added "{channel_name}" to feeds')

home = str(Path.home())
db = home + '/.local/share/QuiteRss/QuiteRss/feeds.db'
url = 'https://www.youtube.com/user/craigenegger'
quite = QuiteDb(db)

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--list', help="list YouTube channels in feeds", action='store_true')
parser.add_argument('-a', '--add', metavar="(video/channel URL)", help="add channel to feeds")
parser.add_argument('-r', '--remove', metavar="(video/channel URL)", help="add channel to feeds")
args = parser.parse_args()

if args.list:
    quite.list_subs()
elif args.add:
    quite.add_sub(args.add)
