import pandas as pd


def process_iris(input_csv):
    # Load the Iris dataset
    df = pd.read_csv(input_csv)

    # Calculate the mean of each column
    sepal_length_mean = df.loc[:,'sepal.length'].mean()

    print(f"This is the mean {sepal_length_mean}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process Iris dataset')
    parser.add_argument('--input-csv', type=str, help='Input CSV file path')
    args = parser.parse_args()

    process_iris(args.input_csv)
