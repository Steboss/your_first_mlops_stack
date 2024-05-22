import pandas as pd


def process_iris(input_csv, output_csv):
    # Load the Iris dataset
    df = pd.read_csv(input_csv)

    # Calculate the mean of each column
    means = df.mean()

    # Save the results
    means.to_csv(output_csv)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process Iris dataset')
    parser.add_argument('--input-csv', type=str, help='Input CSV file path')
    parser.add_argument('--output-csv', type=str, help='Output CSV file path')
    args = parser.parse_args()

    process_iris(args.input_csv, args.output_csv)
