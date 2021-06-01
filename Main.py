from itertools import cycle
import re
import sys
import csv
import tkinter as tk
from tkinter import Label, Button, Text, CENTER, INSERT, END, Entry, messagebox
from pandas.tseries.frequencies import to_offset
from tksheet import Sheet
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', -1)
# Constants
INITIAL_PIPELINE_COLUMNS = ['address', 'instruction', 'opcode']
#  Opcode Types
LW_OPCODE = '0000011'
SW_OPCODE = '0100011'
BRANCH_OPCODE = '1100011'
ALU_ALU_OPCODE = '0110011'
ALU_IMM_OPCODE = '0010011'
# Address Limits
DATA_SEGMENT_LIMIT = '11111111100'

first_col = 0
second_col = 1
third_col = 2
fourth_col = 3
fifth_col = 4


class Main(tk.Frame):

    # Initialize the screen
    def __init__(self, master, commands_dict, reserved_list, registers_dict, sample_input, addresses_to_load_dict, test_flag):
        self.master = master
        self.master.title("RISC-V Simulator")
        self.master.geometry('1400x900')
        # self.master.attributes('-fullscreen', True)
        self.master.config(bg = 'darkgray')
        self.sample_input = sample_input
        self.test = test_flag # Boolean for testing outputs
        self.is_data = False
        self.is_text = False
        self.parsing_passed = True
        self.runtime_passed = True
        self.line_counter = 1
        self.edit_text = None
        self.terminal_text = None
        self.will_jump = False
        self.execute_internal_counter = 0

        self.internal_registers_dict = {
            "IF/ID.IR": {"value": '0',
                         'hex_length': 8},
            "IF/ID.NPC": {"value": '0',
                         'hex_length': 4},
            "PC": {"value": '1000000000000',
                         'hex_length': 4},
            "ID/EX.A": {"value": '0',
                         'hex_length': 8},
            "ID/EX.B": {"value": '0',
                         'hex_length': 8},
            "ID/EX.IMM": {"value": '0',
                         'hex_length': 3},
            "ID/EX.IR": {"value": '0',
                         'hex_length': 8},
            "ID/EX.NPC": {"value": '0',
                         'hex_length': 4},
            "EX/MEM.ALUOUTPUT": {"value": '0',
                         'hex_length': 8},
            "EX/MEM.COND": {"value": '0',
                         'hex_length': 1},
            "EX/MEM.IR": {"value": '0',
                         'hex_length': 8},
            "EX/MEM.B": {"value": '0',
                         'hex_length': 8},
            "MEM/WB.LMD": {"value": '0',
                         'hex_length': 8},
            "MEM/WB.IR": {"value": '0',
                         'hex_length': 8},
            "MEM/WB.ALUOUTPUT": {"value": '0',
                         'hex_length': 8},
            "MEM/MEMORY AFFECTED": {"value": '0',
                         'hex_length': 4},
            "MEM/MEMORY VALUE": {"value": '0',
                         'hex_length': 8},
            "WB/REGISTER AFFECTED": {"value": '0',
                         'hex_length': 2},
            "WB/REGISTER VALUE": {"value": '0',
                         'hex_length': 8}
        }
        self.registers_dict = registers_dict

        self.data_segment_dict = {
        }

        self.pipeline_map_df = pd.DataFrame()
        self.old_pipeline_map_df = pd.DataFrame()
        self.current_pipeline_instructions = []
        self.commands_dict = commands_dict
        self.reserved_list = reserved_list
        self.variables = {}
        self.jump_instructions = {}
        self.current_data_segment = None
        self.current_text_segment = None
        self.binary_table_df = None
        self.registers_table = None
        self.pipeline_map_table = None
        self.internal_registers_table = None
        self.labels_table = None
        self.data_segment_table = None
        self.text_segment_table = None
        self.is_line_by_line = None
        self.line_button = None
        self.line_incrementer = None
        self.go_to_input_ui = None
        self.go_to_variable = tk.StringVar()
        self.initialize_data_segment(addresses_to_load_dict)
        self.create_widgets()

        # comment for auto run
        # self.evaluate()
        # if self.parsing_passed:
        #     self.execute()
        #     self.repopulate_pipeline_ui(self.old_pipeline_map_df)
            # print(self.old_pipeline_map_df)
            # self.print_registers()

    def go_to(self):
        address = str(self.go_to_variable.get())

        data_segment_df = pd.DataFrame(self.data_segment_table.get_sheet_data(get_index=True), columns = ['address', 'value'])




        index_to_go_to = data_segment_df[data_segment_df["address"] == address].index

        if len(address) == 0:
            self.go_to_variable.set("Go to")
            self.go_to_input_ui.config({"background": "white"})
        elif len(index_to_go_to) == 0:
            # messagebox.showwarning("showinfo", f"Address {address} cannot be found")
            self.go_to_input_ui.config({"background": "#9E1A1A"})
        else:
            index_to_go_to = index_to_go_to[0]
            self.data_segment_table.see(row=index_to_go_to, check_cell_visibility=True)
            self.data_segment_table.highlight_rows(rows=[index_to_go_to], bg='green', highlight_index=True, redraw=True)
            self.data_segment_table.dehighlight_all()
            self.go_to_input_ui.config({"background": "lightgreen"})





    def reset_data(self):

        self.is_data = False
        self.is_text = False
        self.parsing_passed = True
        self.runtime_passed = True
        self.line_counter = 1
        self.will_jump = False
        self.go_to_input_ui.config({"background": "white"})
        self.go_to_variable.set("Go to")

        self.internal_registers_dict = {
            "IF/ID.IR": {"value": '0',
                         'hex_length': 8},
            "IF/ID.NPC": {"value": '0',
                         'hex_length': 4},
            "PC": {"value": '1000000000000',
                         'hex_length': 4},
            "ID/EX.A": {"value": '0',
                         'hex_length': 8},
            "ID/EX.B": {"value": '0',
                         'hex_length': 8},
            "ID/EX.IMM": {"value": '0',
                         'hex_length': 3},
            "ID/EX.IR": {"value": '0',
                         'hex_length': 8},
            "ID/EX.NPC": {"value": '0',
                         'hex_length': 4},
            "EX/MEM.ALUOUTPUT": {"value": '0',
                         'hex_length': 8},
            "EX/MEM.COND": {"value": '0',
                         'hex_length': 1},
            "EX/MEM.IR": {"value": '0',
                         'hex_length': 8},
            "EX/MEM.B": {"value": '0',
                         'hex_length': 8},
            "MEM/WB.LMD": {"value": '0',
                         'hex_length': 8},
            "MEM/WB.IR": {"value": '0',
                         'hex_length': 8},
            "MEM/WB.ALUOUTPUT": {"value": '0',
                         'hex_length': 8},
            "MEM/MEMORY AFFECTED": {"value": '0',
                         'hex_length': 4},
            "MEM/MEMORY VALUE": {"value": '0',
                         'hex_length': 8},
            "WB/REGISTER AFFECTED": {"value": '0',
                         'hex_length': 2},
            "WB/REGISTER VALUE": {"value": '0',
                         'hex_length': 8}
        }
        self.registers_dict = registers_dict

        self.data_segment_dict = {
        }

        self.pipeline_map_df = pd.DataFrame()
        self.old_pipeline_map_df = pd.DataFrame()
        self.current_pipeline_instructions = []
        self.commands_dict = commands_dict
        self.reserved_list = reserved_list
        self.variables = {}
        self.jump_instructions = {}
        self.current_data_segment = None
        self.current_text_segment = None
        self.binary_table_df = pd.DataFrame()

        self.is_line_by_line = None
        self.line_incrementer = tk.IntVar()


        self.initialize_data_segment(addresses_to_load_dict)

        # self.repopulate_register_ui()
        # self.repopulate_data_segment_ui()
        # self.repopulate_internal_register_ui()
        # self.repopulate_text_segment_ui()
        # self.repopulate_labels_ui()

        self.pipeline_map_table.destroy()

        self.pipeline_map_table = Sheet(self.master,
                                        show_row_index=True,
                                        header_height="0",
                                        row_index_width=100,
                                        show_y_scrollbar=False,
                                        show_x_scrollbar=False,
                                        data=[])
        self.pipeline_map_table.enable_bindings()
        self.pipeline_map_table.change_theme(theme="dark blue")
        self.pipeline_map_table.grid(row=6, column=fourth_col, columnspan=3, sticky="nswe")


        self.labels_table.destroy()

        self.labels_table = Sheet(self.master,
                                  show_row_index=True,
                                  header_height="0",
                                  show_y_scrollbar=False,
                                  row_index_width=50,
                                  show_x_scrollbar=False,
                                  data=[],
                                  theme="dark blue")
        self.labels_table.headers(newheaders=['VALUE'], index=None,
                                  reset_col_positions=False, show_headers_if_not_sheet=True)
        self.labels_table.enable_bindings()
        self.labels_table.grid(row=2, column=third_col, columnspan=1, sticky="nswe")

        self.data_segment_table.dehighlight_all()

        self.text_segment_table.destroy()

        self.text_segment_table = Sheet(self.master,
                                        show_row_index=True,
                                        header_height="0",
                                        row_index_width=50,
                                        show_y_scrollbar=False,
                                        show_x_scrollbar=False,
                                        data=[[]], theme="dark blue")
        self.text_segment_table.headers(newheaders=['CODE', 'BASIC'], index=None,
                                        reset_col_positions=False, show_headers_if_not_sheet=True)
        self.text_segment_table.enable_bindings()
        self.text_segment_table.grid(row=2, column=fourth_col, columnspan=1, sticky="nswe")


        self.registers_table.set_sheet_data(data=[[]],
                                               reset_col_positions=True,
                                               reset_row_positions=True,
                                               redraw=True,
                                               verify=False,
                                               reset_highlights=False)
        self.repopulate_register_ui()


        self.data_segment_table.set_sheet_data(data = [[]],
               reset_col_positions = True,
               reset_row_positions = True,
               redraw = True,
               verify = False,
               reset_highlights = False)

        self.internal_registers_table.set_sheet_data(data = [[]],
               reset_col_positions = True,
               reset_row_positions = True,
               redraw = True,
               verify = False,
               reset_highlights = False)



    def repopulate_register_ui(self):

        # self.registers_table.set_row_data(0, values = (0 for i in range(35)))
        list_version_of_register_dict = []
        index_registers = []

        for register, value in self.registers_dict.items():
            list_version_of_register_dict += [["{0:0>8X}".format(int(value['value'], 2))]]
            index_registers += [register]

        self.registers_table.set_sheet_data(data=list_version_of_register_dict,
                       reset_col_positions=True,
                       reset_row_positions=True,
                       redraw=True,
                       verify=False,
                       reset_highlights=False)

        self.registers_table.row_index(newindex=index_registers, reset_row_positions=False,
                                      show_index_if_not_sheet=True)

    def repopulate_internal_register_ui(self):

        list_version_of_internal_registers_dict = []
        index_headers = []

        for internal_register, value in self.internal_registers_dict.items():
            hex_length = value['hex_length']
            format_thingy = "0:0>{}X".format(hex_length)
            format_thingy = "{" + format_thingy + "}"
            in_hex = format_thingy.format(int(value['value'], 2))
            # Uncomment  to convert to proper hex value (and length)
            list_version_of_internal_registers_dict += [[in_hex]]

            # list_version_of_internal_registers_dict += [[value['value']]]

            index_headers += [internal_register]

        self.internal_registers_table.set_sheet_data(data=list_version_of_internal_registers_dict,
                                            reset_col_positions=True,
                                            reset_row_positions=True,
                                            redraw=True,
                                            verify=False,
                                            reset_highlights=False)

        self.internal_registers_table.row_index(newindex=index_headers, reset_row_positions=False,
                                      show_index_if_not_sheet=True)

    def repopulate_data_segment_ui(self):
        list_version_of_data_segment_dict = []
        counter = 0
        first = None
        second = None
        third = None
        fourth = None
        ui_address_list = []

        for address, value in self.data_segment_dict.items():

            counter += 1

            if counter == 1:
                first = value
                ui_address = address
            elif counter == 2:
                second = value
            elif counter == 3:
                third = value
            elif counter == 4:
                fourth = value
                counter = 0
                first = "{0:0>2X}".format(int(first, 16))
                second = "{0:0>2X}".format(int(second, 16))
                third = "{0:0>2X}".format(int(third, 16))
                fourth = "{0:0>2X}".format(int(fourth, 16))
                list_version_of_data_segment_dict += [[f"{fourth} | {third} | {second} | {first}"]]
                ui_address_list += [ui_address]

        self.data_segment_table.set_sheet_data(data=list_version_of_data_segment_dict,
                                                     reset_col_positions=True,
                                                     reset_row_positions=True,
                                                     redraw=True,
                                                     verify=False,
                                                     reset_highlights=False)

        self.data_segment_table.row_index(newindex=ui_address_list, reset_row_positions=False,
                                                show_index_if_not_sheet=True)

    def repopulate_text_segment_ui(self):

        list_version_of_text_segment_dict = []
        index_addresses = []

        for index, row in self.binary_table_df.iterrows():
            thirty_one_to_twenty_five = row['31-25'][2:].zfill(7)[::-1][0:8][::-1]
            twenty_four_to_twenty = row['24-20'][2:].zfill(5)[::-1][0:8][::-1]
            nineteen_to_fifteen = row['19-15'][2:].zfill(5)[::-1][0:8][::-1]
            fourteen_to_twelve = row['14-12'][2:].zfill(3)[::-1][0:8][::-1]
            eleven_to_seven = row['11-7'][2:].zfill(5)[::-1][0:8][::-1]
            six_to_zero = row['6-0'][2:].zfill(7)[::-1][0:8][::-1]
            concatenated = thirty_one_to_twenty_five + twenty_four_to_twenty + nineteen_to_fifteen + fourteen_to_twelve + eleven_to_seven + six_to_zero
            list_version_of_text_segment_dict += [["0x" + "{0:0>8X}".format(int(concatenated, 2)), row['actual_command']]]
            index_addresses += ["0x" + "{0:0>4X}".format(int(row['address'], 2))]

        self.text_segment_table.set_sheet_data(data=list_version_of_text_segment_dict,
                                               reset_col_positions=True,
                                               reset_row_positions=True,
                                               redraw=True,
                                               verify=False,
                                               reset_highlights=False)

        self.text_segment_table.row_index(newindex=index_addresses, reset_row_positions=False,
                                      show_index_if_not_sheet=True)

    def repopulate_labels_ui(self):
        list_version_of_labels_dict = []
        index_labels = []

        for label, value in self.jump_instructions.items():
            list_version_of_labels_dict += [["0x" + "{0:0>4X}".format(int(value, 2))]]
            index_labels += [label]

        for name, value in self.variables.items():
            address = value['address']
            list_version_of_labels_dict += [["0x" + "{0:0>4X}".format(int(address, 2))]]
            index_labels += [name]

        self.labels_table.set_sheet_data(data=list_version_of_labels_dict,
                                               reset_col_positions=True,
                                               reset_row_positions=True,
                                               redraw=True,
                                               verify=False,
                                               reset_highlights=False)

        self.labels_table.row_index(newindex=index_labels, reset_row_positions=False,
                                      show_index_if_not_sheet=True)

    def repopulate_pipeline_ui(self, pipeline_map):

        list_version_of_pipeline_df= []
        # for label, value in self.labels_dict.items():
        #     list_version_of_pipeline_df += [[label, value]]
        list_version_of_pipeline_df = []

        pipeline_map = pipeline_map.replace(np.nan, '', regex=True)

        for x in range(pipeline_map.shape[0]):
            temp_flattened_list = pipeline_map.loc[x, (pipeline_map.columns != 'opcode') & (pipeline_map.columns != 'instruction')].values.tolist()
            temp_flattened_list[0] = "0x" + "{0:0>4X}".format(int(temp_flattened_list[0], 2))
            list_version_of_pipeline_df += [temp_flattened_list]

        list_of_clock_cycles = ['ADDRESS'] + [f'CYCLE {x}' for x in range(1, pipeline_map.shape[1] - 2)]

        self.pipeline_map_table.headers(newheaders=list_of_clock_cycles, index=None,
                                     reset_col_positions=False, show_headers_if_not_sheet=True)

        self.pipeline_map_table.set_sheet_data(data=list_version_of_pipeline_df,
                                               reset_col_positions=True,
                                               reset_row_positions=True,
                                               redraw=True,
                                               verify=False,
                                               reset_highlights=False)

        if pipeline_map.shape[0] > 0:
            self.pipeline_map_table.row_index(newindex=pipeline_map['instruction'].tolist(),  reset_row_positions=False, show_index_if_not_sheet=True)

        with open('pipelinemap.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # writer.writerows(list_version_of_pipeline_df)
            writer.writerows(self.pipeline_map_table.get_sheet_data(get_index = True))

    def initialize_data_segment(self, addresses_to_load_dict):

        address = '0'
        for x in range (0, 512):

            value = '0'
            address_key = "{0:0>8X}".format(int(address, 2))

            if address_key in addresses_to_load_dict.keys():
                value = addresses_to_load_dict[address_key]

            self.data_segment_dict[address_key] = value
            address = hex(int(address, 2) + int ('1', 2)) # Increment by 4 current address
            address = bin(int(address,  16))

    def execute_next_line(self):

        if self.is_line_by_line is None:
            self.is_line_by_line = True
            self.execute()
        elif self.is_line_by_line is True:
            self.line_incrementer.set(1)
        else:
            pass


    def execute_all(self):
        if self.is_line_by_line is None:
            self.is_line_by_line = False
            self.execute()
        else:
            pass

    def wait_line_by_line(self, cycle_number, instruction):
        # self.print_formatted_table()

        # print(instruction)
        # cycle_number = cycle_number + 1
        cycle_number = cycle_number

        row_being_executed = self.old_pipeline_map_df.index[self.old_pipeline_map_df.address == instruction][0]
        # print(self.pipeline_map_df[f'Cycle {cycle_number}'])
        # row_being_executed = self.pipeline_map_df.filter(regex='^Cycle ', axis=1).loc[:cycle_number + 1].first_valid_index()
        # row_being_executed = self.pipeline_map_df[f'Cycle {cycle_number}']
        # print(self.pipeline_map_df[self.pipeline_map_df[f'Cycle {cycle_number}'] == 'WB'].index)
        # Get the current column being executed.

        ui_data = list(self.pipeline_map_table.get_column_data(cycle_number, return_copy=True))

        # if self.will_jump == True:
        #     step = ['IF']
        # else:
        #     step = ['WB']


        row_being_executed = [idx for idx, element in enumerate(ui_data) if element != ""][0]

        # Remove all highlights
        self.pipeline_map_table.dehighlight_all()
        # Put row highlight
        self.pipeline_map_table.highlight_rows(rows=[row_being_executed], bg='gray', highlight_index=True, redraw=True)
        # Put column highlight
        self.pipeline_map_table.highlight_columns(columns=[cycle_number], bg='gray', highlight_header=True, redraw=True)
        # move view
        self.pipeline_map_table.see(row=row_being_executed, column=cycle_number,check_cell_visibility=True)

        # print(f"waiting...{cycle_number}")
        if self.is_line_by_line == True:
            self.line_button.wait_variable(self.line_incrementer)

        # print("done...")

    def create_widgets(self):
        # self.master.grid_columnconfigure(0, weight=1)
        # self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1, uniform="group1")
        self.master.grid_columnconfigure(1, weight=1, uniform="group1")
        # self.master.grid_rowconfigure(0, weight=1)

        assemble_button = Button(self.master, text="ASSEMBLE", command=self.evaluate, bg="green", fg="green", highlightbackground='#008000')
        # assemble_button.pack(fill="x")
        assemble_button.grid(row=0, column=first_col, columnspan=1, sticky='nswe')
        editor_label = Label(self.master, text="EDITOR",  background="darkblue", foreground="white")
        editor_label.config(anchor=CENTER)
        editor_label.grid(row=1, column=first_col, columnspan=1, sticky='nswe')
        self.edit_text = Text(self.master, background="white", foreground="black", insertbackground='black', height=20,
                              font=("Calibri", 15))
        self.edit_text.grid(row=2, column=first_col, columnspan=1, sticky='nswe')
        self.line_incrementer = tk.IntVar()
        self.line_button = Button(self.master, text="EXECUTE LINE", command=self.execute_next_line, bg="gray", fg="blue", highlightbackground='#008000')
        self.line_button.grid(row=0, column=third_col, columnspan=1, sticky='nswe')
        execute_all_button = Button(self.master, text="EXECUTE ALL", command=self.execute_all, bg="gray", fg="blue", highlightbackground='#008000')
        execute_all_button.grid(row=0, column=second_col, columnspan=1, sticky='nswe')
        register_label = Label(self.master, text="REGISTERS", background="#606060", foreground="white")
        register_label.config(anchor=CENTER)
        register_label.grid(row=1, column=second_col, columnspan=1, sticky='nswe')
        self.registers_table = Sheet(self.master,
                                     show_row_index=True,
                                         row_index_width=50,
                                     header_height="0",
                                     show_y_scrollbar=False,
                                     show_x_scrollbar=False,
                                     data=[[f"x{r}" if c == 0 else "0" for c in range(2)] for r in range(32)],
                                     theme = "dark blue")
        self.registers_table.headers(newheaders=['VALUE'], index=None,
                                     reset_col_positions=False, show_headers_if_not_sheet=True)
        self.registers_table.enable_bindings()
        self.registers_table.readonly_columns(columns=[0], readonly=True, redraw=True)
        self.registers_table.grid(row=2,  column=second_col, columnspan=1, sticky="nswe")
        self.edit_text.insert(1.0, self.sample_input)
        # self.edit_text.grid(row=4)
        console_log_label = Label(self.master, text="CONSOLE LOG",  background="black", foreground="white")
        console_log_label.config(anchor=CENTER)
        console_log_label.grid(row=5, sticky='nswe', column=first_col, columnspan=1)
        self.terminal_text = Text(self.master, background="black", foreground="green", height=20, font=("Consolas", 14))
        self.terminal_text.config()
        self.terminal_text.grid(row=6, column=first_col, columnspan=1, sticky='nswe')
        labels_label = Label(self.master, text="LABELS", background="#585858", foreground="white")
        labels_label.config(anchor=CENTER)
        labels_label.grid(row=1, column=third_col, columnspan=1, sticky='nswe')
        self.labels_table = Sheet(self.master,
                                        show_row_index=True,
                                        header_height="0",
                                        show_y_scrollbar=False,
                                        row_index_width=50,
                                        show_x_scrollbar=False,
                                        data=[],
                                        theme = "dark blue")
        self.labels_table.headers(newheaders=['VALUE'], index=None,
                                              reset_col_positions=False, show_headers_if_not_sheet=True)
        self.labels_table.enable_bindings()
        self.labels_table.grid(row=2, column=third_col, columnspan=1, sticky="nswe")
        data_segment_label = Label(self.master, text="DATA SEGMENT", background="#484848", foreground="white")
        data_segment_label.config(anchor=CENTER)
        data_segment_label.grid(row=1, column=fifth_col, columnspan=1, sticky='nswe')
        self.data_segment_table = Sheet(self.master,
                                        show_row_index=True,
                                        row_index_width=100,
                                        show_y_scrollbar=False,
                                        show_x_scrollbar=False,
                                        data=[[]], theme = "dark blue")
        self.data_segment_table.enable_bindings()
        self.data_segment_table.headers(newheaders=['VALUE'], index=None,
                                              reset_col_positions=False, show_headers_if_not_sheet=True)
        self.data_segment_table.grid(row=2, column=fifth_col, columnspan=1, sticky="nswe")

        self.go_to_input_ui = Entry(self.master, textvariable = self.go_to_variable)
        self.go_to_input_ui.grid(row=0, column=fourth_col, columnspan=1, sticky='nswe')
        go_to_button = Button(self.master, text="GO TO", command=self.go_to, bg="gray", fg="violet", highlightbackground='#008000')
        go_to_button.grid(row=0, column=fifth_col, columnspan=1, sticky='nswe')
        self.go_to_variable.set("Go to")

        text_segment_label = Label(self.master, text="TEXT SEGMENT", background="#505050", foreground="white")
        text_segment_label.config(anchor=CENTER)
        text_segment_label.grid(row=1, column=fourth_col, columnspan=1, sticky='nswe')
        self.text_segment_table = Sheet(self.master,
                                  show_row_index=True,
                                  header_height="0",
                                  row_index_width=50,
                                  show_y_scrollbar=False,
                                  show_x_scrollbar=False,
                                  data=[[]], theme = "dark blue")
        self.text_segment_table.headers(newheaders=['CODE', 'BASIC'], index=None,
                                              reset_col_positions=False, show_headers_if_not_sheet=True)
        self.text_segment_table.enable_bindings()
        self.text_segment_table.grid(row=2, column=fourth_col, columnspan=1, sticky="nswe")
        internal_registers_label = Label(self.master, text="INTERNAL REGISTERS", background="darkorange", foreground="white")
        internal_registers_label.config(anchor=CENTER)
        internal_registers_label.grid(row=5, column=second_col, columnspan=2,sticky='nswe')
        self.internal_registers_table = Sheet(self.master,
                                        show_row_index=True,
                                        header_height="1",
                                        row_index_width=200,
                                        column_width=200,
                                        show_y_scrollbar=False,
                                        show_x_scrollbar=False,
                                        data=[[]])
        self.internal_registers_table.headers(newheaders=['VALUE'], index=None,
                                              reset_col_positions=False, show_headers_if_not_sheet=True)
        self.internal_registers_table.change_theme(theme = "dark blue")
        self.internal_registers_table.enable_bindings()
        self.internal_registers_table.grid(row=6, column=second_col, columnspan=2, sticky="nswe")
        pipeline_map_label = Label(self.master, text="PIPELINE MAP",  background="darkgreen", foreground="white")
        pipeline_map_label.config(anchor=CENTER)
        pipeline_map_label.grid(row=5,  column=fourth_col, columnspan=3, sticky='nswe')
        self.pipeline_map_table = Sheet(self.master,
                                     show_row_index=True,
                                     header_height="0",
                                     row_index_width=100,
                                     show_y_scrollbar=False,
                                     show_x_scrollbar=False,
                                     data=[])
        self.pipeline_map_table.enable_bindings()
        self.pipeline_map_table.change_theme(theme = "dark blue")
        self.pipeline_map_table.grid(row=6,  column=fourth_col, columnspan=3, sticky="nswe")

        self.repopulate_register_ui()
        self.repopulate_internal_register_ui()
        self.repopulate_data_segment_ui()
        self.repopulate_pipeline_ui(self.pipeline_map_df)


    def print_registers(self):
        for key, value in self.registers_dict.items():
            var_value = value['value']
            print(f'Register: {key} | Value - {var_value}')

    def print_jump_intructions(self):
        for key, value in self.jump_instructions.items():
            print(f'{key}: {value}')

    def print_variables(self):
        for key, value in self.variables.items():
            var_value = value['value']
            address = value['address']
            print(f'{key}: Address - {address} | Value - {var_value}')

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
    def parse_instruction(self, instruction, matched_string, actual_instruction, is_command):
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
                if int(thirtyone_to_twenty, 2) > 4095: #If greater than 0xfff
                    return 'Immediate value is greater than 0xfff.'
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
                if variable_name:
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
                else:
                    immediate = bin(0)[2:].zfill(12)
                if int(immediate, 2) > 4095: #If greater than 0xfff
                    return 'Immediate value is greater than 0xfff.'
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
                    pending_jump_name = jump_inst
                    original_binary = bin(immediate & 0xfff)[2:]
                    if immediate > -1:
                        immediate = bin(immediate)[2:].zfill(12)[::-1]
                    else:
                        immediate = bin(immediate & 0xfff)[2:][::-1] #for two's complement
                    # Get the 4 parts of the immediate value
                    imm_12 = immediate[11]
                    imm_10_5 = immediate[5:10][::-1]
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
            if type(row_to_return) == str:
                return row_to_return
            # Cast to binary
            row_to_return = {key: bin(int(value)) for key, value in row_to_return.items()
                             if key not in ['pending_jump', 'pending_variable']}
            address = self.current_text_segment
            row_to_return['pending_variable'] = pending_variable_name_temp
            row_to_return['pending_jump'] = pending_jump_name_temp
            row_to_return['address'] = address
            row_to_return['instruction'] = instruction
            row_to_return['line_number'] = self.line_counter
            row_to_return['actual_command'] = actual_instruction
            # Get the opcode and default rd, rs1 and rs2
            opcode = row_to_return['6-0'][2:].zfill(7)[::-1][0:7][::-1]
            row_to_return['rd'] = 'x' +  str(int(row_to_return['11-7'][2:], 2))
            row_to_return['rs1'] = 'x' +  str(int(row_to_return['19-15'][2:], 2))
            row_to_return['rs2'] = 'x' +  str(int(row_to_return['24-20'][2:], 2))
            # Handle special cases, reg-reg instruction is exempted
            if   opcode == '0000011': #lw
                row_to_return['rs2'] = ''
            elif opcode == '0100011': #sw
                row_to_return['rd'] = ''
            elif opcode == '1100011': #branch
                row_to_return['rd'] = ''
            elif opcode == '0010011': #immediate
                row_to_return['rs2'] = ''
            # print(f'{row_to_return["rd"]}, {row_to_return["rs1"]}, {row_to_return["rs2"]}')
            # Split the actual instruction's parameters into 3
            # splitted_actual_instruction = [x.replace(",", "") for x in actual_instruction.split(" ")]
            # row_to_return['rd'] = splitted_actual_instruction[1]
            # row_to_return['rs1'] = splitted_actual_instruction[2]
            # row_to_return['rs2'] = ""
            # Check if rs2 exists
            # if len(splitted_actual_instruction) >= 4:
                # row_to_return['rs2'] = splitted_actual_instruction[3]
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


                # Parse memory and value
                affected_memory = int(address, 2)
                value_to_store = int(value, 2)
                first_affected_memory_in_hex = "{0:0>8X}".format(affected_memory)
                second_affected_memory_in_hex = "{0:0>8X}".format((affected_memory + int('1', 2)))
                third_affected_memory_in_hex = "{0:0>8X}".format((affected_memory + int('10', 2)))
                fourth_affected_memory_in_hex = "{0:0>8X}".format((affected_memory + int('11', 2)))

                # value to save to data segment
                memory_value_in_hex = "{0:0>8X}".format(value_to_store)

                # Split into 4, two hex digit strings
                memory_value_splitted_into_four_two_hex_digits = [(memory_value_in_hex[i:i+2]) for i in range(0, len(memory_value_in_hex), 2)]
                self.data_segment_dict[first_affected_memory_in_hex] = memory_value_splitted_into_four_two_hex_digits[3]
                self.data_segment_dict[second_affected_memory_in_hex] = memory_value_splitted_into_four_two_hex_digits[2]
                self.data_segment_dict[third_affected_memory_in_hex] = memory_value_splitted_into_four_two_hex_digits[1]
                self.data_segment_dict[fourth_affected_memory_in_hex] = memory_value_splitted_into_four_two_hex_digits[0]


                print(f'Address To Store: {affected_memory}, Value: {value_to_store}')

                # self.data_segment_dict[address_to_store]['value'] = value
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
                    msg = f"Line: {int(row['line_number'])}, Error: {jump_inst} was never declared."
                    return msg
                # Offset =  (jump instruction address - current address) / 2
                immediate = (int(self.jump_instructions[jump_inst], 2) - int(row['address'], 2)) // 2
                original_binary = bin(immediate & 0xfff)[2:].zfill(12)
                if immediate > -1:
                    immediate = bin(immediate)[2:].zfill(12)[::-1]
                else:
                    immediate = bin(immediate & 0xfff)[2:][::-1]  # for two's complement
                # Get the 4 parts of the immediate value
                imm_12 = immediate[11]
                imm_10_5 = immediate[5:10][::-1]
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
                # self.binary_table_df.at[index, "pending_jump"] = None
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
                    msg = f"Line: {int(row['line_number'])}, Error: {variable_name} was never declared."
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
                    'actual_command': row['actual_command'],
                    'line_number': row['line_number'],
                    'pending_jump': row['pending_jump'],
                    'pending_variable': None,
                    'rd': row['rd'],
                    'rs1': row['rs1'],
                    'rs2': row['rs2']
                }
                if self.test:
                    print("#" * 100)
                    print("START UPDATE VARIABLE")
                    print("#" * 100)
                    print(f"Will update binary for pending variable '{variable_name}' with values:")
                    print(row_to_return)
                    print("Before update:")
                    self.print_formatted_table()
                for key, value in row_to_return.items():
                    self.binary_table_df.at[index, key] = value
                if self.test:
                    print("After update:")
                    self.print_formatted_table()
                    print("#" * 100)
                    print("END UPDATE VARIABLE")
                    print("#" * 100)

    # After parsing, generate a rough draft of the pipeline map
    def generate_pipeline_map(self, is_initial, address_to_branch, starting_cycle_number):
        #
        if not is_initial:
            pipeline_columns_count = int(self.pipeline_map_df.columns[-1].replace('Cycle', '')) + 1  # len(self.pipeline_map_df.columns) - 2
            dropped_columns = ['Cycle ' + str(n) for n in range(starting_cycle_number, pipeline_columns_count)]
            # New parameters below
            # self.generate_pipeline_map(False, address_to_branch, int(dropped_columns[0].replace('Cycle ', '')) + 1)

            self.pipeline_map_df = self.pipeline_map_df.drop(dropped_columns, axis=1)
            self.old_pipeline_map_df = pd.merge(self.old_pipeline_map_df, self.pipeline_map_df, how='left',
                                                left_on=INITIAL_PIPELINE_COLUMNS, right_on=INITIAL_PIPELINE_COLUMNS)
            self.old_pipeline_map_df = self.old_pipeline_map_df.replace(np.nan, '', regex=True)

            # self.repopulate_pipeline_ui(self.temp_old_pipeline_map_df)
        # Reset pipeline map
        counter = 1
        additional_columns = 4
        previous_stalled = None
        initial_index = 0
        cycle_counter = starting_cycle_number
        total_initial_cycles = 4 + (len(self.binary_table_df.index))
        self.pipeline_map_df = pd.DataFrame(columns=INITIAL_PIPELINE_COLUMNS)
        if is_initial:
            self.old_pipeline_map_df = pd.DataFrame(columns=INITIAL_PIPELINE_COLUMNS)
        else:
            counter = starting_cycle_number
            initial_index = self.binary_table_df.index[self.binary_table_df['address'] == address_to_branch].tolist()[0]
            total_initial_cycles = starting_cycle_number + ((len(self.binary_table_df.index) - initial_index) + 4)
            # print(f'Address To Branch: {address_to_branch}')
            # print(f'Initial Index: {initial_index}')
            # print(f'Total Initial Cycles: {total_initial_cycles}')
        # Create columns for each clock cycle
        for cycle_number in range(starting_cycle_number, total_initial_cycles):
            cycle_name = 'Cycle ' + str(cycle_number)
            self.pipeline_map_df[cycle_name] = ''
        # Iterate over each row in the opcode table
        # to be added to the pipeline map
        # for index, row in self.binary_table_df.iterrows():
        for opcode_index in range(initial_index, self.binary_table_df.shape[0]):
            # Initialize row
            is_started = False
            previous_rows = None
            previous_rows_with_dependencies = None
            internal_counter = 1
            stall_count = 0
            current_row = self.binary_table_df.loc[opcode_index,:]
            current_rs1 = current_row['rs1']
            current_rs2 = current_row['rs2']
            num_rows_lookback = opcode_index - 5 if opcode_index > 4 else 0
            current_opcode = current_row['6-0'][2:].zfill(7)[::-1][0:7][::-1]
            row_to_add = {'address': current_row['address'], 'instruction': current_row['actual_command'], 'opcode': current_opcode}
            row_to_add_for_old_pipeline = row_to_add.copy()
            # If first row, don't get the previous
            if opcode_index != initial_index:
                previous_rows = self.binary_table_df.iloc[num_rows_lookback: opcode_index, :]
                previous_rows_with_dependencies = previous_rows[(previous_rows['rd'] != '') &
                                                                ((previous_rows['rd'] == current_rs1) |
                                                                (previous_rows['rd'] == current_rs2)) ]
            if is_initial or initial_index == 0:
                cycle_number = 1
                column_in_current_cycle = additional_columns + (len(self.binary_table_df.index))
            else:
                cycle_number = starting_cycle_number
                column_in_current_cycle = additional_columns + (len(self.binary_table_df.index) - initial_index )
                # print(f'Column in Current Cycle: {column_in_current_cycle}')
            # Add columns per cycle to the row
            while column_in_current_cycle > 0:
                cell = ''
                cycle_name = 'Cycle ' + str(cycle_number)
                # Start adding IF up to MEM for 5 columns
                if cycle_number == counter:
                    is_started = True
                # Internal counter is incremented 1 per iteration
                elif internal_counter > 5:
                    is_started = False
                if is_started:
                    if internal_counter == 1:
                        cell = 'IF'
                        if previous_stalled == 'ID':
                            new_cycle = 'Cycle ' + str(len(self.pipeline_map_df.columns) - 2)
                            # self.pipeline_map_df[new_cycle] = ''
                            # row_to_add[new_cycle] = ''
                            column_in_current_cycle += 1
                            additional_columns += 1
                            previous_stalled = None
                            internal_counter -= 1
                            counter += 1
                            cell = ''
                    elif internal_counter == 2:
                        cell = 'ID'
                        if previous_stalled == 'EX':
                            previous_stalled = 'ID'
                            internal_counter -= 1
                            cell = '*'
                    elif internal_counter == 3:
                        cell = 'EX'
                        if previous_stalled == 'MEM':
                            previous_stalled = 'EX'
                        if opcode_index != initial_index and previous_rows_with_dependencies.shape[0] > 0:
                            for index, row in previous_rows_with_dependencies.iterrows():
                                address_of_dependency = row['address']
                                current_row_with_dependency = self.pipeline_map_df[self.pipeline_map_df['address'] == address_of_dependency].reset_index(drop=True)
                                if current_row_with_dependency.shape[0] > 0:
                                    current_row_with_dependency_rd = self.binary_table_df[self.binary_table_df['address'] == address_of_dependency].reset_index(drop=True)
                                    current_row_with_dependency_rd = current_row_with_dependency_rd['rd'][0]
                                    current_row_with_dependency_opcode = current_row_with_dependency['opcode'][0]
                                    current_columns_of_row_with_dependency = current_row_with_dependency.columns
                                    step = None
                                    column_to_check = 1
                                    column_range_end = len(current_columns_of_row_with_dependency) - 2
                                    if current_row_with_dependency_opcode == LW_OPCODE and current_opcode != LW_OPCODE:
                                        if (current_opcode == SW_OPCODE and current_row_with_dependency_rd == current_rs1) or \
                                            current_opcode != SW_OPCODE:
                                            step = 'MEM'
                                    elif current_row_with_dependency_opcode in [ALU_ALU_OPCODE, ALU_IMM_OPCODE] and \
                                        current_opcode not in[LW_OPCODE, SW_OPCODE]:
                                        step = 'EX'
                                    elif current_row_with_dependency_opcode in [ALU_ALU_OPCODE, ALU_IMM_OPCODE] and \
                                        current_opcode in [SW_OPCODE, LW_OPCODE] and current_rs1 == current_row_with_dependency_rd:
                                        step = 'EX'
                                    if step:
                                        if not is_initial:
                                            column_to_check = starting_cycle_number
                                            column_range_end = starting_cycle_number + column_range_end - 1
                                        for col_num in range(column_to_check, column_range_end):
                                            if current_row_with_dependency['Cycle ' + str(col_num)][0] == step:
                                                if cycle_number <= col_num:
                                                    stall_count = (col_num - cycle_number) + 1
                                                    previous_stalled = step
                                                    internal_counter -= 1
                                                    cell = '*'
                    elif internal_counter == 4:
                        cell = 'MEM'
                        if opcode_index != initial_index and previous_rows_with_dependencies.shape[0] > 0:
                            for index, row in previous_rows_with_dependencies.iterrows():
                                address_of_dependency = row['address']
                                current_row_with_dependency = self.pipeline_map_df[self.pipeline_map_df['address'] == address_of_dependency].reset_index(drop=True)
                                if current_row_with_dependency.shape[0] > 0:
                                    current_row_with_dependency_rd = self.binary_table_df[self.binary_table_df['address'] == address_of_dependency].reset_index(drop=True)
                                    current_row_with_dependency_rd = current_row_with_dependency_rd['rd'][0]
                                    current_row_with_dependency_opcode = current_row_with_dependency['opcode'][0]
                                    current_columns_of_row_with_dependency = current_row_with_dependency.columns
                                    step = None
                                    column_to_check = 1
                                    column_range_end = len(current_columns_of_row_with_dependency) - 2
                                    if current_row_with_dependency_opcode == LW_OPCODE and current_rs1 == current_row_with_dependency_rd:
                                        step = 'MEM'
                                    if step:
                                        if not is_initial:
                                            column_to_check = starting_cycle_number
                                            column_range_end = starting_cycle_number + column_range_end - 1
                                        for col_num in range(column_to_check, column_range_end):
                                            if current_row_with_dependency['Cycle ' + str(col_num)][0] == step:
                                                if cycle_number <= col_num:
                                                    stall_count = (col_num - cycle_number) + 1
                                                    previous_stalled = step
                                                    internal_counter -= 1
                                                    cell = '*'
                        # Add extra column if the second to the last column is reached
                        if opcode_index == len(self.binary_table_df.index) - 1 and previous_stalled:
                            new_cycle = 'Cycle ' + str(cycle_number + 1)
                            self.pipeline_map_df[new_cycle] = ''
                            row_to_add[new_cycle] = ''
                            column_in_current_cycle += 1
                            additional_columns += 1
                    elif internal_counter == 5:
                        # print(f'{opcode_index}: Cycle Num: {cycle_number}, Stall: {stall_count}, Counter: {counter}')
                        cell = 'WB'
                    # if stall_count == 0:
                    internal_counter += 1
                    # else:
                    #     cell = '*'
                    #     stall_count -= 1
                # Add cycle to the row dictionary
                row_to_add[cycle_name] = cell
                cycle_number += 1
                column_in_current_cycle -= 1
            if is_initial:
                self.old_pipeline_map_df = self.old_pipeline_map_df.append(row_to_add_for_old_pipeline, ignore_index=True)
            # Add row to the pipeline map
            self.pipeline_map_df = self.pipeline_map_df.append(row_to_add, ignore_index=True)
            cycle_counter + 1
            counter += 1
        # print('*' * 100)
        # print(self.pipeline_map_df)
        if is_initial:
            self.repopulate_pipeline_ui(self.pipeline_map_df)
        else:
            # print(f'Cycle Counter: {cycle_counter}')
            # print('%' * 100)
            self.repopulate_pipeline_ui(pd.merge(self.old_pipeline_map_df, self.pipeline_map_df, how='left',
                                                left_on=INITIAL_PIPELINE_COLUMNS, right_on=INITIAL_PIPELINE_COLUMNS).replace(np.nan, '', regex=True))
            self.execute(cycle_counter)

    # Gets the string from the edit text box
    def evaluate(self):

        # reset
        self.reset_data()

        #Get lines from text field
        string_to_eval = self.edit_text.get("1.0", "end")
        list_of_commands = string_to_eval.splitlines()
        # Reset all parameters
        self.parsing_passed = True
        self.runtime_passed = True
        self.line_counter = 1
        self.is_data = False
        self.is_text = True
        self.variables = {}
        self.jump_instructions = {}
        self.pipeline_map_df = pd.DataFrame()
        self.old_pipeline_map_df = pd.DataFrame()
        self.current_data_segment = '0b000000000000' # 0x0000 in binary
        self.current_text_segment = '0b1000000000000' # 0x1000 in binary
        self.internal_registers_dict['PC']['value'] = self.current_text_segment
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
            for key, command in self.commands_dict.items():
                match_regex = re.match(command['regex'], formatted_command)
                if match_regex:
                    if self.is_text:
                        row_to_add = self.parse_instruction(key, match_regex.groups(), formatted_command, True)
                        if type(row_to_add) == str:
                            msg = f"Line: {self.line_counter}, Error: {row_to_add}"
                        else:
                            self.binary_table_df = self.binary_table_df.append(row_to_add, ignore_index=True)
                            if self.test: msg = match_regex.groups()
                    else:
                        msg = f"Line: {self.line_counter}, Error: No '.text' reserved word found before this instruction."
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
                                result = self.parse_instruction(key, match_regex.groups(), formatted_command, False)
                                if not result:
                                    msg = f"Line: {self.line_counter}, Error: Instruction '{match_regex[1]}' is already defined."
                            else:
                                msg = f"Line: {self.line_counter}, Error: No '.text' reserved word found before this instruction."
                        elif key in ['data', 'text']:
                            row_to_add = self.parse_instruction(key, match_regex.groups(), formatted_command, False)
                            if self.test: msg = match_regex.groups()
                        elif key == 'variable':
                            if self.is_data:
                                result = self.parse_instruction(key, match_regex.groups(), formatted_command, False)
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
                    self.parsing_passed = False
                    break
            else:
                if not match_regex:
                    msg = f'Line: {self.line_counter}, Error: Incorrect Syntax.'
                output_string = f'[{formatted_command}] : {msg}\n'
                results.append(output_string)
            self.line_counter += 1
        if self.parsing_passed:
            # Populate pending jumps
            has_error = self.populate_pending_jumps()
            if has_error:
                self.print_in_terminal(has_error)
                self.parsing_passed = False
            # Populate pending variables
            has_error = self.populate_pending_variables()
            if has_error:
                self.print_in_terminal(has_error)
                self.parsing_passed = False
        if self.parsing_passed:
            if self.test:
                self.print_in_terminal(results)
            self.print_formatted_table()
            if not self.test:
                self.print_in_terminal('Success in parsing.\n')
            # print('=' * 100)
            # print('Jump Instructions:')
            # self.print_jump_intructions()
            # print('=' * 100)
            # print('Declared Variables:')
            # self.print_variables()
            # print('=' * 100)
            # print('Opcodes:')
            # self.print_formatted_table()
            # print('=' * 100)
            self.generate_pipeline_map(True, None, 1)
        self.repopulate_labels_ui()
        self.repopulate_text_segment_ui()
        self.repopulate_data_segment_ui()
        self.repopulate_internal_register_ui()



    def execute(self, cycle_number = 1):

        def represents_int(s):
            try:
                int(s)
                return True
            except ValueError:
                return False

        def twos_comp(n, bits):
            s = bin(n & int("1"*bits, 2))[2:]
            return ("{0:0>%s}" % (bits)).format(s)

        def to_signed_integer(integer, bit_size = 32):
            unsigned = integer % 2**bit_size
            if unsigned >= 2**(bit_size-1):
                signed = unsigned - 2**bit_size
            else:
                signed = unsigned
            return signed

        # Add pipeline cycle instructions to list to be executed
        self.current_pipeline_instructions = []
        cycle_inside_pipeline_instructions = cycle_number

        for column in self.pipeline_map_df.columns[3:]:
            self.current_pipeline_instructions.append(cycle_inside_pipeline_instructions)
            cycle_inside_pipeline_instructions += 1
            for cell in self.pipeline_map_df[column]:
                if cell != '': self.current_pipeline_instructions.append(cell)

        # Add buffer to last cycle
        self.current_pipeline_instructions.append(-99)

        #
        # print('Instructions List:')
        # print(self.current_pipeline_instructions)

        integer_only_current_pipeline_instructions = [e for e in self.current_pipeline_instructions if isinstance(e, int)]

        address_to_branch = ''
        check_a_cycle = False
        self.will_jump = False
        if_instruction = None
        id_instruction = None
        if_branch = None
        id_branch = None
        pc_row = None

        if check_a_cycle:
            self.print_formatted_table()
            print('*' * 100)
            print('Jump Instructions: ')
            self.print_jump_intructions()
            print('*' * 100)


        stall_cycle = None

        # Iterate through each cycle instruction in the pipeline map
        for cycle_instruction in self.current_pipeline_instructions:

            self.repopulate_internal_register_ui()

            if cycle_instruction == '*':
                stall_cycle = cycle_number
                continue

            elif represents_int(cycle_instruction):

                # Attempt to fix highlighting
                # if cycle_number > 4 \
                #         and pc_row is not None \
                #         and integer_only_current_pipeline_instructions.index(cycle_number) > 3:
                if cycle_number > 4 \
                        and pc_row is not None \
                        and integer_only_current_pipeline_instructions.index(cycle_number) > 3:

                    if stall_cycle is not None:
                        if stall_cycle + 1 == cycle_number or stall_cycle == cycle_number:
                            # and stall_cycle + 2 > cycle_number
                            self.wait_line_by_line(cycle_number, pc_row['address'][0])
                        elif stall_cycle + 2 == cycle_number:
                            stall_cycle = None

                    elif stall_cycle is None:
                        self.wait_line_by_line(cycle_number, pc_row['address'][0])





                cycle_number = cycle_instruction
                continue

            if cycle_instruction == 'IF':


                self.execute_internal_counter = 4

                pc_row = self.binary_table_df[(self.binary_table_df['address'] == self.internal_registers_dict['PC']['value'])].reset_index(drop=True)
                if_instruction = pc_row['instruction'][0]
                if_branch = pc_row['pending_jump'][0]
                thirty_one_to_twenty_five = pc_row['31-25'][0][2:].zfill(7)[::-1][0:7][::-1]
                twenty_four_to_twenty = pc_row['24-20'][0][2:].zfill(5)[::-1][0:5][::-1]
                nineteen_to_fifteen = pc_row['19-15'][0][2:].zfill(5)[::-1][0:5][::-1]
                fourteen_to_twelve = pc_row['14-12'][0][2:].zfill(3)[::-1][0:3][::-1]
                eleven_to_seven = pc_row['11-7'][0][2:].zfill(5)[::-1][0:5][::-1]
                six_to_zero = pc_row['6-0'][0][2:].zfill(7)[::-1][0:7][::-1]

                concatenated = thirty_one_to_twenty_five + twenty_four_to_twenty + nineteen_to_fifteen + fourteen_to_twelve + eleven_to_seven + six_to_zero
                self.internal_registers_dict['IF/ID.IR']['value'] = concatenated # Load the opcode in binary
                self.internal_registers_dict['PC']['value'] =  format(int(pc_row['address'][0], 2) + int ('100', 2), '#014b') # Increment by 4
                self.internal_registers_dict['IF/ID.NPC']['value'] =  self.internal_registers_dict['PC']['value']
                # Old branch checking
                # if self.internal_registers_dict['EX/MEM.COND']['value'] == '1' and self.internal_registers_dict['EX/MEM.ALUOUTPUT']['value'] in self.jump_instructions.values():
                #     self.internal_registers_dict['PC']['value'] = self.internal_registers_dict['EX/MEM.ALUOUTPUT']
                #     self.internal_registers_dict['IF/ID.NPC']['value'] = self.internal_registers_dict['EX/MEM.ALUOUTPUT']
                # else:
                #     self.internal_registers_dict['PC']['value'] =  format(int(pc_row['address'][0], 2) + int ('100', 2), '#014b') # Increment by 4
                #     self.internal_registers_dict['IF/ID.NPC']['value'] =  self.internal_registers_dict['PC']['value']

                if check_a_cycle:
                    print(f"Cycle: {cycle_instruction}")
                    print(f"IR: {self.internal_registers_dict['IF/ID.IR']['value']}")
                    print(f"PC: {self.internal_registers_dict['PC']['value']}")
                    print('=' * 100)

            elif cycle_instruction == 'ID':
                self.execute_internal_counter -= 1

                # Fix
                id_branch = if_branch
                id_instruction = if_instruction
                six_to_zero = self.internal_registers_dict['IF/ID.IR']['value'][::-1][0:7][::-1]
                eleven_to_seven = pc_row['11-7'][0][2:].zfill(5)[::-1][0:5][::-1] # Fix
                nineteen_to_fifteen = self.internal_registers_dict['IF/ID.IR']['value'][::-1][15:20][::-1]
                twenty_four_to_twenty = self.internal_registers_dict['IF/ID.IR']['value'][::-1][20:25][::-1] # Fix
                thirty_one_to_twenty_five = self.internal_registers_dict['IF/ID.IR']['value'][::-1][25:32][::-1]

                # Load rs1 and rs2
                register_a = 'x' + str(int(nineteen_to_fifteen, 2))
                register_b = 'x' + str(int(twenty_four_to_twenty, 2))

                register_a = self.registers_dict[register_a]['value'] # in binary
                register_b = self.registers_dict[register_b]['value'] # in binary

                # print(f'Register A: {register_a}')
                # print(f'Register B: {register_b}')
                # print('*' * 100)

                self.internal_registers_dict['ID/EX.A']['value'] = register_a
                self.internal_registers_dict['ID/EX.B']['value'] = register_b
                self.internal_registers_dict['ID/EX.NPC']['value'] = self.internal_registers_dict['IF/ID.NPC']['value']
                self.internal_registers_dict['ID/EX.IR']['value'] = self.internal_registers_dict['IF/ID.IR']['value']

                if six_to_zero == BRANCH_OPCODE: # branch

                    self.internal_registers_dict['ID/EX.IMM']['value'] = thirty_one_to_twenty_five[0] + eleven_to_seven[4] + thirty_one_to_twenty_five[1:] + eleven_to_seven[0:4]

                elif six_to_zero == SW_OPCODE: # sw

                    self.internal_registers_dict['ID/EX.IMM']['value'] = thirty_one_to_twenty_five + eleven_to_seven

                    # print(f'SW Imme: {thirty_one_to_twenty_five + eleven_to_seven}')

                else: # alu instruction or lw

                    self.internal_registers_dict['ID/EX.IMM']['value'] = thirty_one_to_twenty_five + twenty_four_to_twenty

                    # print(f'Instruction: {id_instruction}, Value: {thirty_one_to_twenty_five + twenty_four_to_twenty}')

                if check_a_cycle:
                    print(f"Cycle: {cycle_instruction}")
                    print(f"A: {self.internal_registers_dict['ID/EX.A']['value']}")
                    print(f"B: {self.internal_registers_dict['ID/EX.B']['value']}")
                    print(f"NPC: {self.internal_registers_dict['ID/EX.NPC']['value']}")
                    # print(f"IR: {self.internal_registers_dict['ID/EX.IR']['value']}")
                    print(f"IMM: {self.internal_registers_dict['ID/EX.IMM']['value']}")
                    print('=' * 100)

            elif cycle_instruction == 'EX':
                self.execute_internal_counter -= 1

                self.internal_registers_dict['EX/MEM.IR']['value'] = self.internal_registers_dict['ID/EX.IR']['value']
                self.internal_registers_dict['EX/MEM.B']['value'] = self.internal_registers_dict['ID/EX.B']['value']
                self.internal_registers_dict['EX/MEM.COND']['value'] = '0'
                six_to_zero = self.internal_registers_dict['EX/MEM.IR']['value'][::-1][0:7][::-1]
                eleven_to_seven = self.internal_registers_dict['EX/MEM.IR']['value'][::-1][7:12][::-1]
                nineteen_to_fifteen = self.internal_registers_dict['EX/MEM.IR']['value'][::-1][15:20][::-1]
                twenty_four_to_twenty = self.internal_registers_dict['EX/MEM.IR']['value'][::-1][20:25][::-1] # Fix
                thirty_one_to_twenty_five = self.internal_registers_dict['EX/MEM.IR']['value'][::-1][25:32][::-1]
                result = 0

                register_a = 'x' + str(int(nineteen_to_fifteen, 2))
                register_b = 'x' + str(int(twenty_four_to_twenty, 2))
                register_a = self.registers_dict[register_a]['value'] # in binary
                register_b = self.registers_dict[register_b]['value'] # in binary
                register_a_in_binary = register_a
                register_b_in_binary = register_b

                # Convert to two's complement
                register_a = int(register_a, 2)
                register_a = to_signed_integer(register_a, 32)
                register_b = int(register_b, 2)
                register_b = to_signed_integer(register_b, 32)

                if six_to_zero == ALU_ALU_OPCODE:

                    if id_instruction == 'add':
                        # performs addition of rs1 and rs2. Arithmetic overflow is ignored,
                        # and the low 32 bits of the result is written in rd.
                        result = register_a + register_b
                    elif id_instruction == 'slt':
                        # SLT (set if less than) performs signed compare, places the value 1 in
                        # register rd if register rs1 < rs2, 0 otherwise.
                        result = 1 if register_a < register_b else 0
                    elif id_instruction == 'sll':
                        # SLL (shift left logical)- the operand to be shifted is in rs1 by the shift
                        # amount held in the lower 5 bits of register rs2 and the result is placed in rd.
                        # Zeros are shifted into the lower bits.
                        # Get five lower bits and cast to int
                        lower_five_bits = to_signed_integer(int(register_b_in_binary[-5:], 2), 32)
                        # add zeroes to the right of the subtring
                        shifted_and_padded_substring = register_a_in_binary + ("0" * lower_five_bits)
                        # only get the last 32 bits
                        result = to_signed_integer(int(shifted_and_padded_substring[-32:], 2), 32)
                    elif id_instruction == 'srl':
                        # SLL (shift left logical)- the operand to be shifted is in rs1 by the shift amount
                        # held in the lower 5 bits of register rs2 and the result is placed in rd.
                        # Zeros are shifted into the lower bits.
                        # Get five lower bits
                        lower_five_bits = to_signed_integer(int(register_b_in_binary[-5:], 2), 32)
                        # remove the lower bits as required, then add zeroes to the left of the subtring (padding to 32 bits)
                        shifted_and_padded_substring = register_a_in_binary[0: len(register_a_in_binary) - lower_five_bits].zfill(32)
                        # only get the last 32 bits
                        result = to_signed_integer(int(shifted_and_padded_substring[-32:], 2), 32)
                    elif id_instruction == 'and':
                        # AND is a logical operation that performs bitwise AND on registers rs1 and rs2
                        # place the result in rd.
                        result = register_a & register_b
                    elif id_instruction == 'or':
                        # OR is a logical operation that performs bitwise OR on registers
                        # rs1 and rs2 place the result in rd
                        result = register_a | register_b
                    elif id_instruction == 'xor':
                        # XOR is a logical operation that performs bitwise XOR on registers
                        # rs1 and rs2 place the result in rd.
                        result = register_a ^ register_b
                    rd = 'x' + str(int(eleven_to_seven, 2))
                    if rd == 'x0': result = 0
                    result = twos_comp(result, 32)
                    self.registers_dict[rd]['value'] = result # forwarding
                    self.internal_registers_dict['EX/MEM.ALUOUTPUT']['value'] = result

                    # print(f"rd: {rd}, value: {self.registers_dict[rd]['value']}")
                    # print(f'Register A: {register_a}')
                    # print(f'Register B: {register_b}')

                elif six_to_zero == ALU_IMM_OPCODE:
                    immediate_in_binary = self.internal_registers_dict['ID/EX.IMM']['value']
                    imme = int(immediate_in_binary, 2)
                    imme = to_signed_integer(imme, 12)
                    if id_instruction == 'addi':
                        result = register_a + imme
                    elif id_instruction == 'slti':
                        # SLTI (set if less than) places the value 1 in register rd if register rs1 is less than
                        # the sign extended immediate when both are treated as signed
                        # integers; else 0 is written to rd.
                        result = 1 if register_a < imme else 0
                    elif id_instruction == 'slli':
                        # SLLI (shift left logical immediate) -
                        # the operand to be shifted is in rs1 and
                        # the shift amount is encoded in the lower 5
                        # bits of the immediate field and the result is
                        # placed in rd. Zeros are shifted into the lower bits.
                        # Get five lower bits and cast to int
                        lower_five_bits = to_signed_integer(int(immediate_in_binary[-5:], 2), 32)
                        # add zeroes to the right of the subtring
                        shifted_and_padded_substring = register_a_in_binary + ("0" * lower_five_bits)
                        # only get the last 32 bits
                        result = to_signed_integer(int(shifted_and_padded_substring[-32:], 2), 32)
                    elif id_instruction == 'srli':
                        # SRLI (shift right logical immediate)- the operand to be shifted is in rs1 and the shift amount
                        # is encoded in the lower 5 bits of the immediate field and the result is placed in rd.
                        # Zeros are shifted into the upper bits.
                        # Get five lower bits
                        lower_five_bits = to_signed_integer(int(immediate_in_binary[-5:], 2), 32)
                        # remove the lower bits as required, then add zeroes to the left of the subtring (padding to 32 bits)
                        shifted_and_padded_substring = register_a_in_binary[0: len(register_a_in_binary) - lower_five_bits].zfill(32)
                        # only get the last 32 bits
                        result = to_signed_integer(int(shifted_and_padded_substring[-32:], 2), 32)
                    elif id_instruction == 'andi':
                        # ANDI is a logical operation that
                        # performs bitwise AND on
                        # register rs1 and the sign- extended 12-bit immediate, place the result in rd.
                        result = register_a & imme
                    elif id_instruction == 'ori':
                        # ORI is a logical operation that performs bitwise OR on register rs1 and
                        # the sign- extended 12-bit immediate place the result in rd.
                        result = register_a | imme
                    elif id_instruction == 'xori':
                        # XORI is a logical operation that performs bitwise XOR on register rs1 and
                        # the sign- extended 12-bit immediate place the result in rd.
                        result = register_a ^ imme
                    rd = 'x' + str(int(eleven_to_seven, 2))
                    if rd == 'x0': result = 0
                    result = twos_comp(result, 32)
                    self.registers_dict[rd]['value'] = result # forwarding
                    self.internal_registers_dict['EX/MEM.ALUOUTPUT']['value'] = result
                    # print(f"rd: {rd}, value: {self.registers_dict[rd]['value']}")
                    # print(f'Register A: {register_a}')
                    # print(f'Immediate: {imme}')

                elif six_to_zero == BRANCH_OPCODE:
                    cond = '0'
                    if id_instruction == 'beq' and register_a == register_b:
                        cond = '1'
                        self.will_jump = True
                    elif id_instruction == 'bne' and register_a != register_b:
                        cond = '1'
                        self.will_jump = True
                    elif id_instruction == 'blt' and register_a < register_b:
                        cond = '1'
                        self.will_jump = True
                    elif id_instruction == 'bge' and register_a >= register_b:
                        cond = '1'
                        self.will_jump = True
                    # print(f'Instruction {id_instruction}')
                    # print(f'Register A: {register_a}')
                    # print(f'Register B: {register_b}')
                    self.internal_registers_dict['EX/MEM.COND']['value'] = cond
                    address_to_branch = self.jump_instructions[id_branch]
                    self.internal_registers_dict['EX/MEM.ALUOUTPUT']['value'] = twos_comp(int(address_to_branch, 2), 32)

                elif six_to_zero in [SW_OPCODE, LW_OPCODE]:

                    immediate_in_binary = self.internal_registers_dict['ID/EX.IMM']['value']

                    # if six_to_zero == LW_OPCODE:
                    #     print('*' * 100)
                    #     print(f'Register A: {register_a}')
                    #     print(f'Register B: {register_b}')
                    #     print(f'Immediate: {immediate_in_binary}')

                    immediate_in_binary = int(immediate_in_binary, 2)
                    immediate_in_binary = to_signed_integer(immediate_in_binary, 12)
                    self.internal_registers_dict['EX/MEM.ALUOUTPUT']['value'] = twos_comp(register_a + immediate_in_binary, 32)

                if check_a_cycle:
                    print(f"Cycle: {cycle_instruction}")
                    print(f"COND: {self.internal_registers_dict['EX/MEM.COND']['value']}")
                    print(f"ALUOUTPUT: {self.internal_registers_dict['EX/MEM.ALUOUTPUT']['value']}")
                    print('=' * 100)

            elif cycle_instruction == 'MEM':
                self.execute_internal_counter -= 1

                # Drop the data in succeeding columns then branch
                if self.will_jump:
                    self.will_jump = False

                    # if not check_a_cycle:
                    #     print(f"Cycle: {cycle_instruction}")
                    #     print(f"New PC for New Pipeline: {address_to_branch}")
                    #     print('*' * 100)
                    #     address_to_branch = ''
                    cycles_to_be_dropped = cycle_number + 1
                    # pipeline_columns_count = int(self.pipeline_map_df.columns[-1].replace('Cycle' , '')) + 1 # len(self.pipeline_map_df.columns) - 2
                    self.internal_registers_dict['PC']['value'] = address_to_branch
                    self.internal_registers_dict['IF/ID.NPC']['value'] =  address_to_branch
                    # dropped_columns = ['Cycle ' + str(n) for n in range(cycles_to_be_dropped, pipeline_columns_count)]
                    # print('$' * 100)
                    # print(f'Cycle number: {cycles_to_be_dropped}, Pipeline Columns: {pipeline_columns_count}')
                    # print(self.pipeline_map_df)
                    # print(f'Columns to be dropped: {dropped_columns}')
                    # print('^' * 100)
                    # self.pipeline_map_df = self.pipeline_map_df.drop(dropped_columns, axis = 1)
                    # self.old_pipeline_map_df = pd.merge(self.old_pipeline_map_df, self.pipeline_map_df, how = 'left', left_on = INITIAL_PIPELINE_COLUMNS, right_on = INITIAL_PIPELINE_COLUMNS)
                    # self.old_pipeline_map_df = self.old_pipeline_map_df.replace(np.nan, '', regex = True)

                    # Bandaid solution, did not deep dive
                    print(f"IN MEM INT @ cycle number: {cycle_number}")
                    self.wait_line_by_line(cycle_number, pc_row['address'][0])


                    self.generate_pipeline_map(False, address_to_branch, cycles_to_be_dropped)
                    # print(f'Register x3: {self.registers_dict["x3"]}')
                    # # Only temporary, for viewing
                    # self.old_pipeline_map_df = pd.merge(self.old_pipeline_map_df, self.pipeline_map_df, how = 'left', left_on = INITIAL_PIPELINE_COLUMNS, right_on = INITIAL_PIPELINE_COLUMNS)
                    # self.old_pipeline_map_df = self.old_pipeline_map_df.replace(np.nan, '', regex = True)
                    # self.repopulate_pipeline_ui(self.old_pipeline_map_df)
                    # print(self.old_pipeline_map_df)




                    return

                six_to_zero = self.internal_registers_dict['EX/MEM.IR']['value'][::-1][0:7][::-1]
                eleven_to_seven = self.internal_registers_dict['EX/MEM.IR']['value'][::-1][7:12][::-1]
                self.internal_registers_dict['MEM/WB.IR']['value'] = self.internal_registers_dict['EX/MEM.IR']['value']
                self.internal_registers_dict['MEM/WB.ALUOUTPUT']['value'] = self.internal_registers_dict['EX/MEM.ALUOUTPUT']['value']
                self.internal_registers_dict['MEM/MEMORY AFFECTED']['value'] = '0'
                self.internal_registers_dict['MEM/MEMORY VALUE']['value'] = '0'
                self.internal_registers_dict['MEM/WB.LMD']['value'] = '0'

                if six_to_zero == SW_OPCODE:

                    self.internal_registers_dict['MEM/MEMORY AFFECTED']['value'] = self.internal_registers_dict['EX/MEM.ALUOUTPUT']['value']
                    self.internal_registers_dict['MEM/MEMORY VALUE']['value'] = self.internal_registers_dict['EX/MEM.B']['value']
                    affected_memory = int(self.internal_registers_dict['MEM/MEMORY AFFECTED']['value'], 2)

                    if affected_memory > int(DATA_SEGMENT_LIMIT, 2):
                        error_message = f'Runtime Error, Line {(cycle_number - 4)}: Address is greater than the data segment limit.'
                        self.print_in_terminal(error_message)
                        self.runtime_passed = False
                        break

                    first_affected_memory_in_hex = "{0:0>8X}".format(affected_memory)
                    second_affected_memory_in_hex = "{0:0>8X}".format((affected_memory + int('1', 2)))
                    third_affected_memory_in_hex = "{0:0>8X}".format((affected_memory + int('10', 2)))
                    fourth_affected_memory_in_hex = "{0:0>8X}".format((affected_memory + int('11', 2)))
                    # value to save to data segment
                    memory_value_in_hex = "{0:0>8X}".format(int(self.internal_registers_dict['MEM/MEMORY VALUE']['value'], 2))
                    # Split into 4, two hex digit strings
                    memory_value_splitted_into_four_two_hex_digits = [(memory_value_in_hex[i:i+2]) for i in range(0, len(memory_value_in_hex), 2)]
                    self.data_segment_dict[first_affected_memory_in_hex] = memory_value_splitted_into_four_two_hex_digits[3]
                    self.data_segment_dict[second_affected_memory_in_hex] = memory_value_splitted_into_four_two_hex_digits[2]
                    self.data_segment_dict[third_affected_memory_in_hex] = memory_value_splitted_into_four_two_hex_digits[1]
                    self.data_segment_dict[fourth_affected_memory_in_hex] = memory_value_splitted_into_four_two_hex_digits[0]

                    # print(f"ALU Output: {self.internal_registers_dict['EX/MEM.ALUOUTPUT']['value']}")
                    # print(f'Address of data in memory: {address_of_data_from_memory}' )

                    # print(f'1st data: {first_data}')
                    # print(f'1st address: {first_address_of_data}')

                    # print(f'2nd data: {second_data}')
                    # print(f'2nd address: {second_address_of_data}')

                    # print(f'3rd data: {third_data}')
                    # print(f'3rd address: {third_address_of_data}')

                    # print(f'4th data: {forth_data}')
                    # print(f'4th address: {forth_address_of_data}')

                    # print(f'Register to update: {register_to_update}')
                    # print(f'LMD data in binary: {data_to_loaded_to_lmd}')

                elif six_to_zero == LW_OPCODE:
                    register_to_update = 'x' + str(int(eleven_to_seven, 2))
                    address_of_data_from_memory = int(self.internal_registers_dict['EX/MEM.ALUOUTPUT']['value'], 2)
                    # Get the 4 address based on the ALUOUTPUT
                    first_address_of_data = "{0:0>8X}".format(address_of_data_from_memory)
                    second_address_of_data = "{0:0>8X}".format((address_of_data_from_memory + int('1', 2)))
                    third_address_of_data = "{0:0>8X}".format((address_of_data_from_memory + int('10', 2)))
                    forth_address_of_data = "{0:0>8X}".format((address_of_data_from_memory + int('11', 2)))
                    # Get the data from memory using data
                    first_data = self.data_segment_dict[first_address_of_data]
                    second_data = self.data_segment_dict[second_address_of_data]
                    third_data = self.data_segment_dict[third_address_of_data]
                    forth_data = self.data_segment_dict[forth_address_of_data]
                    data_to_loaded_to_lmd = bin(int(forth_data + third_data + second_data + first_data, 16))[2:]


                    # print(f"ALU Output: {self.internal_registers_dict['EX/MEM.ALUOUTPUT']['value']}")
                    # print(f'Address of data in memory: {address_of_data_from_memory}' )

                    # print(f'1st data: {first_data}')
                    # print(f'1st address: {first_address_of_data}')

                    # print(f'2nd data: {second_data}')
                    # print(f'2nd address: {second_address_of_data}')

                    # print(f'3rd data: {third_data}')
                    # print(f'3rd address: {third_address_of_data}')

                    # print(f'4th data: {forth_data}')
                    # print(f'4th address: {forth_address_of_data}')

                    # print(f'Register to update: {register_to_update}')
                    # print(f'LMD data in binary: {data_to_loaded_to_lmd}')

                    if register_to_update == 'x0':
                        data_to_loaded_to_lmd = '0'

                    self.internal_registers_dict['MEM/WB.LMD']['value'] = data_to_loaded_to_lmd
                    self.registers_dict[register_to_update]['value'] = data_to_loaded_to_lmd

                if check_a_cycle:
                    print(f"Cycle: {cycle_instruction}")
                    print(f"ALUOUTPUT: {self.internal_registers_dict['MEM/WB.ALUOUTPUT']['value']}")
                    print(f"LMD: {self.internal_registers_dict['MEM/WB.LMD']['value']}")
                    print(f"MEMORY AFFECTED: {self.internal_registers_dict['MEM/MEMORY AFFECTED']['value']}")
                    print(f"MEMORY VALUE: {self.internal_registers_dict['MEM/MEMORY VALUE']['value']}")
                    print('=' * 100)

                self.repopulate_data_segment_ui()
                self.repopulate_register_ui()
                # print(pc_row)
                # self.wait_line_by_line(cycle_number, pc_row['address'][0])

            elif cycle_instruction == 'WB':
                self.execute_internal_counter -= 1

                six_to_zero = self.internal_registers_dict['MEM/WB.IR']['value'][::-1][0:7][::-1]
                eleven_to_seven = self.internal_registers_dict['MEM/WB.IR']['value'][::-1][7:12][::-1]

                if six_to_zero in [LW_OPCODE,  ALU_ALU_OPCODE, ALU_IMM_OPCODE] :
                    if six_to_zero == LW_OPCODE:
                        self.internal_registers_dict['WB/REGISTER AFFECTED']['value'] = eleven_to_seven
                        self.internal_registers_dict['WB/REGISTER VALUE']['value'] = self.internal_registers_dict['MEM/WB.ALUOUTPUT']['value'] # yung value ng address na ito
                    else:
                        self.internal_registers_dict['WB/REGISTER AFFECTED']['value'] = eleven_to_seven
                        self.internal_registers_dict['WB/REGISTER VALUE']['value'] = self.internal_registers_dict['MEM/WB.ALUOUTPUT']['value']
                    if check_a_cycle:
                        print(f"Cycle: {cycle_instruction}")
                        print(f"REGISTER: {self.internal_registers_dict['WB/REGISTER AFFECTED']['value']}")
                        print(f"VALUE: {self.internal_registers_dict['WB/REGISTER VALUE']['value']}")
                        print('=' * 100)
                else:
                    self.internal_registers_dict['WB/REGISTER AFFECTED']['value'] = '0'
                    self.internal_registers_dict['WB/REGISTER VALUE']['value'] = '0'

                self.repopulate_data_segment_ui()
                self.repopulate_register_ui()

                # print(f'Cycle number: {cycle_number}, Max: {cycle_inside_pipeline_instructions}')
                if cycle_number == cycle_inside_pipeline_instructions - 1:
                    self.old_pipeline_map_df = pd.merge(self.old_pipeline_map_df, self.pipeline_map_df, how = 'left', left_on = INITIAL_PIPELINE_COLUMNS, right_on = INITIAL_PIPELINE_COLUMNS)
                    self.old_pipeline_map_df = self.old_pipeline_map_df.replace(np.nan, '', regex = True)
                    self.repopulate_pipeline_ui(self.old_pipeline_map_df)
                # print(f"waiting...{cycle_number}")
                # self.line_button.wait_variable(self.line_incrementer)
                # print("done...")


        # print(self.pipeline_map_df)

if __name__ == "__main__":

    # region Declarables
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
    regex_store_instruction = r"[\s]+x(0|0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*((?!x(0|0?[1-9]|[12][0-9]|3[01]))[a-z_][\w]+|[-+]?0|[-+]?[1-9][0-9]*|0x[a-f0-9]+)?(\(x(0|0?[1-9]|[12][0-9]|3[01])\))?$"
    regex_integer_computation = r"[\s]+x(0|0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*x(0|0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*x(0|0?[1-9]|[12][0-9]|3[01])$"
    regex_integer_computation_immediate = r"[\s]+x(0|0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*x(0|0?[1-9]|[12][0-9]|3[01])[\s]*,[\s]*([-+]?0|[-+]?[1-9][0-9]*|0x[a-f0-9]+)$"
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

    sample_input = ['']

    addresses_to_load_dict = {}

    registers_dict = {
            "x0":  {"value": '0'},
            "x1":  {"value": '0'},
            "x2":  {"value": '0'},
            "x3":  {"value": '0'},
            "x4":  {"value": '0'},
            "x5":  {"value": '0'},
            "x6":  {"value": '0'},
            "x7":  {"value": '0'},
            "x8":  {"value": '0'},
            "x9":  {"value": '0'},
            "x10": {"value": '0'},
            "x11": {"value": '0'},
            "x12": {"value": '0'},
            "x13": {"value": '0'},
            "x14": {"value": '0'},
            "x15": {"value": '0'},
            "x16": {"value": '0'},
            "x17": {"value": '0'},
            "x18": {"value": '0'},
            "x19": {"value": '0'},
            "x20": {"value": '0'},
            "x21": {"value": '0'},
            "x22": {"value": '0'},
            "x23": {"value": '0'},
            "x24": {"value": '0'},
            "x25": {"value": '0'},
            "x26": {"value": '0'},
            "x27": {"value": '0'},
            "x28": {"value": '0'},
            "x29": {"value": '0'},
            "x30": {"value": '0'},
            "x31": {"value": '0'}
        }

# RISC-V pipeline test template (I) - check value
    sample_input.append("""
.text
main:
addi x9, x0, 0x008
addi x10,x0, 0x00C
addi x11, x0, 0x765
sll x12, x11, x10
srl x13, x11, x9
slli x22, x11, 0x004
srli x23, x11, 0x004
and x14, x11, x11
or x15, x11, x11
xor x16, x11, x11
slt x17,x10,x11
andi x24, x11, 0x0  
ori x25, x11, 0x0   
xori x26, x11, 0x0  
slti x27, x10, 0x010
""")

# RISC-V pipeline test template(II) - memory test 1/pipeline map
# load address 0x100 with word data 0x0a
# load address 0x104 with word data 0x0b
# load address 0x108 with word data 0x0c
    sample_input.append("""
.text
main:
lw x11, 0x100(x0)
lw x12, 0x104(x0)
add x13, x11, x12
sw x13, 0x108(x0)
FIN: 
addi x0, x0, 0
""")

# RISC-V pipeline test template(III) - memory test 2/pipeline map
    sample_input.append("""
.data
var1: .word 0x0a
var2: .word 0x0b
var3: .word 0x0c
.text
main:
lw x11, var1(x0)
lw x12, var2(x0)
add x13, x11, x12
sw x13, var3(x0)
FIN:
addi x0, x0, 0
""")

# RISC-V pipeline test template(IV) - pipeline map
    sample_input.append("""
.data
var1: .word 0x0a
var2: .word 0x0b
var3: .word 0x0c

.text
lw x6, var1(x0)
lw x7, var2(x0)
BLT x6, x7, L1
add x8, x6, x7
and x9, x6, x7
or x10, x6, x7
xor x11, x6, x7
BEQ x0, x0, L2
L1: 
ADDI x8, x7, 0x008
ANDI x9, x7, 0x00C
ORI x10, x7, 0x0FF
XORI x11, x7, 0x000
L2: 
SW x11, var3(x0)
""")

# RISC-V pipeline test template(V) - no branch internal register
# intialize addr 0x100 to word data 0x00000088
# intialize addr 0x104 to word data 0x00000099
# initialize x4=3;x5=4; x6=8;x11=3; x12=5;x14=6,x15=7
    sample_input.append("""
.text
beq x5, x6, L1
lw x11, 0x100(x0)
addi x12, x0, 0x004
sll x14, x11, x12
L1:
slt x15, x5, x6
sw x14, 0x104(x0)
""")

# RISC-V pipeline test template(VI) -branch internal register
# .data
# intialize addr 0x100 to word data 0x00000044
# intialize addr 0x104 to word data 0x00000077
# initialize x4=3; x5=4; x6=4; x11=3; x12=5;x14=6,x15=7
    sample_input.append("""
.text
beq x5, x6, L1
lw x11, 0x100(x0)
addi x12, x0, 0x004
sll x14, x11, x12
L1:
slt x15, x5, x6
sw x14, 0x104(x0)
""")

    # endregion Declarables

    testing_scenario = 5

    if testing_scenario == 2:

        # load address 0x100 with word data 0x0a
        addresses_to_load_dict['00000100'] = 'A'

        # load address 0x104 with word data 0x0b
        addresses_to_load_dict['00000104'] = 'B'

        # load address 0x108 with word data 0x0c
        addresses_to_load_dict['00000108'] = 'C'

    elif testing_scenario == 5:

        # intialize addr 0x100 to word data 0x00000088
        addresses_to_load_dict['00000100'] = '00000088'

        # intialize addr 0x104 to word data 0x00000099
        addresses_to_load_dict['00000104'] = '00000099'

        # initialize x4=3; x5=4; x6=8; x11=3; x12=5; x14=6,x15=7
        registers_dict['x4']['value'] = '11'
        registers_dict['x5']['value'] = '100'
        registers_dict['x6']['value'] = '1000'
        registers_dict['x11']['value'] = '11'
        registers_dict['x12']['value'] = '101'
        registers_dict['x14']['value'] = '110'
        registers_dict['x15']['value'] = '111'

    elif testing_scenario == 6:

        # intialize addr 0x100 to word data 0x00000044
        addresses_to_load_dict['00000100'] = '44'

        # intialize addr 0x104 to word data 0x00000077
        addresses_to_load_dict['00000104'] = '77'

        # initialize x4=3; x5=4; x6=4; x11=3; x12=5; x14=6,x15=7
        registers_dict['x4']['value'] = '11'
        registers_dict['x5']['value'] = '100'
        registers_dict['x6']['value'] = '100'
        registers_dict['x11']['value'] = '11'
        registers_dict['x12']['value'] = '101'
        registers_dict['x14']['value'] = '110'
        registers_dict['x15']['value'] = '111'

    if testing_scenario < 7:
        root = tk.Tk()
        app = Main(root, commands_dict, reserved_list, registers_dict, sample_input[testing_scenario], addresses_to_load_dict, False)
        root.mainloop()

