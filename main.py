import pygame
from pygame import mixer
from customtkinter import *
from CTkListbox import *
from tkinter.filedialog import askdirectory
from pystray import Icon, Menu, MenuItem
from PIL import Image
import os
import asyncio

# todo additional window with stuff like volume or position (to make program consume less resources)

pygame.init()
MUSIC_END = pygame.USEREVENT+1
mixer.music.set_endevent(MUSIC_END)
pygame.event.set_allowed(MUSIC_END)

window: CTk
volume: float
volume_slider: CTkSlider
position_slider: CTkSlider
paused: bool = False
iconified: bool
play_button: CTkButton
music_queue: list[str] = []
current_song_index: int = 0
music_listbox: CTkListbox
image = Image.open("icon.png")


# async def end_check():
#     global MUSIC_END
#     while 1:
#         for event in pygame.event.get():
#             if event.type == MUSIC_END:
#                 play("next")
#
#         await asyncio.sleep(0.1)


def end_check(ctk: CTk):
    global MUSIC_END
    for event in pygame.event.get():
        if event.type == MUSIC_END:
            play("next")

    ctk.after(100, lambda: end_check(ctk))


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


def play(mode: str = "default"):
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

    play_button.configure(text="Pause")

    paused = False
    song = music_queue[current_song_index]
    mixer.music.load(song)
    mixer.music.play()


def icon_command(icon, item):
    command = str(item)
    match command:
        case "Expand":
            print("Expanding... no")
        case "Exit":
            icon.stop()


# def iconify(ctk):
#     global image, iconified
#     iconified = True
#     ctk.destroy()
#     icon = Icon("Bragi", image, menu=Menu(
#         MenuItem("Expand", icon_command),
#         MenuItem("Exit", icon_command),
#     ))
#     icon.run()


def gui_startup():
    global volume_slider, position_slider, play_button, music_listbox, iconified
    iconified = False
    ctk = CTk()
    ctk.geometry("720x480")
    # ctk.protocol("WM_DELETE_WINDOW", lambda: iconify(ctk))

    CTkButton(master=ctk, text="Load Songs", command=load_songs).pack()
    volume_slider = CTkSlider(master=ctk, orientation="horizontal", from_=0, to=100, command=volume_update)
    volume_slider.set(100)
    volume_slider.pack()

    position_slider = CTkSlider(master=ctk, orientation="horizontal", from_=0, to=1000)
    position_slider.bind("<ButtonRelease-1>", position_update)
    position_slider.pack()

    play_button = CTkButton(master=ctk, text="Play", command=play)
    play_button.pack()

    CTkButton(master=ctk, text="Next", command=lambda: play("next")).pack()
    CTkButton(master=ctk, text="Previous", command=lambda: play("prev")).pack()

    music_listbox = CTkListbox(master=ctk, command=lambda _: play("listbox"))
    music_listbox.pack()

    CTkButton(master=ctk, text="Clear Playlist", command=clear_playlist).pack()

    # if iconify() is commented
    end_check(ctk)

    ctk.mainloop()

    return ctk


if __name__ == "__main__":
    mixer.init()
    window = gui_startup()
    # asyncio.run(end_check())
