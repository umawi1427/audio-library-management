import re
import pandas as pd
import os
import json
import random
import string

class User:
    def __init__(self, username, password, email, music_collection=None, playlists=None, favorites=None):
        self.username = username
        self.password = password
        self.email = email
        self.music_collection = music_collection if music_collection is not None else []
        self.playlists = playlists if playlists is not None else []
        self.favorites = favorites if favorites is not None else []

    @staticmethod
    def load_users():
        if os.path.exists('users.csv'):
            return pd.read_csv('users.csv')
        else:
            return pd.DataFrame(columns=['username', 'password', 'email', 'music_collection', 'playlists', 'favorites'])

    @staticmethod
    def save_users(users_df):
        users_df.to_csv('users.csv', index=False)


    @staticmethod
    def create_account(username, password, email=None):
        users_df = User.load_users()

        if username in users_df['username'].values:
            print("Username already exists.")
            return None

        while True:
            if email is None or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                print("Invalid email address.")
                email = input("Enter a valid email address: ")
            else:
                if email in users_df['email'].values:
                    print("Email address already in use.")
                    email = input("Enter a different email address: ")
                else:
                    break

        new_user = pd.DataFrame([{
            'username': username,
            'password': password,
            'email': email,
            'music_collection': json.dumps([]),
            'playlists': json.dumps([]),
            'favorites': json.dumps([])
        }])
        users_df = pd.concat([users_df, new_user], ignore_index=True)
        User.save_users(users_df)
        return User(username, password, email)

    @staticmethod
    def login(username, password):
        while True:
            users_df = User.load_users()

            user_data = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
            if not user_data.empty:
                user_data = user_data.iloc[0]
                user_obj = User(
                    username, password, user_data['email'],
                    json.loads(user_data['music_collection']),
                    json.loads(user_data['playlists']),
                    json.loads(user_data['favorites'])
                )
                user_obj.music_collection = [Song(**song) for song in user_obj.music_collection]
                user_obj.playlists = [Playlist.from_dict(pl) for pl in user_obj.playlists]
                user_obj.favorites = [Song(**song) for song in user_obj.favorites]

                print(f"Hi, {username}")
                return user_obj
            else:
                print("Invalid username or password. Please try again.")
                username = input("Enter username: ")
                password = input("Enter password: ")

    def logout(self):
        print(f"User {self.username} logged out.")
        self.save_user_data()

    def save_user_data(self):
        users_df = User.load_users()
        user_idx = users_df[users_df['username'] == self.username].index[0]

        users_df.at[user_idx, 'music_collection'] = json.dumps([song.__dict__ for song in self.music_collection])
        users_df.at[user_idx, 'playlists'] = json.dumps([playlist.to_dict() for playlist in self.playlists])
        users_df.at[user_idx, 'favorites'] = json.dumps([song.__dict__ for song in self.favorites])

        User.save_users(users_df)

    def add_song_to_collection(self, song):
        if any(existing_song == song for existing_song in self.music_collection):
            print("Song with the same title already exists in the collection.")
            return
        else:
            self.music_collection.append(song)
            self.save_user_data()
            print("Song added to collection.")

    def remove_song_from_collection(self, song_title):
        self.music_collection = [song for song in self.music_collection if song.title != song_title]
        self.save_user_data()

    def view_collection(self):
        if not self.music_collection:
            print("No songs in your collection.")
        for song in self.music_collection:
            print(song)

    def create_playlist(self, name):
        self.playlists.append(Playlist(name))
        self.save_user_data()

    def delete_playlist(self, name):
        self.playlists = [playlist for playlist in self.playlists if playlist.name != name]
        self.save_user_data()

    def add_song_to_playlist(self, playlist_name, song):
        playlist = next((pl for pl in self.playlists if pl.name == playlist_name), None)
        if playlist:
            playlist.add_song(song)
            self.save_user_data()
            print("Song added to playlist.")
        else:
            print("Playlist not found.")

    def remove_song_from_playlist(self, playlist_name, song_title):
        for playlist in self.playlists:
            if playlist.name == playlist_name:
                playlist.remove_song(song_title)
                self.save_user_data()
                break

    def view_playlists(self):
        if not self.playlists:
            print("No playlists available.")
        for playlist in self.playlists:
            print(f"Playlist: {playlist.name}")
            playlist.view_songs()

    def search_songs(self, keyword):
        results = [song for song in self.music_collection if keyword.lower() in song.title.lower()]
        for song in results:
            print(song)

    def filter_songs(self, criteria):
        pass

    def add_song_to_favorites(self, song):
        if song not in self.favorites:
            self.favorites.append(song)
            self.save_user_data()
            print("Song added to favorites.")
        else:
            print("Song is already in favorites.")

    def remove_song_from_favorites(self, song_title):
        self.favorites = [song for song in self.favorites if song.title != song_title]
        self.save_user_data()
        print("Song removed from favorites.")

    def view_favorites(self):
        if not self.favorites:
            print("No favorite songs.")
        for song in self.favorites:
            print(song)

    def view_profile(self):
        print(f"Username: {self.username}")
        print(f"Password: {self.password}")
        print(f"Email: {self.email}")

    def edit_profile(self, new_username=None, new_password=None, new_email=None):
        users_df = User.load_users()
        user_idx = users_df[users_df['username'] == self.username].index[0]

        updated = False

        if new_username:
            if new_username in users_df['username'].values:
                print("Profile updated successfully.")
                return
            if new_username != self.username:
                self.username = new_username
                users_df.at[user_idx, 'username'] = new_username
                updated = True

        if new_password:
            if new_password != self.password:
                self.password = new_password
                users_df.at[user_idx, 'password'] = new_password
                updated = True

        if new_email:
            if new_email in users_df['email'].values:
                print("Email already exists.")
                return
            if new_email != self.email:
                self.email = new_email
                users_df.at[user_idx, 'email'] = new_email
                updated = True

        if updated:
            User.save_users(users_df)
            print("Profile updated successfully.")
        else:
            print("No changes made to the profile.")

    @staticmethod
    def delete_account(username):
        users_df = User.load_users()
        users_df = users_df[users_df['username'] != username]
        User.save_users(users_df)
        print(f"Account '{username}' deleted successfully.")

    @staticmethod
    def forgot_username(email):
        users_df = User.load_users()
        user_data = users_df[users_df['email'] == email]
        if not user_data.empty:
            print(f"Your username is: {user_data.iloc[0]['username']}")
        else:
            print("Email not found in the records.")

    @staticmethod
    def forgot_password(username, email):
        users_df = User.load_users()
        user_data = users_df[(users_df['username'] == username) & (users_df['email'] == email)]
        if not user_data.empty:
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            user_idx = user_data.index[0]
            users_df.at[user_idx, 'password'] = new_password
            User.save_users(users_df)
            print(f"A new password has been generated for ypur account: {new_password}")
        else:
            print("Username or email not found in the records.")

class Song:
    def __init__(self, title, artist, album, genre, duration):
        self.title = title
        self.artist = artist
        self.album = album
        self.genre = genre
        self.duration = duration

    def __str__(self):
        return f"{self.title} by {self.artist} from the album {self.album} ({self.genre}) - {self.duration}"

    def __eq__(self, other):
        if isinstance(other, Song):
            return self.title == other.title
        return False

class Playlist:
    def __init__(self, name):
        self.name = name
        self.songs = []

    def add_song(self, song):
        self.songs.append(song)

    def remove_song(self, song_title):
        self.songs = [song for song in self.songs if song.title != song_title]

    def view_songs(self):
        if not self.songs:
            print(f"No songs in playlist '{self.name}'.")
        for song in self.songs:
            print(song)

    def total_duration(self):
        return sum([song.duration for song in self.songs])

    def to_dict(self):
        return {
            'name': self.name,
            'songs': [song.__dict__ for song in self.songs]
        }

    @staticmethod
    def from_dict(data):
        playlist = Playlist(data['name'])
        playlist.songs = [Song(**song) for song in data['songs']]
        return playlist

class Player:
    def __init__(self):
        self.current_song = None
        self.is_playing = False
        self.current_playlist = None
        self.song_index = 0

    def play(self):
        if self.current_playlist and self.current_playlist.songs:
            if 0 <= self.song_index < len(self.current_playlist.songs):
                self.current_song = self.current_playlist.songs[self.song_index]
                self.is_playing = True
                self.display_current_song()
            else:
                print("Song index out of range.")
        else:
            print("No playlist loaded or playlist is empty.")

    def pause(self):
        self.is_playing = False
        print("Playback paused.")

    def stop(self):
        self.is_playing = False
        self.current_song = None
        self.song_index = 0
        print("Playback stopped.")

    def next_song(self):
        if self.current_playlist and self.current_playlist.songs:
            self.song_index = (self.song_index + 1) % len(self.current_playlist.songs)
            self.play()
        else:
            print("No playlist loaded or playlist is empty.")

    def previous_song(self):
        if self.current_playlist and self.current_playlist.songs:
            self.song_index = (self.song_index - 1) % len(self.current_playlist.songs)
            self.play()
        else:
            print("No playlist loaded or playlist is empty.")

    def display_current_song(self):
        if self.current_song:
            print(f"Now playing: {self.current_song}")

    def load_playlist(self, playlist):
        if playlist and playlist.songs:
            self.current_playlist = playlist
            self.song_index = 0
            print(f"Playlist '{playlist.name}' loaded.")
        else:
            print("Playlist is empty or not valid.")

def initialize_user_file():
    if not os.path.exists('users.csv'):
        try:
            df = pd.DataFrame(columns=['username', 'password', 'email', 'music_collection', 'playlists', 'favorites'])
            df.to_csv('users.csv', index=False)
        except IOError as e:
            print(f"Error initializing user file: {e}")

def main(choice=None):
    initialize_user_file()
    current_user = None
    player = Player()

    while True:
        if not current_user:
            print("\nMain Menu:")
            print("1. Create Account")
            print("2. Login")
            print("3. Forgot Username")
            print("4. Forgot Password")
            print("5. Exit")

            if not choice:
                choice = input("Enter your choice: ")

            if choice == '1':
                while True:
                    username = input("Enter username: ")
                    password = input("Enter password: ")
                    email = input("Enter email: ")
                    current_user = User.create_account(username, password, email)
                    if current_user:
                        print("Account created successfully.")
                    break
            elif choice == '2':
                username = input("Enter username: ")
                password = input("Enter password: ")
                current_user = User.login(username, password)
                if current_user:
                    print("Logged in successfully.")
            elif choice == '3':
                email = input("Enter your email: ")
                User.forgot_username(email)
            elif choice == '4':
                username = input("Enter username: ")
                email = input("Enter email: ")
                User.forgot_password(username, email)
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")
        else:
            print("\nUser Menu:")
            print("1. View Music Collection")
            print("2. Add Song to Collection")
            print("3. Remove Song from Collection")
            print("4. Create Playlist")
            print("5. Delete Playlist")
            print("6. Add Song to Playlist")
            print("7. Remove Song from Playlist")
            print("8. View Playlists")
            print("9. Search Songs")
            print("10. Play Playlist")
            print("11. View Favorite Songs")
            print("12. Add Song to Favorites")
            print("13. Remove Song from Favorites")
            print("14. View Profile")
            print("15. Edit Profile")
            print("16. Delete Account")
            print("17. Logout")

            if not choice:
                choice = input("Enter your choice: ")

            try:
                if choice == '1':
                    current_user.view_collection()
                elif choice == '2':
                    title = input("Enter song title: ")
                    artist = input("Enter artist: ")
                    album = input("Enter album: ")
                    genre = input("Enter genre: ")
                    duration = float(input("Enter duration (minutes): "))
                    song = Song(title, artist, album, genre, duration)
                    current_user.add_song_to_collection(song)
                elif choice == '3':
                    title = input("Enter song title to remove: ")
                    current_user.remove_song_from_collection(title)
                elif choice == '4':
                    name = input("Enter playlist name: ")
                    current_user.create_playlist(name)
                elif choice == '5':
                    name = input("Enter playlist name to delete: ")
                    current_user.delete_playlist(name)
                elif choice == '6':
                    playlist_name = input("Enter playlist name: ")
                    title = input("Enter song title: ")
                    song = next((s for s in current_user.music_collection if s.title == title), None)
                    if song:
                        current_user.add_song_to_playlist(playlist_name, song)
                    else:
                        print("Song not found in collection.")
                elif choice == '7':
                    playlist_name = input("Enter playlist name: ")
                    title = input("Enter song title to remove: ")
                    current_user.remove_song_from_playlist(playlist_name, title)
                elif choice == '8':
                    current_user.view_playlists()
                elif choice == '9':
                    keyword = input("Enter keyword to search: ")
                    current_user.search_songs(keyword)
                elif choice == '10':
                    name = input("Enter playlist name to play: ")
                    playlist = next((pl for pl in current_user.playlists if pl.name == name), None)
                    if playlist:
                        player.load_playlist(playlist)
                        player.play()
                    else:
                        print("Playlist not found.")
                elif choice == '11':
                    current_user.view_favorites()
                elif choice == '12':
                    title = input("Enter song title: ")
                    song = next((s for s in current_user.music_collection if s.title == title), None)
                    if song:
                        current_user.add_song_to_favorites(song)
                    else:
                        print("Song not found in collection.")
                elif choice == '13':
                    title = input("Enter song title to remove from favorites: ")
                    current_user.remove_song_from_favorites(title)
                elif choice == '14':
                    current_user.view_profile()
                elif choice == '15':
                    new_username = input("Enter new username (leave blank to keep current): ")
                    new_password = input("Enter new password (leave blank to keep current): ")
                    new_email = input("Enter new email (leave blank to keep current): ")
                    current_user.edit_profile(new_username if new_username else None, new_password if new_password else None, new_email if new_email else None)
                elif choice == '16':
                    confirm = input("Are you sure you want to delete your account? (yes/no): ")
                    if confirm.lower() == 'yes':
                        User.delete_account(current_user.username)
                        current_user = None
                elif choice == '17':
                    current_user.logout()
                    current_user = None
                else:
                    print("Invalid choice. Please try again.")
            except Exception as e:
                print(f"An error occurred: {e}")

        choice = None
        
if __name__ == "__main__":
    main()
