import pygame
from pygame import mixer
from customtkinter import *
from CTkListbox import *
from tkinter.filedialog import askdirectory
import os

# todo additional window with stuff like volume or position (to make program consume less resources)

pygame.init()
MUSIC_END = pygame.USEREVENT+1
mixer.music.set_endevent(MUSIC_END)
pygame.event.set_allowed(MUSIC_END)

volume: float
volume_slider: CTkSlider
position_slider: CTkSlider
paused: bool = False
play_button: CTkButton
music_queue: list[str] = []
current_song_index: int = 0
music_listbox: CTkListbox


def end_check():
    global MUSIC_END
    for event in pygame.event.get():
        if event.type == MUSIC_END:
            play("next")

    window.after(100, end_check)


def volume_update(_):
    global volume, volume_slider
    volume = volume_slider.get() / 100
    mixer.music.set_volume(volume)


def position_update(_):
    global position_slider
    pos = position_slider.get() / 10
    if mixer.music.get_busy():
        mixer.music.set_pos(pos)


def load_songs():
    global music_queue, music_listbox

    music_directory = askdirectory()
    if not music_directory:
        return

    for root, _, files in os.walk(music_directory):
        for file in files:
            if file.endswith(".mp3") or file.endswith(".ogg") or file.endswith(".wav"):
                music_queue.append(os.path.join(root, file))
                music_listbox.insert(END, file[:-4])


def clear_playlist():
    global current_song_index, music_queue, music_listbox
    current_song_index = 0
    music_queue.clear()
    for widget in music_listbox.winfo_children():
        widget.destroy()


def play(mode: str = "default", song_name: str = ""):
    global volume, paused, music_queue, current_song_index, play_button, music_listbox

    if mode != "default":
        mixer.music.unload()
    if len(music_queue) < 1:
        return

    match mode:
        case "default":
            if paused:
                paused = False
                mixer.music.unpause()
                play_button.configure(text="Pause")
                return
            elif not paused and mixer.music.get_busy():
                paused = True
                mixer.music.pause()
                play_button.configure(text="Play")
                return
        case "listbox":
            current_song_index = music_listbox.curselection()
        case "next":
            current_song_index = (current_song_index + 1) % len(music_queue)
        case "prev":
            current_song_index = current_song_index - 1 if current_song_index > 0 else len(music_queue) - 1

    paused = False
    play_button.configure(text="Pause")
    song = music_queue[current_song_index]
    mixer.music.load(song)
    mixer.music.play()


if __name__ == "__main__":
    window = CTk()
    mixer.init()
    window.geometry("720x480")

    CTkButton(master=window, text="Load Songs", command=load_songs).pack()
    volume_slider = CTkSlider(master=window, orientation="horizontal", from_=0, to=100, command=volume_update)
    volume_slider.set(100)
    volume_slider.pack()

    position_slider = CTkSlider(master=window, orientation="horizontal", from_=0, to=1000)
    position_slider.bind("<ButtonRelease-1>", position_update)
    position_slider.pack()

    play_button = CTkButton(master=window, text="Play", command=play)
    play_button.pack()

    CTkButton(master=window, text="Next", command=lambda: play("next")).pack()
    CTkButton(master=window, text="Previous", command=lambda: play("prev")).pack()

    music_listbox = CTkListbox(master=window, command=lambda _: play("listbox"))
    # music_listbox.bind("<Double-Button-1>", lambda _: play("listbox"))
    music_listbox.pack()

    CTkButton(master=window, text="Clear Playlist", command=clear_playlist).pack()

    end_check()

    window.mainloop()
