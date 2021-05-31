import tkinter as tk
root = tk.Tk()
var = tk.IntVar()
button = tk.Button(root, text="Click Me", command=lambda: var.set(1))
button.place(relx=.5, rely=.5, anchor="c")

for i in range(0,10):
    print("waiting...")
    button.wait_variable(var)
    print("done waiting.")

