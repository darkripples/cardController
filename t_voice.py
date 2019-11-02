# coding:utf8

import win32com.client as win, sys

def main(msg):
    speak = win.Dispatch("SAPI.SpVoice")
    speak.Speak("你好")

if __name__ == "__main__":
    main(sys.argv[1])
