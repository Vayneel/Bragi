import pygame
from pygame import mixer
from customtkinter import *
from CTkListbox import *
from tkinter.filedialog import askdirectory
from PIL import Image
import os
import json

if os.path.exists("settings.json"):
    with open("settings.json") as settings:
        volume = json.load(settings)["volume"]
else:
    with open("settings.json", "w") as settings:
        json.dump({"volume": 1}, settings)
    volume = 1

pygame.init()
MUSIC_END = pygame.USEREVENT+1
mixer.music.set_endevent(MUSIC_END)
pygame.event.set_allowed(MUSIC_END)
mixer.music.set_volume(volume)

window: CTk
volume_slider: CTkSlider
position_slider: CTkSlider
paused: bool = False
play_button: CTkButton
add_songs_button: CTkButton
clear_button: CTkButton
music_queue: list[str] = []
current_song_index: int = 0
current_song_label: CTkLabel
music_listbox: CTkListbox


def end_check(ctk: CTk):
    global MUSIC_END
    for event in pygame.event.get():
        if event.type == MUSIC_END:
            play("next")

    ctk.after(100, lambda: end_check(ctk))


def volume_update(_ = float(0), mode: str = ""):
    global volume, volume_slider
    volume = round(volume_slider.get() / 100, 2)
    if mode == "write":
        with open("settings.json", "w") as f:
            json.dump({"volume": volume}, f)
        return
    mixer.music.set_volume(volume)


def position_update(_):
    global position_slider
    pos = position_slider.get() / 10
    if mixer.music.get_busy():
        mixer.music.set_pos(pos)


def load_songs():
    global music_queue, music_listbox, clear_button, add_songs_button

    clear_button.configure(state="disabled")
    add_songs_button.configure(state="disabled")

    first_song = True if len(music_queue) < 1 else False

    music_directory = askdirectory()
    if not music_directory:
        clear_button.configure(state="normal")
        add_songs_button.configure(state="normal")
        return

    for root, _, files in os.walk(music_directory):
        for file in files:
            if file.endswith(".mp3") or file.endswith(".ogg") or file.endswith(".wav"):
                music_queue.append(os.path.join(root, file))
                music_listbox.insert(END, file[:-4])

            if first_song:
                first_song = False
                music_listbox.select(0)

    clear_button.configure(state="normal")
    add_songs_button.configure(state="normal")


def clear_playlist():
    global current_song_index, music_queue, music_listbox, current_song_label, add_songs_button, clear_button

    add_songs_button.configure(state="disabled")
    clear_button.configure(state="disabled")

    current_song_label.configure(text="BRAGI")
    current_song_index = 0
    music_queue.clear()
    mixer.music.unload()
    music_listbox.delete("all")

    add_songs_button.configure(state="normal")
    clear_button.configure(state="normal")


def play(mode: str = "default"):
    global volume, paused, music_queue, current_song_index, play_button, music_listbox, current_song_label

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

    song_label = music_listbox.get(current_song_index)
    song_label = song_label[:28] + "..." if not len(song_label) < 29 else song_label

    paused = False
    song = music_queue[current_song_index]
    current_song_label.configure(text=song_label)
    mixer.music.load(song)
    mixer.music.play()


def gui_startup():
    global volume_slider, position_slider, play_button, music_listbox, volume, current_song_label, add_songs_button
    global clear_button

    bragi_image = CTkImage(light_image=Image.open("bragi.png"),
                                  dark_image=Image.open("bragi.png"),
                                  size=(250, 250))
    color_soft_beige = "#E6D4B4"
    color_dark_charcoal = "#2D2A26"
    color_deep_red = "#A43B2A"
    color_golden_yellow = "#D4B363"
    font = ("Comic Sans MS", 16)

    ctk = CTk()
    ctk.configure(fg_color=color_soft_beige)
    ctk.geometry("720x480")
    ctk.title("BRAGI")
    ctk.resizable(False, False)
    ctk.iconbitmap("bragi.ico")

    sidebar = CTkFrame(master=ctk, fg_color=color_dark_charcoal, width=240, corner_radius=0)
    sidebar.pack(side="left", fill="y")

    add_songs_button = CTkButton(master=sidebar, text="Add Songs", command=load_songs, fg_color=color_golden_yellow,
              hover_color=color_deep_red, width=220, corner_radius=10, font=font,
              text_color=color_dark_charcoal, text_color_disabled=color_soft_beige)
    add_songs_button.pack(padx=10, pady=10)

    music_listbox = CTkListbox(master=sidebar,
                               command=lambda _: play("listbox"),
                               fg_color=color_soft_beige,
                               text_color=color_dark_charcoal, corner_radius=10,
                               hover_color=color_deep_red, highlight_color=color_golden_yellow,
                               border_width=0, scrollbar_button_color=color_soft_beige,
                               scrollbar_button_hover_color=color_golden_yellow)
    music_listbox.configure(font=font)
    music_listbox.pack(pady=10, padx=10, expand="y", fill="both")

    volume_slider = CTkSlider(master=sidebar, orientation="horizontal", from_=0, to=100, command=volume_update,
                              fg_color=color_soft_beige, progress_color=color_golden_yellow,
                              button_color=color_golden_yellow, hover=False)
    volume_slider.set(volume * 100)

    volume_slider.bind("<ButtonRelease-1>", lambda _: volume_update(mode="write"))
    volume_slider.pack(side="bottom", pady=30, padx=10, fill="x")

    clear_button = CTkButton(master=sidebar, text="Clear", command=clear_playlist, fg_color=color_golden_yellow,
              hover_color=color_deep_red, width=220, corner_radius=10, font=font,
              text_color=color_dark_charcoal, text_color_disabled=color_soft_beige)
    clear_button.pack(side="bottom", padx=10, pady=0)

    current_song_label = CTkLabel(master=ctk, text_color=color_dark_charcoal,
                                  font=("Comic Sans MS Bold", 24), text="BRAGI")
    current_song_label.pack(pady=30)

    current_song_image_image = CTkLabel(master=ctk, text="", image=bragi_image)
    current_song_image_image.pack(pady=0)

    command_frame = CTkFrame(master=ctk, fg_color=color_soft_beige)
    command_frame.pack(fill="x", padx=110, pady=20)

    CTkButton(master=command_frame, text="<", command=lambda: play("prev"), fg_color=color_golden_yellow,
              hover_color=color_deep_red, corner_radius=10, font=font, width=70,
              text_color=color_dark_charcoal, text_color_disabled=color_soft_beige).pack(side="left", expand=True,
                                                                                         fill="x", padx=5)

    play_button = CTkButton(master=command_frame, text="Play", command=play, fg_color=color_golden_yellow,
              hover_color=color_deep_red, corner_radius=10, font=font, width=70,
              text_color=color_dark_charcoal, text_color_disabled=color_soft_beige)
    play_button.pack(side="left", expand=True, fill="x", padx=5)

    CTkButton(master=command_frame, text=">", command=lambda: play("next"), fg_color=color_golden_yellow,
              hover_color=color_deep_red, corner_radius=10, font=font, width=70,
              text_color=color_dark_charcoal, text_color_disabled=color_soft_beige).pack(side="left", expand=True,
                                                                                         fill='x', padx=5)

    position_slider = CTkSlider(master=ctk, orientation="horizontal", from_=0, to=1000, width=250,
                                fg_color=color_dark_charcoal, progress_color=color_golden_yellow,
                                button_color=color_golden_yellow, hover=False)
    position_slider.bind("<ButtonRelease-1>", position_update)
    position_slider.pack()

    end_check(ctk)
    ctk.mainloop()
    return ctk


if __name__ == "__main__":
    mixer.init()
    # window = gui_startup()
    gui_startup()
