from bs4 import BeautifulSoup
import requests
import re


class Lyrics:
    def __init__(self, artist, song):
        self.artist = artist
        self.song = song
        self.re_comments = re.compile(r'(\<\!\-\-.*?\-\-\>)')
        self.re_tags = re.compile(r'(<.*?>)')

    def get_url(self, artist, song):
        """ Creates a url depending on the artist and song name """
        base_url = 'https://www.azlyrics.com/lyrics/'

        # Removes spaces from the song names
        #TODO: Figure out what to do with songs/artists with punctuation
        #TODO: Handle misspelled artists/songs or artists/songs that do not exist
        artist = artist.split(' ')
        artist = ''.join(artist)

        song = song.split(' ')
        song = ''.join(song)

        final_url = base_url + f'{artist}/{song}.html'
        return final_url

    def find_lyrics(self, soup):
        css_path = 'div.col-xs-12:nth-child(2) > div:nth-child(8)'
        html = soup.select(css_path)
        if html:
            return html
        else:
            return 'invalid' #Invalid Input

    def remove_comments(self, html):
        html = ''.join(html)
        replacement = re.sub(self.re_comments, '', html)
        return replacement

    def remove_tags(self, html):
        html = ''.join(html)
        replacement = re.sub(self.re_tags, '', html)
        return replacement

    def start_request(self):
        url = self.get_url(self.artist, self.song)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        html = self.find_lyrics(soup)
        if html == 'invalid':
            return False
        else:
            pass
        html_str = []
        for x in html:
            html_str.append(str(x))
        no_comments = self.remove_comments(html_str)
        no_tag = self.remove_tags(no_comments)
        return no_tag
