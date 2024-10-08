import pygame
from pygame import mixer
from customtkinter import *
from CTkListbox import *
from tkinter.filedialog import askdirectory
from PIL import Image
import os
import sys
from random import shuffle, choice

pygame.init()
mixer.init()
MUSIC_END = pygame.USEREVENT + 1
mixer.music.set_endevent(MUSIC_END)
pygame.event.set_allowed(MUSIC_END)
mixer.music.set_volume(1)

# Other variables
window: CTk
volume_slider: CTkSlider
volume: float = 0
position_slider: CTkSlider
shuffle_slider: CTkSlider
shuffle_value: bool = False
paused: bool = False
# prev_button: CTkButton
play_button: CTkButton
add_songs_button: CTkButton
clear_button: CTkButton
music_queue: list[str] = []
unused_indexes: list[int] = []
used_indexes: list[int] = []
current_used_song_index: int = 0
current_song_index: int = 0
current_song_label: CTkLabel
current_song_length: float = 0
music_listbox: CTkListbox


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return os.path.join(os.path.abspath("."), relative_path)


def end_check(ctk: CTk):
    global MUSIC_END
    for event in pygame.event.get():
        if event.type == MUSIC_END:
            play("next")
    ctk.after(100, lambda: end_check(ctk))


def volume_update(_):
    global volume, volume_slider
    volume = round(volume_slider.get() / 100, 2)
    mixer.music.set_volume(volume)


def position_update(_):
    global position_slider, current_song_length
    pos = position_slider.get() / 100 * current_song_length
    if mixer.music.get_busy():
        mixer.music.set_pos(pos)


def shuffle_update(_):
    global shuffle_slider, shuffle_value#, prev_button#, music_listbox, music_queue, used_indexes, current_song_index
    shuffle_value = not shuffle_value
    shuffle_slider.set(int(shuffle_value))
    # prev_button.configure(state="disabled" if shuffle_value else "normal")
    # if shuffle_value:
        # if music_listbox.size() > 2:
        #     shuffle(music_queue)
        #     listbox_update()


def clear_listbox():
    global music_listbox, current_song_index, current_song_label
    if music_listbox.size():
        current_song_label.configure(text="BRAGI")
        current_song_index = 0
        mixer.music.unload()
        music_listbox.delete("all")

def listbox_update():
    global music_queue, music_listbox, clear_button, add_songs_button, current_song_index, current_song_label,\
        shuffle_slider, unused_indexes, used_indexes, current_used_song_index

    clear_button.configure(state="disabled")
    add_songs_button.configure(state="disabled")
    shuffle_slider.configure(state="disabled")

    if len(music_queue) > 0:
        clear_listbox()

    for song in music_queue:
        song = song.split("\\")[-1][:-4]
        music_listbox.insert(END, song[:16] + ".." if len(song) > 15 else song)

    if music_listbox.size() > 0:
        music_listbox.select(0)
        unused_indexes = list(range(1, len(music_queue)))
        used_indexes = [0]
        current_used_song_index = 0

    clear_button.configure(state="normal")
    add_songs_button.configure(state="normal")
    shuffle_slider.configure(state="normal")


def load_songs():
    global music_queue#, shuffle_value

    music_directory = askdirectory()
    if not music_directory:
        return

    for root, _, files in os.walk(music_directory):
        for file in files:
            if file.endswith(".mp3") or file.endswith(".ogg") or file.endswith(".wav"):
                music_queue.append(os.path.join(root, file))

    # if shuffle_value:
    #     shuffle(music_queue)
    listbox_update()


def clear_playlist():
    global current_song_index, music_queue, music_listbox, current_song_label, add_songs_button, clear_button,\
        shuffle_slider, unused_indexes, used_indexes

    add_songs_button.configure(state="disabled")
    clear_button.configure(state="disabled")
    shuffle_slider.configure(state="disabled")

    music_queue.clear()
    unused_indexes.clear()
    used_indexes.clear()
    clear_listbox()

    add_songs_button.configure(state="normal")
    clear_button.configure(state="normal")
    shuffle_slider.configure(state="normal")


def play(mode: str = "default"):
    global paused, music_queue, current_song_index, play_button, music_listbox, current_song_label,\
        current_song_length, unused_indexes, used_indexes, current_used_song_index

    if mode != "default":
        mixer.music.unload()
    if len(music_queue) < 1:
        return

    if len(unused_indexes) == 0:
        unused_indexes = list(range(len(music_queue)))
        for index in used_indexes:
            unused_indexes.remove(index)
    if len(used_indexes) > 10:
        used_indexes = used_indexes[-10:]
        current_used_song_index = 9

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
            if shuffle_value and not current_used_song_index == len(used_indexes) - 1:
                current_song_index = used_indexes[used_indexes.index(current_song_index) + 1]
            else:
                if shuffle_value:
                    current_song_index = choice(unused_indexes)
                else:
                    current_song_index = (current_song_index + 1) % len(music_queue)

                if current_song_index in unused_indexes:
                    unused_indexes.remove(current_song_index)
                if current_song_index not in used_indexes:
                    used_indexes.append(current_song_index)

            if current_used_song_index < 9:
                current_used_song_index += 1
        case "prev":
            if shuffle_value:
                if current_song_index != used_indexes[0]:
                    current_used_song_index -= 1
                else:
                    current_used_song_index = 9
                current_song_index = used_indexes[current_used_song_index]
            else:
                current_song_index = current_song_index - 1 if current_song_index > 0 else len(music_queue) - 1
                if current_song_index in unused_indexes:
                    unused_indexes.remove(current_song_index)
                if current_song_index not in used_indexes:
                    used_indexes.append(current_song_index)
                if current_used_song_index < 9:
                    current_used_song_index += 1

    if not mode == "listbox":
        music_listbox.select(current_song_index)

    play_button.configure(text="Pause")

    song_label = music_queue[current_song_index].split("\\")[-1][:-4]
    song_label = song_label[:28] + "..." if not len(song_label) < 29 else song_label

    paused = False
    song = music_queue[current_song_index]
    current_song_label.configure(text=song_label)
    current_song_length = mixer.Sound(song).get_length()
    mixer.music.load(song)
    mixer.music.play()


def gui_startup():
    global volume_slider, position_slider, play_button, music_listbox, current_song_label, add_songs_button, \
        clear_button, shuffle_slider#, prev_button

    bragi_image = CTkImage(Image.open(resource_path("bragi.png")),
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
    ctk.iconbitmap(resource_path("bragi.ico"))

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
    music_listbox.pack(pady=0, padx=10, expand="y", fill="both")

    clear_button = CTkButton(master=sidebar, text="Clear", command=clear_playlist, fg_color=color_golden_yellow,
              hover_color=color_deep_red, width=220, corner_radius=10, font=font,
              text_color=color_dark_charcoal, text_color_disabled=color_soft_beige)
    clear_button.pack(side="bottom", padx=10, pady=10)

    current_song_label = CTkLabel(master=ctk, text_color=color_dark_charcoal,
                                  font=("Comic Sans MS Bold", 24), text="BRAGI")
    current_song_label.pack(pady=30)

    current_song_image_image = CTkLabel(master=ctk, text="", image=bragi_image)
    current_song_image_image.pack(pady=0)

    command_frame = CTkFrame(master=ctk, fg_color=color_soft_beige)
    command_frame.pack(fill="x", padx=120, pady=10)

    # prev_button = CTkButton(master=command_frame, text="<", command=lambda: play("prev"), fg_color=color_golden_yellow,
    #           hover_color=color_deep_red, width=70, corner_radius=10, font=font, text_color_disabled=color_soft_beige,
    #           text_color=color_dark_charcoal)
    # prev_button.pack(side="left", padx=5)
    CTkButton(master=command_frame, text="<", command=lambda: play("prev"), fg_color=color_golden_yellow,
              hover_color=color_deep_red, width=70, corner_radius=10, font=font, text_color_disabled=color_soft_beige,
              text_color=color_dark_charcoal).pack(side="left", padx=5)

    play_button = CTkButton(master=command_frame, text="Play", command=play, fg_color=color_golden_yellow,
                            hover_color=color_deep_red, width=70, corner_radius=10, font=font,
                            text_color=color_dark_charcoal)
    play_button.pack(side="left", padx=5)

    CTkButton(master=command_frame, text=">", command=lambda: play("next"), fg_color=color_golden_yellow,
              hover_color=color_deep_red, width=70, corner_radius=10, font=font,
              text_color=color_dark_charcoal).pack(side="left", padx=5)

    sliders_frame = CTkFrame(master=ctk, fg_color=color_soft_beige)
    sliders_frame.pack(fill="x", padx=125, pady=0)

    sf_0 = CTkFrame(master=sliders_frame, fg_color=color_soft_beige)
    sf_0.pack(fill="x", padx=0, pady=0)

    CTkLabel(master=sf_0, font=font, text_color=color_dark_charcoal, width=70,
             text="Position").pack(side="left", pady=0, padx=0)
    position_slider = CTkSlider(master=sf_0, orientation="horizontal", from_=0, to=100,
                                fg_color=color_dark_charcoal, progress_color=color_golden_yellow,
                                button_color=color_golden_yellow, hover=False, width=150, border_width=0)
    position_slider.bind("<ButtonRelease-1>", position_update)
    position_slider.pack(side="right", pady=0, padx=0)

    sf_1 = CTkFrame(master=sliders_frame, fg_color=color_soft_beige)
    sf_1.pack(fill="x", padx=0, pady=0)

    CTkLabel(master=sf_1, font=font, text_color=color_dark_charcoal, width=70,
             text="Volume").pack(side="left", pady=0, padx=0)
    volume_slider = CTkSlider(master=sf_1, orientation="horizontal", from_=0, to=100, command=volume_update,
                                fg_color=color_dark_charcoal, progress_color=color_golden_yellow,
                                button_color=color_golden_yellow, hover=False, width=150, border_width=0)
    volume_slider.pack(side="right", pady=0, padx=0)

    sf_2 = CTkFrame(master=sliders_frame, fg_color=color_soft_beige)
    sf_2.pack(fill="x", padx=0, pady=0)

    CTkLabel(master=sf_2, font=font, text_color=color_dark_charcoal, width=70,
             text="Shuffle").pack(side="left", pady=0, padx=0)
    shuffle_slider = CTkSlider(master=sf_2, orientation="horizontal", from_=0, to=1, command=shuffle_update,
                              fg_color=color_dark_charcoal, progress_color=color_dark_charcoal,
                              button_color=color_golden_yellow, hover=False, width=150, border_width=0)
    shuffle_slider.set(0)
    shuffle_slider.pack(side="right", pady=0, padx=0)

    end_check(ctk)
    ctk.mainloop()


if __name__ == "__main__":
    gui_startup()
