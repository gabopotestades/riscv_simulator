import pandas as pd

pipeline_map_df = pd.DataFrame(
                                [{
                                  'rd': 'x1',
                                  'rs1': 'x1',
                                  'rs2': 'x2'
                                  },
                                 {
                                  'rd': "x2",
                                  'rs1': 'x1',
                                  'rs2': 'x3'
                                  },
                                  {
                                        'rd': "x3",
                                        'rs1': 'x3',
                                        'rs2': 'x5'
                                 },
                                    {
                                        'rd': "x4",
                                        'rs1': 'x3',
                                        'rs2': 'x5'
                                    },
                                    {
                                        'rd': "x5",
                                        'rs1': 'x3',
                                        'rs2': 'x5'
                                    }
                               ])

number_of_rows = pipeline_map_df.shape[0]
for x in range(number_of_rows):
    current_row = pipeline_map_df.loc[x,:]
    current_row_rs1 = current_row["rs1"]
    current_row_rs2 = current_row["rs2"]

    if x != 0:
        print(f'current line: {current_row.tolist()}')
        print(f'My rd: {current_row["rd"]}')
        print(f'My rs1: {current_row_rs1}')
        print(f'My rs2: {current_row_rs2}')


        previous_rows = pipeline_map_df.iloc[0: x, :]

        # Check for dependencies
        # if(previous_rows['rd'] in [])
        previous_rows_with_dependencies = previous_rows[(previous_rows['rd'] == current_row_rs1) | (previous_rows['rd'] == current_row_rs2)]
        if previous_rows_with_dependencies.shape[0] > 0:
            print("My dependencies")
            print("HITS")
            print(previous_rows_with_dependencies)



        print()
        print()

#
#
# print(pipeline_map_df)

