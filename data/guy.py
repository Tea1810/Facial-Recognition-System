import tkinter as tk
from src.videostream import VideoStream


if __name__ == '__main__':
    # Tkinter window
    root_window = tk.Tk()

    # Window settings
    root_window.title('Face Recognition')
    root_window.geometry('500x540')
    root_window.configure(background='#353535')

    # Panel for webcam visualization
    panel = tk.Label(root_window)
    panel.pack(side='top', fill='none')


    # Webcam stream init
    vs = VideoStream(panel=panel)
    vs.stream()

    # Main loop
    root_window.mainloop()