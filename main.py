from pygame import mixer, event
from tkinter import *
from tkinter import filedialog
import os

# todo additional window with stuff like volume or position (to make program consume less resources)
# event.set_allowed()
volume: float
volume_slider: Scale
position_slider: Scale
paused: bool = False
play_button: Button
music_queue: list[str] = []
current_song_index: int = 0
music_listbox: Listbox


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

    music_directory = filedialog.askdirectory()
    if not music_directory:
        return

    for root, _, files in os.walk(music_directory):
        for file in files:
            if file.endswith(".mp3"):
                music_queue.append(os.path.join(root, file))
                music_listbox.insert(END, file[:-4])


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
                play_button.config(text="Pause")
                return
            elif not paused and mixer.music.get_busy():
                paused = True
                mixer.music.pause()
                play_button.config(text="Play")
                return
        case "listbox":
            current_song_index = music_listbox.curselection()[0]
        case "next":
            current_song_index = (current_song_index + 1) % len(music_queue)
        case "prev":
            current_song_index = current_song_index - 1 if current_song_index > 0 else len(music_queue) - 1

    paused = False
    play_button.config(text="Pause")
    song = music_queue[current_song_index]
    mixer.music.load(song)
    mixer.music.play()


if __name__ == "__main__":
    tk = Tk()
    mixer.init()
    tk.geometry("300x720")

    Button(master=tk, text="Load Songs", command=load_songs).pack()
    volume_slider = Scale(master=tk, orient=HORIZONTAL, from_=0, to=100, command=volume_update)
    volume_slider.set(100)
    volume_slider.pack()

    position_slider = Scale(master=tk, orient=HORIZONTAL, from_=0, to=1000)
    position_slider.bind("<ButtonRelease-1>", position_update)
    position_slider.pack()

    play_button = Button(master=tk, text="Play", command=play)
    play_button.pack()

    Button(master=tk, text="Next", command=lambda: play("next")).pack()
    Button(master=tk, text="Previous", command=lambda: play("prev")).pack()

    music_listbox = Listbox(master=tk, activestyle="dotbox")
    music_listbox.bind("<Double-Button-1>", lambda _: play("listbox"))
    music_listbox.pack()

    Button(tk, text="TEST EVENTS", command=event.get)

    mainloop()
