from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from lyric.get_lyrics import Lyrics
import rumps
import webbrowser
import os
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
        artist = rumps.Window(**context, dimensions=(320, 80)).run()
        # If they didn't cancel, ask for song name
        if artist.clicked:
            self.artist = artist.text
            self.get_song()

    def get_song(self):
        """ Input window for song name """
        context = {
            'title': 'Enter Song name',
            'ok': 'Submit',
            'cancel': 'Cancel'
        }
        song = rumps.Window(**context, dimensions=(320, 80)).run()
        # If they didn't cancel, grab lyrics
        if song.clicked:
            self.song = song.text
            lyrics = Lyrics(self.artist, self.song).start_request()
            if lyrics:
                self.write_lyrics(lyrics)
            else:
                self.invalid_input()

    def write_lyrics(self, lyrics):
        """ Grabs lyrics and puts them into an html file to display on browser """

        # Setting up Jinja2 environment
        env = Environment(loader=PackageLoader('lyric', 'templates'),
                          autoescape=select_autoescape(['html', 'xml'])
                          )
        template_context = {'artist': self.artist,
                            'song': self.song,
                            'lyrictext': lyrics}
        # Grabs template and renders it with artist and song name and lyrics
        template = env.get_template('lyrics_template.html')
        text = template.render(**template_context)

        # Creating folder to place lyrics if it does not exist already
        folder_path = 'lyrics'
        if os.path.exists(folder_path) is not True:
            os.makedirs(folder_path)

        # Creates a html file separate from template with lyrics
        with open('lyrics/lyrics.html', 'wb') as lt:
            lt.write(text.encode())

        self.open_file()

    def open_file(self):
        """ Opens html file in safari browser """
        # Grabs the file path so absolute paths don't have to be hardcoded
        file_path = os.path.realpath("lyrics/lyrics.html")

        # Opens the created html file using the relative path from before
        file_url = f'file://{file_path}'
        browser_path = 'open -a /Applications/Safari.app %s'
        webbrowser.get(browser_path).open_new(file_url)

    def invalid_input(self):
        alert = {
            'title': 'Invalid Input',
            'message': f'Artist or Song is incorrectly spelled.\nPlease try again.\n\n'
                     + f'Given Artist: {self.artist}\n'
                     + f'Given Song: {self.song}'
                     + f'{os.getcwd()}',
            'ok': 'Try Again',
            'cancel': 'Cancel'
        }
        alert = rumps.alert(**alert)
        if alert:
            self.get_artist(rumps.clicked)
