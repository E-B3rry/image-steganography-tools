from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk


def frames(x: tk.Tk):
    """Cette fonction donne aux fenêtres des frames pour positionner les éléments.
    :x est une fenêtre Tkinter,
    :big_big_title et btn sont des booléens."""
    global frame1, frame2, frame3, frame4, frame5, frame6, frame7

    frame1 = tk.Frame(x, width=300, height=50)
    frame1.grid(row=0, column=0, columnspan=1)

    frame2 = tk.Frame(x, width=300, height=50)
    frame2.grid(row=2, column=0)

    frame3 = tk.Frame(x, width=300, height=50)
    frame3.grid(row=3, column=0)

    frame4 = tk.Frame(x, width=300, height=50)
    frame4.grid(row=4, column=0)

    frame5 = tk.Frame(x, width=300, height=50)
    frame5.grid(row=5, column=0)

    frame6 = tk.Frame(x, width=300, height=50)
    frame6.grid(row=6, column=0)

    frame7 = tk.Frame(x, width=300, height=50)
    frame7.grid(row=7, column=0)


def code_fen():
    """Cette fonction permet d'ouvrir la fenêtre principale.
    :current est un dictionnaire,
    :buttons est un booléen."""
    Main_Fen = tk.Tk()
    Main_Fen.geometry("800x600")
    Main_Fen.resizable(False, False)
    Main_Fen.title("Codator 3000 v1.0.0a")
    # Main_Fen.iconbitmap(logo)

    frames(Main_Fen)
    phrase = tk.StringVar()

    label1 = tk.Label(frame1, justify="center", text="Codator 3000", font=("Comic sans MS", 35), fg='red')
    label1.grid(pady=10, padx='250')
    label2 = tk.Label(frame2, justify="center", text="Entrez une phrase à coder:", font=("Comic sans MS", 20), fg='blue')
    label2.grid(pady=10, padx='200')

    txt = tk.Entry(frame3, textvariable=phrase)
    txt.focus_set()
    txt.grid(pady=10)
    menu = ttk.Combobox(frame3, values=["1", "2", "3"])
    menu.grid(row=2, pady=10, padx='200')
    bouton1 = tk.Button(frame4, text="Coder", font=("Burbank Big Cd bd", 16), fg='Orange', cursor='heart')
    bouton1.grid()
    bouton2 = tk.Button(frame5, text="Décoder une image", font=("Burbank Big Cd bd", 16), fg='Orange', cursor='heart',
                        command=lambda: change_fen(decode_fen, Main_Fen))
    bouton2.grid(pady=10)

    Main_Fen.mainloop()


def decode_fen():
    """Cette fonction permet d'ouvrir la fenêtre principale.
    :current est un dictionnaire,
    :buttons est un booléen."""

    Main_Fen = tk.Tk()
    Main_Fen.geometry("800x600")
    Main_Fen.resizable(False, False)
    Main_Fen.title("Codator 3000 v1.0.0a")
    # Main_Fen.iconbitmap(logo)

    frames(Main_Fen)
    phrase = tk.StringVar()

    label1 = tk.Label(frame1, justify="center", text="Codator 3000", font=("Comic sans MS", 35), fg='red')
    label1.grid(pady=10, padx='250')
    label2 = tk.Label(frame2, justify="center", text="Sélectionnez une image à décoder:", font=("Comic sans MS", 20), fg='blue')
    label2.grid(pady=10, padx='180')

    txt = tk.Entry(frame3, )
    txt.focus_set()
    txt.pack(pady=10)
    bouton1 = tk.Button(frame4, text="Décoder", font=("Burbank Big Cd bd", 16), fg='Orange', cursor='heart')
    bouton1.grid()
    bouton2 = tk.Button(frame5, text="Décoder une image", font=("Burbank Big Cd bd", 16), fg='Orange', cursor='heart',
                        command=lambda: change_fen(code_fen, Main_Fen))
    bouton2.grid(pady=10)

    Main_Fen.mainloop()


def change_fen(new: callable, current: tk.Tk) -> None:
    current.destroy()
    new()


if __name__ == "__main__":
    code_fen()
