import pandas as pd
import os

# Specify the folder containing the CSV files
folder_path = 'folderpath'
output_file = 'concatenated_output.csv'

# List to hold DataFrames
dataframes = []

# Iterate over all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        # Read the CSV file and append it to the list
        df = pd.read_csv(file_path)
        dataframes.append(df)

# Concatenate all DataFrames in the list
concatenated_df = pd.concat(dataframes, ignore_index=True)

# Save the concatenated DataFrame to a new CSV file
concatenated_df.to_csv(output_file, index=False)

print(f"Successfully concatenated {len(dataframes)} files into '{output_file}'.")
