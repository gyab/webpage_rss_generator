import requests
from datetime import datetime, timedelta
import os
import urllib

from dotenv import load_dotenv
from lxml import etree
from bs4 import BeautifulSoup
from google.cloud import storage

load_dotenv()

RSS_FILE = os.getenv('rss_file')
TITLE = os.getenv('title')
FAVICON = os.getenv('favicon')
URL = os.getenv('url')
LINK_SELECTOR = os.getenv('link_selector')
AUTH_GOOGLE_FILE = os.getenv('auth_google_file')
RSS_FILE_NAME = os.getenv('rss_file')
BUCKET = os.getenv('bucket')
URL_RSS_FILE = f'https://storage.googleapis.com/{BUCKET}/{RSS_FILE_NAME}'


def create_feed():
    root = etree.Element("rss")
    channel = etree.Element("channel")
    root.append(channel)

    title = etree.Element("title")
    title.text = URL
    link = etree.Element("link")
    link.text = URL_RSS_FILE
    channel.append(title)
    channel.append(link)

    image = etree.Element("image")
    url = etree.Element("url")
    url.text = FAVICON
    title = etree.Element("title")
    title.text = TITLE
    image.append(url)
    image.append(title)
    channel.append(image)

    language = etree.Element("language")
    language.text = "en"
    channel.append(language)
    write_to_file(root)
    etree.dump(root)


def check_for_update(event, context):
    r = requests.head(URL)
    url_time = r.headers['last-modified']
    if datetime.strptime(url_time, "%a, %d %b %Y %I:%M:%S %Z") > datetime.now() - timedelta(days=2):
        print(f'new update to fetch today {RSS_FILE}')
        get_update()
    else:
        print(datetime.strptime(url_time, "%a, %d %b %Y %I:%M:%S %Z"))
        print(datetime.now() - timedelta(days=1))
        print(f'no update to fetch today {RSS_FILE}')


def parse_page(url):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup.select(LINK_SELECTOR)


def get_last_update_title():
    root = get_xml_root()
    if root.xpath("//item/title"):
        return root.xpath("//item/title")[0].text


def get_update():
    links = parse_page(URL)
    last_update_title = get_last_update_title()
    if links[0].get_text() != last_update_title:
        add_item_feed(links[0].get_text(), links[0]['href'])


def get_xml_root(file=URL_RSS_FILE):
    with urllib.request.urlopen(file) as url:
        xml_str = url.read()
        tree = etree.HTML(xml_str)
    return tree


def add_item_feed(tt, lk):
    root = get_xml_root()
    channel = root.xpath("//channel")[0]

    item = etree.Element("item")
    title = etree.Element("title")
    title.text = tt
    pubDate = etree.Element("pubDate")
    pubDate.text = datetime.now().isoformat()
    link = etree.Element("link")
    link.text = lk

    item.append(title)
    item.append(pubDate)
    item.append(link)
    language = channel.xpath("//language")[0]
    language.addnext(item)
    # write_to_file(root)
    send_to_cloud(root)


def delete_last_item(root):
    t = root.getchildren()[0].getchildren()[-1]
    t.getparent().remove(t)


def write_to_file(root):
    et = etree.ElementTree(root)
    et.write('rss.xml', pretty_print=True)


def send_to_cloud(root):
    client = storage.Client.from_service_account_json(
        AUTH_GOOGLE_FILE)
    bucket = client.get_bucket(BUCKET)
    blob = bucket.blob(RSS_FILE_NAME)
    blob.cache_control = 'no-store'
    blob.patch()
    blob.upload_from_string(etree.tostring(root), content_type='application/xml')


if __name__ == "__main__":
    check_for_update(1, 2)
    # create_feed()
