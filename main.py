from cProfile import label
from doctest import master

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

NO_SYS_TRAY = True

window: CTk
volume: float = -1
volume_slider: CTkSlider
position_slider: CTkSlider
paused: bool = False
play_button: CTkButton
music_queue: list[str] = []
current_song_index: int = 0
music_listbox: CTkListbox

COLOR_SOFT_BEIGE = "#E6D4B4"
COLOR_DARK_CHARCOAL = "#2D2A26"
COLOR_DEEP_RED = "#A43B2A"
COLOR_GOLDEN_YELLOW = "#D4B363"
COLOR_MUTED_GREEN = "#4A6F50"

if not NO_SYS_TRAY:
    iconified: bool
    image = Image.open("bragi.png")

    async def end_check():
        global MUSIC_END
        while 1:
            for event in pygame.event.get():
                if event.type == MUSIC_END:
                    play("next")

            await asyncio.sleep(0.1)


    def icon_command(icon, item):
        command = str(item)
        match command:
            case "Expand":
                print("Expanding... no")
            case "Exit":
                icon.stop()


    def iconify(ctk):
        global image, iconified
        iconified = True
        ctk.destroy()
        icon = Icon("Bragi", image, menu=Menu(
            MenuItem("Expand", icon_command),
            MenuItem("Exit", icon_command),
        ))
        icon.run()
else:
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

    if not mode == "listbox":
        music_listbox.select(current_song_index)

    play_button.configure(text="Pause")

    paused = False
    song = music_queue[current_song_index]
    mixer.music.load(song)
    mixer.music.play()


def gui_startup():
    global volume_slider, position_slider, play_button, music_listbox, volume
    # global iconified
    # iconified = False

    ctk = CTk()
    ctk.configure(fg_color=COLOR_SOFT_BEIGE)
    ctk.geometry("720x480")
    ctk.title("BRAGI")
    ctk.resizable(False, False)
    ctk.iconbitmap("bragi.ico")

    font = ("Garamond Bold", 16)

    # ctk.protocol("WM_DELETE_WINDOW", lambda: iconify(ctk))

    sidebar = CTkFrame(master=ctk, fg_color=COLOR_DARK_CHARCOAL, width=240, corner_radius=0)
    sidebar.pack(side="left", fill="y")

    CTkButton(master=sidebar, text="Add Songs", command=load_songs, fg_color=COLOR_GOLDEN_YELLOW,
              hover_color=COLOR_DEEP_RED, width=220, corner_radius=10, font=font,
              text_color=COLOR_DARK_CHARCOAL).pack(padx=10, pady=10)
    music_listbox = CTkListbox(master=sidebar, command=lambda _: play("listbox"), fg_color=COLOR_SOFT_BEIGE,
                               text_color=COLOR_DARK_CHARCOAL, font=font, corner_radius=10,
                               hover_color=COLOR_DEEP_RED, highlight_color=COLOR_GOLDEN_YELLOW,
                               border_width=0, scrollbar_button_color=COLOR_SOFT_BEIGE,
                               scrollbar_button_hover_color=COLOR_GOLDEN_YELLOW,)
    music_listbox.pack(pady=10, padx=10, expand="y", fill="both")
    volume_slider = CTkSlider(master=sidebar, orientation="horizontal", from_=0, to=100, command=volume_update,
                              fg_color=COLOR_SOFT_BEIGE, progress_color=COLOR_GOLDEN_YELLOW,
                              button_color=COLOR_GOLDEN_YELLOW, hover=False)
    volume_slider.set(volume if volume >= 0 else 100)
    volume_slider.pack(side="bottom", pady=30, padx=10, fill="x")
    CTkButton(master=sidebar, text="Clear", command=clear_playlist(), fg_color=COLOR_GOLDEN_YELLOW,
              hover_color=COLOR_DEEP_RED, width=220, corner_radius=10, font=font,
              text_color=COLOR_DARK_CHARCOAL).pack(side="bottom", padx=10, pady=0)

    # position_slider = CTkSlider(master=ctk, orientation="horizontal", from_=0, to=1000)
    # position_slider.bind("<ButtonRelease-1>", position_update)
    # position_slider.pack()
    #
    # play_button = CTkButton(master=ctk, text="Play", command=play)
    # play_button.pack()
    #
    # CTkButton(master=ctk, text="Next", command=lambda: play("next")).pack()
    # CTkButton(master=ctk, text="Previous", command=lambda: play("prev")).pack()

    # if iconify() is commented
    end_check(ctk)

    ctk.mainloop()

    return ctk


if __name__ == "__main__":
    mixer.init()
    window = gui_startup()
    # asyncio.run(end_check())
