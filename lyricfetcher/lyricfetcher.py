from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from bs4 import BeautifulSoup
import rumps
import webbrowser
import os
import requests
import re
import pkg_resources.py2_warn
import pkg_resources
import pathlib

rumps.debug_mode(True)

class LyricFetcher(rumps.App):
    @rumps.clicked('Get Lyrics')
    def get_artist(self, _):
        """ Creates an input window with title and dimensions for artist """
        context = {
            'title': 'Enter Artist\'s name',
            'ok': 'Submit',
            'cancel': 'Cancel',
        }
        artist = rumps.Window(**context, dimensions=(320,80)).run()
        # If they didn't cancel, ask for song name
        if artist.clicked:
            self.get_song(artist.text)

    def get_song(self, artist):
        """ Input window for song name """
        context = {
            'title': 'Enter Song name',
            'ok': 'Submit',
            'cancel': 'Cancel'
        }

        song = rumps.Window(**context, dimensions=(320,80)).run()
        # If they didn't cancel, grab lyrics
        if song.clicked:
            lyrics = self.lyrics(artist, song.text)
            if lyrics:
                self.write_lyrics(artist, song.text, lyrics)
            else:
                pass


    def write_lyrics(self, artist, song, lyrics):
        """ Grabs lyrics and puts them into an html file to display on browser """

        # Setting up Jinja2 environment
        env = Environment(
        loader=PackageLoader('lyricfetcher', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
        )

        # Grabs template and renders it with artist and song name and lyrics
        template = env.get_template('lyrics.html')
        text = template.render(artist=artist, song=song, lyrictext=lyrics)

        # Creating folder to place lyrics if it does not exist already
        folder_path = 'lyrics'
        if os.path.exists(folder_path) is not True:
            os.makedirs(folder_path)

        # Creates a html file separate from template with lyrics
        with open('lyrics/lyrics2.html', 'wb') as lt:
            lt.write(text.encode())

        self.open_file()

    def open_file(self):
        """ Opens html file in safari browser """
        # Grabs the file path so absolute paths don't have to be hardcoded
        file_path = os.path.realpath("lyrics/lyrics2.html")

        # Opens the created html file using the relative path from before
        file_url = f'file://{file_path}'
        browser_path = 'open -a /Applications/Safari.app %s'
        webbrowser.get(browser_path).open_new(file_url)

    def invalid_input(self, artist, song):
        self.artist = artist
        self.song = song
        alert = {
            'title': 'Invalid Input',
            'message': f'Artist or Song is incorrectly spelled.\nPlease try again.\n\n'\
                     + f'Given Artist: {self.artist}\n'\
                     + f'Given Song: {self.song}',
            'ok': 'Try Again',
            'cancel': 'Cancel'
        }
        alert = rumps.alert(**alert)
        if alert:
            self.get_artist(rumps.clicked)

    """ vvv Block that finds lyrics vvv """

    def get_url(self, artist, song):
        """ Creates a url depending on the artist and song name """
        BASE_URL = 'https://www.azlyrics.com/lyrics/'

        # Removes spaces from the song names
        #TODO: Figure out what to do with songs/artists with punctuation
        #TODO: Handle misspelled artists/songs or artists/songs that do not exist
        artist = artist.split(' ')
        artist = ''.join(artist)

        song = song.split(' ')
        song = ''.join(song)

        final_url = BASE_URL + f'{artist}/{song}.html'
        return final_url

    def find_lyrics(self, soup, artist, song):
        CSS_PATH = 'div.col-xs-12:nth-child(2) > div:nth-child(8)'
        html = soup.select(CSS_PATH)
        if html:
            return html
        else:
            self.invalid_input(artist, song)


    def remove_comments(self, html):
        html = ''.join(html)
        reComments = re.compile(r'(\<\!\-\-.*?\-\-\>)')
        replacement = re.sub(reComments, '', html)
        return replacement


    def remove_tags(self, html):
        html = ''.join(html)
        reTags = re.compile(r'(<.*?>)')
        replacement = re.sub(reTags, '', html)
        return replacement

    def lyrics(self, artist, song):
        url = self.get_url(artist, song)

        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        html = self.find_lyrics(soup, artist, song)

        html_str = []
        for x in html:
            html_str.append(str(x))

        no_comments = self.remove_comments(html_str)
        no_tag = self.remove_tags(no_comments)
        return no_tag


if __name__ == '__main__':
    LyricFetcher('Lyrics').run()