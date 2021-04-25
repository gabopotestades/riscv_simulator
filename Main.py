import re
import sys
import tkinter as tk
from tkinter import Label, Button, Text, CENTER, INSERT, END
import pandas as pd


class Main(tk.Frame):

    # Initialize the screen
    def __init__(self, master, commands_dict, reserved_list, test_flag):
        self.master = master
        self.master.title("RISC-V Simulator")
        self.master.geometry('600x650')
        self.master.config(bg = 'black')
        self.test = test_flag # Boolean for testing outputs
        self.edit_text = None
        self.terminal_text = None
        self.commands_dict = commands_dict
        self.reserved_list = reserved_list
        self.binary_table_df = None
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

        # Sample input for r-type
        sample_input = """add x0, x1, x2
and x3, x4, x5
or x6, x7, x8
xor x9, x10, x11
slt x12, x13, x14
srl x15, x16, x17
sll x18, x19, x20
"""

        # Sample input for i-type
#         sample_input = """addi x0, x1, 0x2
# slti x3, x4, 0x5
# slli x6, x7, 2323
# srli x9, x10, 34543
# andi x12, x13, 0xfff
# ori x15, x22, 234
# xori x31, x19, 0xabcdef
# """

# Sample input for s-type
#         sample_input = """sw x0, (x02)
# sw x0, 0(x12)
# lw x2, 3(x31)
# """

       # Sample input for sb-type
#         sample_input = """beq x0, x02, jumper
#  bne x0, x02, _test
#  blt x31, x11, _12312
#  bge x12, x22, a23524
#  """

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
    
    # Pad binary digits
    def print_formatted_table(self):
        self.binary_table_df['31-25'] = self.binary_table_df['31-25'].apply(lambda x: x[2:].zfill(7)[::-1][0:8][::-1])
        self.binary_table_df['24-20'] = self.binary_table_df['24-20'].apply(lambda x: x[2:].zfill(5)[::-1][0:5][::-1])
        self.binary_table_df['19-15'] = self.binary_table_df['19-15'].apply(lambda x: x[2:].zfill(5)[::-1][0:5][::-1])
        self.binary_table_df['14-12'] = self.binary_table_df['14-12'].apply(lambda x: x[2:].zfill(3)[::-1][0:3][::-1])
        self.binary_table_df['11-7'] = self.binary_table_df['11-7'].apply(lambda x: x[2:].zfill(5)[::-1][0:5][::-1])
        self.binary_table_df['6-0'] = self.binary_table_df['6-0'].apply(lambda x: x[2:].zfill(7)[::-1][0:7][::-1])
        print(self.binary_table_df)

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

    def parse_instruction(self, instruction, matched_string, is_command):

        if is_command:

            def r_type():
                # op code
                six_to_zero = 51
                # rd
                eleven_to_seven = matched_string[1]
                # funct3
                fourteen_to_twelve = taxonomy_details['14-12']
                # rs1
                nineteen_to_fifteen = matched_string[2]
                # rs2
                twentyfour_to_twenty = matched_string[3]
                # funct7
                thirtyone_to_twentyfive = taxonomy_details['31-25']

                row_to_return = {
                    '31-25': thirtyone_to_twentyfive,
                    '24-20': twentyfour_to_twenty,
                    '19-15': nineteen_to_fifteen,
                    '14-12': fourteen_to_twelve,
                    '11-7': eleven_to_seven,
                    '6-0': six_to_zero
                }

                return row_to_return

            def i_type():
                # op code
                six_to_zero = 19
                # rd
                eleven_to_seven = matched_string[1]
                # funct3
                fourteen_to_twelve = taxonomy_details['14-12']
                # rs1
                nineteen_to_fifteen = matched_string[2]

                # immediate
                thirtyone_to_twenty = matched_string[3]

                # parse hex (there should be another rule for non hex
                thirtyone_to_twenty = bin(int(thirtyone_to_twenty, 16))

                # pad to 12 bits
                thirtyone_to_twenty = thirtyone_to_twenty[2:].zfill(12)
                thirtyone_to_twenty = thirtyone_to_twenty[-12:len(thirtyone_to_twenty)]
                
                # print(f"hex received: {thirtyone_to_twenty} in int: {int(thirtyone_to_twenty, 16)} in raw: {matched_string[3]}")

                # convert to binary
                twentyfour_to_twenty = bin(int(f"0b{thirtyone_to_twenty[7:12]}", 2))
                thirtyone_to_twentyfive = bin(int(f"0b{thirtyone_to_twenty[0:7]}", 2))

                # convert to integer
                twentyfour_to_twenty = int(twentyfour_to_twenty, 2)
                thirtyone_to_twentyfive = int(thirtyone_to_twentyfive, 2)

                # print(f"first: {twentyfour_to_twenty}, second: {thirtyone_to_twentyfive}")

                row_to_return = {
                    '31-25': thirtyone_to_twentyfive,
                    '24-20': twentyfour_to_twenty,
                    '19-15': nineteen_to_fifteen,
                    '14-12': fourteen_to_twelve,
                    '11-7': eleven_to_seven,
                    '6-0': six_to_zero
                }

                return row_to_return
            
            def s_type():
                # op code
                six_to_zero = taxonomy_details['6-0']
                # rd
                eleven_to_seven = 0
                # funct3
                fourteen_to_twelve = taxonomy_details['14-12']
                # rs1
                nineteen_to_fifteen = matched_string[1]
                # rs2
                twentyfour_to_twenty = 0
                # funct7
                thirtyone_to_twentyfive = 0

                row_to_return = {
                    '31-25': thirtyone_to_twentyfive,
                    '24-20': twentyfour_to_twenty,
                    '19-15': nineteen_to_fifteen,
                    '14-12': fourteen_to_twelve,
                    '11-7': eleven_to_seven,
                    '6-0': six_to_zero
                }

                return row_to_return

            def sb_type():
                # op code
                six_to_zero = 63
                # rd
                eleven_to_seven = 0
                # funct3
                fourteen_to_twelve = taxonomy_details['14-12']
                # rs1
                nineteen_to_fifteen = matched_string[1]
                # rs2
                twentyfour_to_twenty = 0
                # funct7
                thirtyone_to_twentyfive = 0

                row_to_return = {
                    '31-25': thirtyone_to_twentyfive,
                    '24-20': twentyfour_to_twenty,
                    '19-15': nineteen_to_fifteen,
                    '14-12': fourteen_to_twelve,
                    '11-7': eleven_to_seven,
                    '6-0': six_to_zero
                }

                return row_to_return

            taxonomy_details = self.commands_dict[instruction]

            if taxonomy_details['type'] == 'r-type':
                row_to_return = r_type()
            elif taxonomy_details['type'] == 'i-type':
                row_to_return = i_type()
            elif taxonomy_details['type'] == 's-type':
                row_to_return = s_type()
            elif taxonomy_details['type'] == 'sb-type':
                row_to_return = sb_type()

            # Cast to binary
            row_to_return = {key: bin(int(value)) for key, value in row_to_return.items()}

            row_to_return['instruction'] = instruction

            return row_to_return
        
        elif not is_command:

            pass


    # Gets the string from the edit text box
    def evaluate(self):
        parsing_passed = True

        string_to_eval = self.edit_text.get("1.0", "end")
        list_of_commands = string_to_eval.splitlines()
        self.binary_table_df = pd.DataFrame(columns=['instruction', '31-25', '24-20', '19-15', '14-12', '11-7', '6-0'])

        #For testing
        results = []

        for command in list_of_commands:
            match_found = False
            formatted_command = command.lower().strip()

            if formatted_command == '': continue # Skip if empty line

            # print(f"Command to match regex: {command}")
            for key, command in self.commands_dict.items():
                match_regex = re.match(command['regex'], formatted_command)

                if match_regex:
                    row_to_add = self.parse_instruction(key, match_regex.groups(), True)
                    self.binary_table_df = self.binary_table_df.append(row_to_add, ignore_index=True)
                    match_found = True
                    # print("Row to add")
                    # print(row_to_add)
                    break

            if not match_found:
                
                for regex in reserved_list:
                    match_regex = re.match(regex, formatted_command)

                    if match_regex:
                        row_to_add = self.parse_instruction(match_regex[0], match_regex.groups(), False)
                        break
            
            if not self.test:
                results = 'Success!'
                if not match_regex:
                    parsing_passed = False
                    results = 'Fail!'
                    break
            else:
                if match_regex:
                    output_string = f'[{formatted_command}] : {match_regex.groups()}\n'
                    # print(match_regex.groups())

                else:
                    output_string = f'[{formatted_command}] : Failed\n'

                results.append(output_string)

        if parsing_passed:
            self.print_in_terminal(results)
            # print(self.binary_table_df)
            self.print_formatted_table()



if __name__ == "__main__":

    reserved_words = r'^$'

    # register = [<regex>]

    # Bawal to, check if it passes
    # add x6, x6, x8

    reserved_list = [
        # reserved word
        r'^.(data)$',
        # reserved word
        r'^.(text)$',
        # variable declaration
        r'^([a-z_][\w]*)[\s]*:[\s]*(.word)[\s]+([-+]?0|[-+]?[1-9]+|0x[a-f0-9]+)$',
        # jump declaration
        r'^([a-z_][\w]*)[\s]*:$'
    ]

    regex_store_instruction = r"[\s]+x(0|0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*([\d]*)\(x(0|0?[1-9]|[12][0-9]|3[01])\)$"
    regex_integer_computation = r"[\s]+x(0|0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*x(0|0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*x(0|0?[1-9]|[12][0-9]|3[01])$"
    regex_integer_computation_immediate = r"[\s]+x(0|0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*x(0|0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*([-+]?0|[-+]?[1-9]+|0x[a-f0-9]+)$"
    regex_branching_instruction = r"[\s]+x(0|0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*x(0|0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*([a-z_][\w]*)$"

    commands_dict = {
        # Register to Memory
        "lw": {
            "regex": f"^(lw){regex_store_instruction}",
            "type": 's-type',
            '14-12': 0b010,
            '6-0': 3
        },
        "sw": {
            "regex": f"^(sw){regex_store_instruction}",
            "type": 's-type',
            '14-12': 0b010,
            '6-0': 35
        },
        # Register to register
        "add": {
            "regex": f"^(add){regex_integer_computation}",
            "type": 'r-type',
            '14-12': 0b000,
            '31-25': 0b0000000
        },
        "sll": {
            "regex": f"^(sll){regex_integer_computation}",
            "type": 'r-type',
            '14-12': 0b001,
            '31-25': 0b0000000
        },
        "slt": {
            "regex": f"^(slt){regex_integer_computation}",
            "type": 'r-type',
            '14-12': 0b010,
            '31-25': 0b0000000
        },
        "srl": {
            "regex": f"^(srl){regex_integer_computation}",
            "type": 'r-type',
            '14-12': 0b101,
            '31-25': 0b0000000
        },
        "and": {
            "regex": f"^(and){regex_integer_computation}",
            "type": 'r-type',
            '14-12': 0b111,
            '31-25': 0b0000000
        },
        "or": {
            "regex": f"^(or){regex_integer_computation}",
            "type": 'r-type',
            '14-12': 0b110,
            '31-25': 0b0000000
        },
        "xor": {
            "regex": f"^(xor){regex_integer_computation}",
            "type": 'r-type',
            '14-12': 0b100,
            '31-25': 0b0000000
        },
        # Register to Immediate
        "addi": {
            "regex": f"^(addi){regex_integer_computation_immediate}",
            "type": 'i-type',
            '14-12': 0b000
        },
        "slti": {
            "regex": f"^(slti){regex_integer_computation_immediate}",
            "type": 'i-type',
            '14-12': 0b010
        },
        "andi": {
            "regex": f"^(andi){regex_integer_computation_immediate}",
            "type": 'i-type',
            '14-12': 0b111
        },
        "ori": {
            "regex": f"^(ori){regex_integer_computation_immediate}",
            "type": 'i-type',
            '14-12': 0b110
        },
        "xori": {
            "regex": f"^(xori){regex_integer_computation_immediate}",
            "type": 'i-type',
            '14-12': 0b100
        },
        "slli": {
            "regex": f"^(slli){regex_integer_computation_immediate}",
            "type": 'i-type',
            '14-12': 0b001
        },
        "srli": {
            "regex": f"^(srli){regex_integer_computation_immediate}",
            "type": 'i-type',
            '14-12': 0b101
        },
        # Branching,
        "beq": {
            "regex": f"^(beq){regex_branching_instruction}",
            "type": 'sb-type',
            '14-12': 0b000
        },
        "bne": {
            "regex": f"^(bne){regex_branching_instruction}",
            "type": 'sb-type',
            '14-12': 0b001
        },
        "blt": {
            "regex": f"^(blt){regex_branching_instruction}",
            "type": 'sb-type',
            '14-12': 0b100
        },
        "bge": {
            "regex": f"^(bge){regex_branching_instruction}",
            "type": 'sb-type',
            '14-12': 0b101
        }
    }


    root = tk.Tk()
    app = Main(root, commands_dict, reserved_list, True)
    root.mainloop()


    # Test data
    # .data
    # .main
    # lw x3,  0(x3)
    # add x4, x6, x3
