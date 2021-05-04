import re
import sys
import tkinter as tk
from tkinter import Label, Button, Text, CENTER, INSERT, END
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

class Main(tk.Frame):

    # Initialize the screen
    def __init__(self, master, commands_dict, reserved_list, test_flag):
        self.master = master
        self.master.title("RISC-V Simulator")
        self.master.geometry('600x650')
        self.master.config(bg = 'black')
        self.test = test_flag # Boolean for testing outputs
        self.is_data = False
        self.is_text = False
        self.line_counter = 1

        self.edit_text = None
        self.terminal_text = None

        self.commands_dict = commands_dict
        self.reserved_list = reserved_list

        self.variables = {}
        self.jump_instructions = {}

        self.current_data_segment = None
        self.current_text_segment = None

        self.binary_table_df = None
        self.create_widgets()


    # Create the objects in the screen
    def create_widgets(self):
        menu_evaluate = Button(self.master, text="Assemble", command=self.evaluate, bg="lightgreen", fg="black")
        menu_evaluate.pack(fill="x")

        step_one_label = Label(self.master, text="INSTRUCTIONS",  background="grey", foreground="white")
        step_one_label.config(anchor=CENTER)
        step_one_label.pack(fill="x")

        self.edit_text = Text(self.master, background="black", foreground="white", insertbackground='white', height=30)
        self.edit_text.pack(fill="x")

        # Sample input for reserved words
#         sample_input = """.data
# var1: .word 0x0f
# var2: .word 2
# var3: .word 0x08

# .text
# jump:

# """

        # Sample input for r-type
#         sample_input = """.text
# add x0, x1, x2
# and x3, x4, x5
# or x6, x7, x8
# xor x9, x10, x11
# slt x12, x13, x14
# srl x15, x16, x17
# sll x18, x19, x20
# """

        # Sample input for i-type
#         sample_input = """.text
# addi x0, x1, 0x2
# slti x3, x4, 0x5
# slli x6, x7, 4
# srli x9, x10, 34543
# andi x12, x13, 0xfff
# ori x15, x22, 234
# xori x31, x19, 0xabcdef
# """

        # Sample input for s-type
#         sample_input = """.text
# lw x6, 0(x8)
# sw x10, (x9)
# """


        # Sample input for sb-type
#         sample_input = """.data
# var1: .word 1
# .text
# lw x9, var1
# lw x10, var2
# beq x9, x10, jumper
# jumper:
# lw x0, var1
# .data
# var2: .word 2
#         """


#         sample_input =  """.data
# var1: .word 0x0f
# var2: .word 15
# .text
# addi x3, x31, 0x0ff
# addi x3, x4, 0x0ff
# addi x3, x5, 255
# beq x0, x02, jumper
# lw x1, +15
# lw x1, var1
# lw x1, 0(x15)
# lw x1, -15(x0)
# lw x1, 0xf
# lw x6, var5
# jumper:
# lw x1, -2
# sw x1, -2
# sw x2, var2
# sw x3, 0xc
# .data
# var4: .word 33
# var5: .word 0x21
# .text
# add x3, x4, x7
# addi x6, x23, -2
# slti x3, x4, 0x5
# """

        sample_input =  """
.data
.text
addi x5, x0, 8
addi x6, x0, 4
BLT x5, x6, L1
xor x7, x5, x6
and x8, x5, x6
beq x0, x0, FIN
L1: 
sll x7, x5, x6
srl x8, x5, x6
FIN: 
addi x0, x0, 0
sw x2, var2
"""
        self.edit_text.insert(1.0, sample_input)
        self.edit_text.pack(fill="x")

        step_three_label = Label(self.master, text="MESSAGE",  background="grey", foreground="white")
        step_three_label.config(anchor=CENTER)
        step_three_label.pack(fill="x")

        self.terminal_text = Text(self.master, background="black", foreground="green", height=10)
        self.terminal_text.config()
        self.terminal_text.pack(fill="x")


    def print_jump_intructions(self):
        for key, value in self.jump_instructions.items():
            print(f'{key}: {value}')

    def print_variables(self):
        for key, value in self.variables.items():
            var_value = value['value']
            address = value['address']
            print(f'{key}: Address - {address} | Value - {var_value}')

    # Pad binary digits
    def print_formatted_table(self):
        print_df = self.binary_table_df.copy()
        print_df['address'] = print_df['address'].apply(lambda x: x[2:].zfill(16))
        print_df['31-25']   = print_df['31-25'].apply(lambda x: x[2:].zfill(7)[::-1][0:8][::-1])
        print_df['24-20']   = print_df['24-20'].apply(lambda x: x[2:].zfill(5)[::-1][0:5][::-1])
        print_df['19-15']   = print_df['19-15'].apply(lambda x: x[2:].zfill(5)[::-1][0:5][::-1])
        print_df['14-12']   = print_df['14-12'].apply(lambda x: x[2:].zfill(3)[::-1][0:3][::-1])
        print_df['11-7']    = print_df['11-7'].apply(lambda x: x[2:].zfill(5)[::-1][0:5][::-1])
        print_df['6-0']     = print_df['6-0'].apply(lambda x: x[2:].zfill(7)[::-1][0:7][::-1])

        if not self.test:
            print_df.drop(['line_number', 'pending_jump', 'pending_variable'], axis='columns', inplace=True)

        print(print_df)

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

    # Get return row on parsing of matched line
    def parse_instruction(self, instruction, matched_string, is_command):

        # If is_command is True, convert the command to opcode
        if is_command:

            def represents_int(s):
                try:
                    int(s)
                    return True
                except ValueError:
                    return False

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

                if thirtyone_to_twenty[0:2] == '0x':
                    thirtyone_to_twenty = bin(int(thirtyone_to_twenty, 16))[2:].zfill(12)
                else:
                    string_to_int = int(thirtyone_to_twenty)
                    if string_to_int > -1:
                        thirtyone_to_twenty = bin(string_to_int)[2:].zfill(12)
                    else:
                        thirtyone_to_twenty = bin(string_to_int & 0xfff)[2:]

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

                # Old way of computing immediate value for opcode
                # immediate = '0' if matched_string[2] == '' else matched_string[2]
                variable_name = matched_string[2]

                pending_variable_name = None
                if variable_name[0:2] == '0x':
                    immediate = bin(int(variable_name, 16))[2:].zfill(12)
                elif represents_int(variable_name):
                    var_as_int = int(variable_name)
                    if var_as_int > -1:
                        immediate = bin(int(variable_name))[2:].zfill(12)
                    else:
                        immediate = bin(var_as_int & 0xfff)[2:] #for two's complement
                elif variable_name in self.variables.keys():
                    immediate = self.variables[variable_name]['address']
                else:
                    # Kapag wala sa listahan, zero muna
                    pending_variable_name = variable_name
                    immediate = bin(0)[2:].zfill(12)

                immi_0_4 = int(immediate[::-1][0:5][::-1], 2)

                # op code
                six_to_zero = taxonomy_details['6-0']
                # funct3
                fourteen_to_twelve = taxonomy_details['14-12']
                # funct7
                thirtyone_to_twentyfive = int(immediate[::-1][5:12][::-1], 2)

                if instruction == 'sw':
                    #rd
                    eleven_to_seven = immi_0_4
                    # rs2
                    twentyfour_to_twenty = matched_string[1]
                elif instruction == 'lw':
                    #rd
                    eleven_to_seven = matched_string[1]
                    # rs2
                    twentyfour_to_twenty = immi_0_4

                # rs 1
                # nineteen_to_fifteen = matched_string[3] # Old way of getting rs1 in lw/sw
                if matched_string[5]:
                    nineteen_to_fifteen = matched_string[5]
                else:
                    nineteen_to_fifteen = 0

                row_to_return = {
                    '31-25': thirtyone_to_twentyfive,
                    '24-20': twentyfour_to_twenty,
                    '19-15': nineteen_to_fifteen,
                    '14-12': fourteen_to_twelve,
                    '11-7': eleven_to_seven,
                    '6-0': six_to_zero,
                    'pending_variable': pending_variable_name
                }

                return row_to_return

            def sb_type():

                jump_inst = matched_string[3]

                pending_jump_name = None

                # If jump instruction already in lookup, get the immediate
                if jump_inst in self.jump_instructions.keys():

                    # Offset = jump instruction address - current address divided by 2
                    immediate = (int(self.jump_instructions[jump_inst], 2) - int(self.current_text_segment, 2)) // 2

                    original_binary = bin(immediate & 0xfff)[2:]

                    if immediate > -1:
                        immediate = bin(immediate)[2:].zfill(12)[::-1]
                    else:
                        immediate = bin(immediate & 0xfff)[2:][::-1] #for two's complement

                    # Get the 4 parts of the immediate value
                    imm_12 = immediate[11]
                    imm_10_5 = immediate[5:11][::-1]
                    imm_4_1 = immediate[0:5][::-1]
                    imm_11 = immediate[10]


                    # For checking if slicing of binary value is correct

                    # print(f'Original: {original_binary}')
                    # print(f'Reversed: {immediate}')
                    # print(f'Recombined: {imm_12}-{imm_11}-{imm_10_5}-{imm_4_1}')
                    # checking_result = original_binary == (imm_12 + imm_11 + imm_10_5 + imm_4_1)
                    # print(f'Checking: {checking_result}')

                    # rd
                    eleven_to_seven = int(f'{imm_4_1}{imm_11}', 2)
                    # funct7
                    thirtyone_to_twentyfive = int(f'{imm_12}{imm_10_5}', 2)

                else:

                    # Dito yung kailangan word yung wala pang jump instruction sa look up
                    pending_jump_name = jump_inst
                    # rd
                    eleven_to_seven = 0
                    # funct7
                    thirtyone_to_twentyfive = 0

                # op code
                six_to_zero = 99
                # funct3
                fourteen_to_twelve = taxonomy_details['14-12']
                # rs1
                nineteen_to_fifteen = matched_string[1]
                # rs2
                twentyfour_to_twenty = matched_string[2]

                row_to_return = {
                    '31-25': thirtyone_to_twentyfive,
                    '24-20': twentyfour_to_twenty,
                    '19-15': nineteen_to_fifteen,
                    '14-12': fourteen_to_twelve,
                    '11-7': eleven_to_seven,
                    '6-0': six_to_zero,
                    'pending_jump': pending_jump_name
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
            else:
                raise Exception(f"Unmapped instruction type '{taxonomy_details['type']}'")

            if 'pending_jump' in row_to_return:
                pending_jump_name_temp = row_to_return['pending_jump']
            else:
                pending_jump_name_temp = None

            if 'pending_variable' in row_to_return:
                pending_variable_name_temp = row_to_return['pending_variable']
            else:
                pending_variable_name_temp = None

            # Cast to binary
            row_to_return = {key: bin(int(value)) for key, value in row_to_return.items()
                             if key not in ['pending_jump', 'pending_variable']}

            address = self.current_text_segment
            row_to_return['pending_variable'] = pending_variable_name_temp
            row_to_return['pending_jump'] = pending_jump_name_temp
            row_to_return['address'] = address
            row_to_return['instruction'] = instruction
            row_to_return['line_number'] = self.line_counter

            self.current_text_segment = bin(int(address, 2) + int ('100', 2)) # Increment by 4 current address

            return row_to_return

        # If is_command is False, handle special cases depending of instruction type
        elif not is_command:

            # Returns boolean if variable was added
            if instruction == 'variable':

                # Get value of variable
                var_name = matched_string[1]
                value = matched_string[3]
                # value = bin(int(value, 16))

                if value[0:2] == '0x':
                    value = bin(int(value, 16))
                else:
                    value = bin(int(value))

                if var_name in self.variables.keys(): return False

                self.variables[var_name] = {}

                # Get current address to place variable
                address = self.current_data_segment
                # Increment by 4 the current address and pad with zeroes until 32 bits
                self.current_data_segment = format(int(address, 2) + int ('100', 2), '#014b')

                self.variables[var_name]['value'] = value
                self.variables[var_name]['address'] = address

                return True

            #Toggle the mode of the edit text field
            elif instruction == 'data':
                self.is_data = True
                self.is_text = False
            elif instruction == 'text':
                self.is_data = False
                self.is_text = True

            #Returns false if jump instrution already in the table
            elif instruction == 'jump':

                jump_inst = matched_string[1]

                if jump_inst in self.jump_instructions.keys(): return False

                address = self.current_text_segment
                self.jump_instructions[jump_inst] = address

                # Commented out, jump doesn't need to be added as a intruction
                # self.current_text_segment = bin(int(address, 2) + int ('100', 2)) # Increment by 4 the current address

                return True

    # Search if pending jumps are declared
    def populate_pending_jumps(self):

        if self.test:
            print("in populate pending jump")
            self.print_formatted_table()

        for index, row in self.binary_table_df.iterrows():
            if row['pending_jump'] is not None:
                jump_inst = row['pending_jump']

                if jump_inst not in self.jump_instructions.keys():
                    # raise Exception(f"Error: {jump_inst} was never declared.")
                    msg = f"Line: {row['line_number']}, Error: {jump_inst} was never declared."
                    return msg

                # Offset =  (jump instruction address - current address) / 2
                immediate = (int(self.jump_instructions[jump_inst], 2) - int(row['address'], 2)) // 2

                original_binary = bin(immediate & 0xfff)[2:]

                if immediate > -1:
                    immediate = bin(immediate)[2:].zfill(12)[::-1]
                else:
                    immediate = bin(immediate & 0xfff)[2:][::-1]  # for two's complement

                # Get the 4 parts of the immediate value
                imm_12 = immediate[11]
                imm_10_5 = immediate[5:11][::-1]
                imm_4_1 = immediate[0:5][::-1]
                imm_11 = immediate[10]

                # For checking if slicing of binary value is correct

                # print(f'Original: {original_binary}')
                # print(f'Reversed: {immediate}')
                # print(f'Recombined: {imm_12}-{imm_11}-{imm_10_5}-{imm_4_1}')
                # checking_result = original_binary == (imm_12 + imm_11 + imm_10_5 + imm_4_1)
                # print(f'Checking: {checking_result}')

                # rd
                eleven_to_seven = int(imm_4_1 + imm_11, 2)
                # funct7
                thirtyone_to_twentyfive = int(imm_12 + imm_10_5, 2)

                # cast to binary
                eleven_to_seven = bin(int(eleven_to_seven))
                thirtyone_to_twentyfive = bin(int(thirtyone_to_twentyfive))

                row_to_return = {
                    'address': row['address'],
                    'instruction': row['instruction'],
                    '31-25': thirtyone_to_twentyfive,
                    '24-20': row['24-20'],
                    '19-15': row['19-15'],
                    '14-12': row['14-12'],
                    '11-7': eleven_to_seven,
                    '6-0': row['6-0'],
                    'line_number': row['line_number'],
                    'pending_jump': None,
                    'pending_variable': row['pending_variable']
                }

                if self.test:
                    print("#" * 100)
                    print("START UPDATE FUNCTION")
                    print("#" * 100)

                    print(f"Will update binary df for pending function '{jump_inst}' with values:")
                    print(row_to_return)

                    print("Before update:")
                    self.print_formatted_table()

                # New way of updating
                self.binary_table_df.at[index, "31-25"] = thirtyone_to_twentyfive
                self.binary_table_df.at[index, "11-7"] = eleven_to_seven
                self.binary_table_df.at[index, "pending_jump"] = None


                if self.test:
                    print("After update:")
                    self.print_formatted_table()
                    print("#" * 100)
                    print("END UPDATE FUNCTION")
                    print("#" * 100)


    # Search if pending variables are declared
    def populate_pending_variables(self):

        if self.test:
            print("in populate pending variables")
            self.print_formatted_table()

        for index, row in self.binary_table_df.iterrows():
            if row['pending_variable'] is not None:
                variable_name = row['pending_variable']
                instruction = row['instruction']

                if variable_name in self.variables.keys():
                    immediate = self.variables[variable_name]['address']
                else:
                    msg = f"Line: {row['line_number']}, Error: {variable_name} was never declared."
                    return msg
                    # raise Exception(f"Error: {variable_name} was never declared.")

                immi_0_4 = int(immediate[::-1][0:5][::-1], 2)

                # funct7
                thirtyone_to_twentyfive = bin(int(immediate[::-1][5:12][::-1], 2))

                if instruction == 'sw':
                    #rd
                    eleven_to_seven = bin(int(immi_0_4))
                    # rs2
                    twentyfour_to_twenty = row['11-7']
                elif instruction == 'lw':
                    #rd
                    eleven_to_seven = row['11-7']
                    # rs2
                    twentyfour_to_twenty = bin(int(immi_0_4))

                row_to_return = {
                    'address': row['address'],
                    'instruction': instruction,
                    '31-25': thirtyone_to_twentyfive,
                    '24-20': twentyfour_to_twenty,
                    '19-15': row['19-15'],
                    '14-12': row['14-12'],
                    '11-7': eleven_to_seven,
                    '6-0': row['6-0'],
                    'pending_jump': row['pending_jump'],
                    'pending_variable': None,
                    'line_number': row['line_number']
                }

                if self.test:
                    print("#" * 100)
                    print("START UPDATE VARIABLE")
                    print("#" * 100)
                    print(f"Will update binary for pending variable '{variable_name}' with values:")
                    print(row_to_return)

                    print("Before update:")
                    self.print_formatted_table()

                self.binary_table_df.at[index] = row_to_return

                if self.test:
                    print("After update:")
                    self.print_formatted_table()
                    print("#" * 100)
                    print("END UPDATE VARIABLE")
                    print("#" * 100)

    # Gets the string from the edit text box
    def evaluate(self):

        #Get lines from text field
        string_to_eval = self.edit_text.get("1.0", "end")
        list_of_commands = string_to_eval.splitlines()

        # Reset all parameters
        parsing_passed = True
        self.line_counter = 1
        self.is_data = False
        self.is_text = True

        self.variables = {}
        self.jump_instructions = {}
        self.current_data_segment = '0b000000000000' # 0x0000 in binary
        self.current_text_segment = '0b1000000000000' # 0x1000 in binary
        self.binary_table_df = pd.DataFrame(columns=['address', 'instruction', '31-25', '24-20', '19-15', '14-12', '11-7', '6-0'])

        #For testing
        results = []

        for command in list_of_commands:
            msg = None
            match_found = False
            formatted_command = command.lower().strip()

            if formatted_command == '': # Skip if empty line
                self.line_counter += 1
                continue

            # print(f"Command to match regex: {command}")
            for key, command in self.commands_dict.items():
                match_regex = re.match(command['regex'], formatted_command)

                if match_regex:

                    if self.is_text:
                        row_to_add = self.parse_instruction(key, match_regex.groups(), True)
                        self.binary_table_df = self.binary_table_df.append(row_to_add, ignore_index=True)
                        if self.test: msg = match_regex.groups()
                    else:
                        msg = f"Line: {self.line_counter}, Error: No '.text' reserved word found before this instruction."
                    # print("Row to add")
                    # print(row_to_add)
                    match_found = True
                    break

            # If no commands matched, check if it's a reserved word command
            if not match_found:

                # Key is the regex type
                for key, regex in reserved_list.items():
                    match_regex = re.match(regex, formatted_command)

                    if match_regex:

                        if key == 'jump':
                            if self.is_text:
                                result = self.parse_instruction(key, match_regex.groups(), False)
                                if not result:
                                    msg = f"Line: {self.line_counter}, Error: Instruction '{match_regex[1]}' is already defined."
                            else:
                                msg = f"Line: {self.line_counter}, Error: No '.text' reserved word found before this instruction."

                        elif key in ['data', 'text']:
                            row_to_add = self.parse_instruction(key, match_regex.groups(), False)
                            if self.test: msg = match_regex.groups()

                        elif key == 'variable':
                            if self.is_data:
                                result = self.parse_instruction(key, match_regex.groups(), False)
                                if result:
                                    if self.test: msg = match_regex.groups()
                                else:
                                    msg = f"Line: {self.line_counter}, Error: Variable '{match_regex[1]}' is already defined."
                            else:
                                msg = f"Line: {self.line_counter}, Error: No '.data' reserved word found before this instruction."
                        break

            if not self.test:

                if not match_regex:
                    msg = f'Line: {self.line_counter}, Error: Incorrect Syntax.'

                if msg != None:
                    self.print_in_terminal(msg)
                    parsing_passed = False
                    break

            else:
                if not match_regex:
                    msg = f'Line: {self.line_counter}, Error: Incorrect Syntax.'
                output_string = f'[{formatted_command}] : {msg}\n'
                results.append(output_string)

            self.line_counter += 1

        # Populate pending jumps
        has_error = self.populate_pending_jumps()
        if has_error:
            self.print_in_terminal(has_error)
            parsing_passed = False

        # Populate pending variables
        has_error = self.populate_pending_variables()
        if has_error:
            self.print_in_terminal(has_error)
            parsing_passed = False


        if parsing_passed:
            if self.test:
                self.print_in_terminal(results)

            self.print_formatted_table()



            if not self.test:
                self.print_in_terminal('Success in parsing.\n')

            print('=' * 100)
            print('Jump Instructions:')
            self.print_jump_intructions()
            print('=' * 100)
            print('Declared Variables:')
            self.print_variables()
            print('=' * 100)
            print('Opcodes:')
            self.print_formatted_table()
            print('=' * 100)

if __name__ == "__main__":

    # Bawal to, check if it passes
    # add x6, x6, x8

    reserved_list = {
        # reserved word
        "data": r'^.(data)$',
        # reserved word
        "text": r'^.(text)$',
        # variable d/eclaration
        "variable": r'^(?!^x(0|0?[1-9]|[12][0-9]|3[01]):)([a-z_][\w]*)[\s]*:[\s]*(.word)[\s]+([-+]?0|[-+]?[1-9]+|0x[a-f0-9]+)$',
        # jump declaration
        "jump": r'(?!^x(0|0?[1-9]|[12][0-9]|3[01]):$)^([a-z_][\w]*)[\s]*:$'
    }

    # Old regex for load store
    # regex_store_instruction = r"[\s]+x(0|0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*([\d]*)\(x(0|0?[1-9]|[12][0-9]|3[01])\)$"

    regex_store_instruction = r"[\s]+x(0|0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*((?!x(0|0?[1-9]|[12][0-9]|3[01]))[a-z_][\w]+|[-+]?0|[-+]?[1-9]+|0x[a-f0-9]+)?(\(x(0|0?[1-9]|[12][0-9]|3[01])\))?$"
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
    app = Main(root, commands_dict, reserved_list, False)
    root.mainloop()
