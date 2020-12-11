#!/usr/bin/env python3
import re
import argparse
import sqlite3
from urllib.request import urlopen
from pathlib import Path
import xml.etree.ElementTree as ET
from requests_html import HTMLSession

class QuiteDb():
    def __init__(self, db):
        self.db = db
        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()

    def db_close(self):
        self.conn.close()

    def sub_list(self):
        self.c.execute('SELECT id FROM feeds WHERE text = "YouTube Subscriptions"')
        parent_id = str(self.c.fetchone()[0])
        self.c.execute('SELECT text FROM feeds WHERE parentId = ?', parent_id)
        subs = self.c.fetchall()
        return subs
    
    
    def sub_add(self, url):
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
            session = HTMLSession()
            response = session.get(url)
        except:
            print("Could not reach URL")
    
        if 'This video is restricted' in response.text:
            print("Video is restricted")
            return
    
        try:
            channel_name = response.html.search('"name": "{}"')[0]
        except:
            print("Channel name not found")
            return
        try:
            channel_id = response.html.search('"channelId" content="{}"')[0]
        except:
            print("Channel ID not found")
            return
    
        xml_url = 'https://www.youtube.com/feeds/videos.xml?channel_id=' + channel_id
        html_url = 'https://www.youtube.com/channel/' + channel_id
    
        # youtube icon image
        image = 'AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAQAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/EAAA/0AAAP9AAAD/cAAA/4AAAP+AAAD/gAAA/4AAAP+AAAD/QAAA/0AAAP8QAAAAAAAAAAAAAAAAAAD/YAAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA/2AAAAAAAAD/MAAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD/MAAA/1AAAP//AAD//wAA//8AAP//AAD//wAA//8QEP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA/2AAAP+AAAD//wAA//8AAP//AAD//wAA//8AAP//4OD//1BQ//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP+AAAD/gAAA//8AAP//AAD//wAA//8AAP//AAD/////////////wMD//yAg//8AAP//AAD//wAA//8AAP//AAD/gAAA/4AAAP//AAD//wAA//8AAP//AAD//wAA/////////////7Cw//8gIP//AAD//wAA//8AAP//AAD//wAA/4AAAP+AAAD//wAA//8AAP//AAD//wAA//8AAP//4OD//0BA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP+AAAD/UAAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD/YAAA/zAAAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA/zAAAAAAAAD/YAAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA/2AAAAAAAAAAAAAAAAAAAP8QAAD/QAAA/0AAAP+AAAD/gAAA/4AAAP+AAAD/gAAA/4AAAP9AAAD/QAAA/xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//8AAP//AADAAwAAgAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAEAAMADAAD//wAA//8AAA=='
        print(xml_url)
        print(html_url)
        self.c.execute('SELECT xmlUrl FROM feeds WHERE xmlUrl = ?', (xml_url,))
        sub_exists = self.c.fetchone()
        if sub_exists:
            print(f'"{channel_name}" not added already in feeds')
        else:
            self.c.execute('INSERT INTO feeds (id, text, xmlUrl, htmlUrl, image, parentId, rowToParent) VALUES (?, ?, ?, ?, ?, ?, ?)', (new_id, channel_name, xml_url, html_url, image, parent_id, parent_row))
            self.conn.commit()
            print(f'Added "{channel_name}" to feeds')

    def sub_rm(self, sub):
        # doesn't work if quiterss is open
        self.c.execute('DELETE FROM feeds WHERE text = ?', (sub,))
        if self.c.rowcount == 1:
            self.conn.commit()
            print(f'Deleted "{sub}" from feeds')
        else:
            try:
                sub = int(sub)
                if sub == 0:
                    print("Unable to find channel name/index number")
                else:
                    subs = self.sub_list()
                    del_sub = subs[sub - 1]
                    self.c.execute('DELETE FROM feeds WHERE text = ?', del_sub)
                    self.conn.commit()
                    print(f'Deleted index: {sub} name: "{del_sub[0]}" from feeds')
            except:
                print("Unable to find channel name/index number")

    def gen_xml(self, sub_file):
        self.c.execute('SELECT text, xmlUrl FROM feeds')
        subs = self.c.fetchall()
        print(subs)

        #opml = ET.Element('opml', version="1.1")
        #body = ET.SubElement(opml, 'body')
        #outline = ET.SubElement(body, 'outline', text="YouTube Subscriptions", title="YouTube Subscriptions")
        #outline.append((ET.fromstring('<outline text="{}" title="{}" type="rss" xmlUrl="https://www.youtube.com/feeds/videos.xml?channel_id={}" />'.format(channelName, channelName, channelId))))

        #tree = ET.ElementTree(opml)
        #try:
        #    tree.write(sub_file)
        #except Exception as e:
        #    print("{} Could not create file \'{}\'".format(e, subFile))
            

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--database', metavar="feeds.db", help="specify db location if not specified uses default location")
parser.add_argument('-l', '--list', help="list YouTube channels in feeds", action='store_true')
parser.add_argument('-a', '--add', metavar="(video/channel URL)", help="add channel to feeds.db")
parser.add_argument('-r', '--remove', metavar="(channel name/id)", help="remove channel from feeds.db")
parser.add_argument('-e', '--export', metavar="(channel name/id)", help="remove channel from feeds.db")
args = parser.parse_args()

if args.database:
    db = args.database
else:
    home = str(Path.home())
    db = home + '/.local/share/QuiteRss/QuiteRss/feeds.db'

url = 'https://www.youtube.com/user/craigenegger'
quite = QuiteDb(db)

if args.list:
    subs = quite.sub_list()

    print(f"\nYoutube Subscriptions ({db})")
    print("---------------------")
    num = 1
    for channel in subs:
        print(f"{num}: {channel[0]}")
        num += 1
elif args.add:
    quite.sub_add(args.add)
elif args.remove:
    quite.sub_rm(args.remove)
elif args.export:
    quite.gen_xml('subscription_manager')

quite.db_close()
