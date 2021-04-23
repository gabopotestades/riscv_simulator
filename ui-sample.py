from tkinter import *
from tkinter.filedialog import askopenfilename
import re


def show_visualization(inputStr):
    simulation_text.insert(INSERT, inputStr)


def evaluate():
    # function to be trigged when program is executed / button to execute is pressed

    # trick to assign the prints to a text area
    sys.stdout.write = show_visualization


def do_evaluation():

    # get the input from user, sample here is from 2 input fields from user
    # modules_string = manual_input_modules_text.get(1.0, END)
    # omega_string = manual_input_omega_text.get(1.0, END)

    # do the actual evaluation
    evaluate()



window = Tk()
window.title("Turing Modules by Glenn Matias")

step_one_label = Label(window, text="STEP 1: INPUT MODULES",  background="grey", foreground="white")
step_one_label.config(anchor=CENTER)
step_one_label.pack(fill="x")


manual_input_text = Text(window, background="white", foreground="black", height=10)
sample_input = """1]shr-2
2]copy-2
3]copy-2
4]shl-2
5]ifeq(26)
6]copy-2
7]copy-2
8]shl-2
9]ifgt(17)
10]copy-1
11]copy-3
12]shl-2
13]monus
14]move-1-1
15]shl-1
16]goto(1)
17]copy-2
18]copy-2
19]shl-2
20]monus
21]shr-1
22]copy-2
23]shl-2
24]move-2-2
25]goto(1)
26]copy-2
27]shl-1
28]move-2-1
29]halt"""




Label(window, text="", background="black").pack(fill="x")

step_two_label = Label(window, text="STEP 2: INPUT OMEGA",  background="grey", foreground="white")
step_two_label.config(anchor=CENTER)
step_two_label.pack(fill="x")

manual_input_omega_text = Text(window, background="white", foreground="black", height=1)
manual_input_omega_text.pack(fill="x")

menu_evaluate = Button(window, text="Click to Evaluate", command=do_evaluation, bg="green", fg="blue")
menu_evaluate.pack(fill="x")

Label(window, text="", background="black").pack(fill="x")


step_three_label = Label(window, text="STEP 3: SIMULATION",  background="grey", foreground="white")
step_three_label.config(anchor=CENTER)
step_three_label.pack(fill="x")

simulation_text = Text(window, background="black", foreground="green", height=40)
simulation_text.pack(fill="x")

window.geometry('500x900')
window.configure(background='black')

mainloop()