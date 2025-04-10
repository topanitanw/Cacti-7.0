import pandas as pd
import sys

def transpose_csv(file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path, header=0)

    # Strip whitespace from column headers
    df.columns = df.columns.str.strip()

    # Transpose the DataFrame
    transposed_df = df.T

    # Print the transposed DataFrame to stdout
    print(transposed_df)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python transpose_csv_reader.py <csv_file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    transpose_csv(file_path)
