import re
import sys
import tkinter as tk
from tkinter import Label, Button, Text, CENTER, INSERT, END
import pandas as pd


class Main(tk.Frame):

    # Initialize the screen
    def __init__(self, master, taxonomy_dict, types_dict, test_flag):
        self.master = master
        self.master.title("RISC-V Simulator")
        self.master.geometry('600x650')
        self.master.config(bg = 'black')
        self.test = test_flag # Boolean for testing outputs
        self.edit_text = None
        self.terminal_text = None
        self.opcode_legend_dict = types_dict
        self.taxonomy_dict = taxonomy_dict
        self.binary_table_df = pd.DataFrame(columns=['instruction', '32-25', '24-20', '19-15', '14-12', '11-7', '6-0'])
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

        sample_input = """add x12, x13, x3
"""
# .data
# var_1       :     .word 0x11213
# var_2       :     .word 876
# var_2       :     .word -876
# .text
# lw x12, 0(x12)
# addi x12, x13, 0x8
# addi x12, x13, 1231
# bge x1, x2, jump1
# jump1:

        self.edit_text.insert(1.0, sample_input)
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

    def parse_instruction(self, instruction, matched_string):
        def r_type():
            # op code
            six_to_zero = 0b0110011
            # rd
            eleven_to_seven = matched_string[0]
            # funct3
            fourteen_to_twelve = taxonomy_details['14-12']
            # rs1
            nineteen_to_fifteen = matched_string[1]
            # rs2
            twentyfour_to_twenty = matched_string[2]
            # funct7
            thirtytwo_to_twentyfive = taxonomy_details['32-25']

            row_to_return = {
                '32-25': thirtytwo_to_twentyfive,
                '24-20': twentyfour_to_twenty,
                '19-15': nineteen_to_fifteen,
                '14-12': fourteen_to_twelve,
                '11-7': eleven_to_seven,
                '6-0': six_to_zero
            }

            return row_to_return

        # def i_type():
        #
        # for key, taxonomy in self.taxonomy_dict.items():
        #     match_regex = re.match(taxonomy['regex'], formatted_instruction)
        #
        #     type = taxonomy['type']



        taxonomy_details = taxonomy_dict[instruction]

        row_to_return = r_type()

        # Cast to binary
        row_to_return = {key: bin(int(value)) for key, value in row_to_return.items()}

        row_to_return['instruction'] = instruction

        return row_to_return





    # Gets the string from the edit text box
    def evaluate(self):
        parsing_passed = True
        string_to_eval = self.edit_text.get("1.0", "end")
        list_of_commands = string_to_eval.splitlines()

        #For testing
        results = []



        for command in list_of_commands:
        # for key, value in a_dict.items():
            formatted_command = command.lower().strip()

            if formatted_command == '': continue # Skip if empty line

            for key, taxonomy in taxonomy_dict.items():
                print(taxonomy['regex'])
                match_regex = re.match(taxonomy['regex'], formatted_command)

                print(match_regex.groups())
                type = taxonomy['type']

                row_to_add = self.parse_instruction(key, match_regex.groups())

                # type_details = types_dict[type]
                #
                # # opcode / static for all types
                # six_to_zero = type_details['6-0']
                #
                # if type in ['r-type', 'i-type']:
                #     # rd
                #     eleven_to_seven_details = type_details["11-7"]
                #     eleven_to_seven = bin(int(match_regex[eleven_to_seven_details['regex_index']]))[2:].zfill(4)
                #
                #     # rs1
                #     nineteen_to_fifteen = bin(int(match_regex[type_details["19-15"]]))[2:].zfill(5)
                #     if type == 'r-type':
                #         # rs2
                #         twentyfour_to_twenty = bin(int(match_regex[type_details["24-20"]]))[2:].zfill(4)
                #         thirtytwo_to_twentyfive = bin(taxonomy['32-25'])[2:].zfill(8)
                #         print("rs2")
                #
                #     if type == 'i-type':
                #         # immediate
                #         thirtytwo_to_twenty = bin(int(match_regex[type_details["32-20"]]))[2:].zfill(12)
                #         twentyfour_to_twenty = thirtytwo_to_twenty[5:12]
                #         thirtytwo_to_twentyfive = thirtytwo_to_twenty[0:5]
                #
                #
                # fourteen_to_twelve = bin(taxonomy['14-12'])[2:].zfill(8)
                #
                #
                # row_to_add = {
                #     'command': key,
                #     '32-25': thirtytwo_to_twentyfive,
                #     '24-20': twentyfour_to_twenty,
                #     '19-15': nineteen_to_fifteen,
                #     '14-12': fourteen_to_twelve,
                #     '11-7': eleven_to_seven,
                #     '6-0': six_to_zero
                # }


                print(row_to_add)

                self.binary_table_df = self.binary_table_df.append(row_to_add, ignore_index=True)
                if match_regex: break



            if not self.test:
                results = 'Success!'
                if not match_regex:
                    parsing_passed = False
                    results = 'Fail!'
                    break
            else:
                if match_regex:
                    output_string = f'[{formatted_command}] : {match_regex.groups()}\n'
                    print(match_regex.groups())

                else:
                    output_string = f'[{formatted_command}] : Failed\n'

                results.append(output_string)

        if parsing_passed:
            self.print_in_terminal(results)
            print(list_of_commands)
            print(self.binary_table_df)



if __name__ == "__main__":

    reserved_words = r'^$'

    # register = [<regex>]

    # Bawal to, check if it passes
    # add x6, x6, x8



    # regex_lib = [
    #     # reserved word
    #     r'^.(data)$',
    #     # reserved word
    #     r'^.(text)$',
    #     # variable declaration
    #     r'^([a-z_][\w]*)[\s]*:[\s]*(.word)[\s]+([-+]?0|[-+]?[1-9]+|0x[a-f0-9]+)$',
    #     # jump declaration
    #     r'^([a-z_][\w]*)[\s]*:$',
    #     # load / store
    #     r'^(lw|sw)[\s]+x(0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*([\d]*)\(x(0?[1-9]|[12][0-9]|3[01])\)$',
    #     # integer computation
    #     r'^(add|slt|sll|srl|and|or|xor)[\s]+x(0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*x(0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*x(0?[1-9]|[12][0-9]|3[01])$',
    #     # integer computation (immediate)
    #     r'^(addi|slti|slli|srli|andi|ori|xori)[\s]+x(0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*x(0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*([-+]?0|[-+]?[1-9]+|0x[a-f0-9]+)$',
    #     # control transfer (branching)
    #     r'^(beq|bnq|blt|bge)[\s]+x(0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*x(0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*([a-z_][\w]*)$'
    # ]

    regex_integer_computation = "[\s]+x(0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*x(0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*x(0?[1-9]|[12][0-9]|3[01])$"
    regex_integer_computation_immediate = "[\s]+x(0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*x(0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*([-+]?0|[-+]?[1-9]+|0x[a-f0-9]+)$"


    types_dict = {
        # 'i-type': 0b0010011, #immediate
        'r-type': {
            "6-0": 0b0110011,
            "11-7": {
                "regex_index": 0,
            },
            '19-15': {
                "regex_index": 1,
            },
            '24-20': {
                "regex_index": 2,
            },
        },
        # immediate
        'i-type': {
            "6-0": 0b0010011,
            "11-7": {
                "regex_index": 0,
            },
            '19-15': {
                "regex_index": 1,
            },
            '32-20': {
                "regex_index": 2,
            }
        }
        # 's-type': 0b0100011, #store
        # 'b-type': 0b1100011, #branch
        # 'j-type': 0b1101111, #jump
    }


    taxonomy_dict = {
        "add": {
            "regex": f"^add{regex_integer_computation}",
            "type": 'r-type',
            '14-12': 0b000,
            '32-25': 0b000000
        },
        "addi": {
            "regex": f"^addi{regex_integer_computation_immediate}",
            "type": 'i-type',
            '14-12': 0b000
        }
    }


    root = tk.Tk()
    app = Main(root, taxonomy_dict, types_dict, True)
    root.mainloop()


    # Test data
    # .data
    # .main
    # lw x3,  0(x3)
    # add x4, x6, x3