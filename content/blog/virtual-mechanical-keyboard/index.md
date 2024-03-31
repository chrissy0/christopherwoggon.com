+++
title = "Virtual Mechanical Keyboard: Make your keyboard sound like a mechanical keyboard"
date = "2023-04-05"
+++

Lately I’ve been looking into mechanical keyboards. As I spend most of my time in front of a screen, I thought – “why not invest a little to make the process more fun?”

After days down the mechanical keyboards subreddit rabbit hole I came close to ordering one for myself, but I ended up opting for the Apple Magic Keyboard instead. I like the portability and also needed something which I could use silently in a public setting.

But today, I found myself missing a little audio feedback for my keypresses. That’s when it hit me – why not just simulate the audio? No need for it to come from actual key presses.

So I hacked together a tiny Python script in 5 minutes - and it works like a charm.

```python
from playsound import playsound
from pynput.keyboard import Key, Listener
import threading


def play_press():
    playsound("mechanical.mp3")


def on_press(_):
    t = threading.Thread(target=play_press)
    t.start()


with Listener(on_press=on_press) as listener:
    listener.join()
```

Yep, that’s all.

I’m using `pynput` to listen for key presses, then start a new thread upon key presses which plays the sound of a mechanical keyboard button press. The file `mechanical.mp3` needs to be in the same directory as the Python script.

While it works without starting new threads, the script waits for the sound to finish playing. For fast typists, this leads to congestion and further key presses being played after the last key is pressed.

This is the sound file I’m using for key presses:
{{ audio(path="mechanical.mp3") }}

I also played with the sound of a key release upon release, but I like it better with just the down press. If you’re interested in the key releases as well, adjust the code snippet like this:

```python
from playsound import playsound
from pynput.keyboard import Key, Listener
import threading

def play_press():
    playsound("mechanical_press.mp3")

def play_release():
    playsound("mechanical_release.mp3")

def on_press(_):
    t = threading.Thread(target=play_press)
    t.start()

def on_release(_):
    t = threading.Thread(target=play_release)
    t.start()

with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
```

That’s all!