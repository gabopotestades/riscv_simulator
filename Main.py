import re
import sys
import tkinter as tk
from tkinter import Label, Button, Text, CENTER, INSERT, END

class Main(tk.Frame):

    # Initialize the screen
    def __init__(self, master, regex_lib, test_flag):
        self.master = master
        self.master.title("RISC-V Simulator")
        self.master.geometry('500x650')
        self.master.config(bg = 'black')
        self.test = test_flag # Boolean for testing outputs
        self.regex_lib = regex_lib
        self.edit_text = None
        self.terminal_text = None
        self.create_widgets()

    # Create the objects in the screen
    def create_widgets(self):
        menu_evaluate = Button(self.master, text="Execute", command=self.evaluate, bg="lightgreen", fg="black")
        menu_evaluate.pack(fill="x")

        step_one_label = Label(self.master, text="EDIT",  background="grey", foreground="white")
        step_one_label.config(anchor=CENTER)
        step_one_label.pack(fill="x")

        self.edit_text = Text(self.master, background="black", foreground="white", insertbackground='white', height=30)
        self.edit_text.pack(fill="x")

        step_three_label = Label(self.master, text="MESSAGE",  background="grey", foreground="white")
        step_three_label.config(anchor=CENTER)
        step_three_label.pack(fill="x")

        self.terminal_text = Text(self.master, background="black", foreground="green", height=10)
        self.terminal_text.config()
        self.terminal_text.pack(fill="x")

    # Outputs to terminal the processed data
    def print_in_terminal(self, inputStr):

        # Enabled the terminal to insert text and disable again to make it readonly
        if not self.test:
            self.terminal_text.config(state="normal")
            self.terminal_text.delete("1.0", END)
            self.terminal_text.insert(INSERT, inputStr)
            self.terminal_text.see("end")
            self.terminal_text.config(state="disabled")
        else:
            self.terminal_text.config(state="normal")
            self.terminal_text.delete("1.0", END)

            for result in inputStr:
                self.terminal_text.insert(INSERT, result)

            self.terminal_text.see("end")
            self.terminal_text.config(state="disabled")

    # Gets the string from the edit text box
    def evaluate(self):
        parsing_passed = True
        string_to_eval = self.edit_text.get("1.0", "end")
        list_of_commands = string_to_eval.splitlines()

        #For testing
        string_checker = None    
        results = []

        for command in list_of_commands:
            formatted_command = command.lower().strip()

            if formatted_command == '': continue # Skip if empty line

            if not self.test:
                results = 'Success!'
                if not re.match(self.regex_lib, formatted_command):
                    parsing_passed = False
                    results = 'Fail!'
                    break
                    
            else:          
                if not re.match(self.regex_lib, formatted_command):
                    string_checker = 'failed'
                else:
                    string_checker = 'passed'
            
                output_string = f'[{formatted_command}] : {string_checker}\n'

                results.append(output_string)

        if parsing_passed:
            self.print_in_terminal(results)
        

if __name__ == "__main__":

    regex_lib = [
        r'^#data$',
        r'^#main$',
        r'^(lw)[\s *]()$'
    ]
    
    regex_lib = '(' + ')|('.join(regex_lib) + ')'

    root = tk.Tk()
    app = Main(root, regex_lib, True)
    root.mainloop()