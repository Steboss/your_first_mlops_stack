import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from torch.utils.data import TensorDataset, DataLoader
from sklearn.preprocessing import StandardScaler
from urllib.parse import urlparse, urljoin, ParseResult
from pathlib import Path
import typer
import os
# gcs
import fsspec
import gcsfs

import pandas as pd
import logging

logging.getLogger().setLevel(logging.INFO)


class Net(nn.Module):
        def __init__(self):
            super(Net, self).__init__()
            self.fc1 = nn.Linear(4, 100)
            self.fc2 = nn.Linear(100, 3)

        def forward(self, x):
            x = torch.relu(self.fc1(x))
            x = self.fc2(x)
            return x


# HELPER FUNCTIONS
def load_data(data_path):
    r"""Load data from a bucket to local mode

    Args
    ---------
        data_path: str, input path where the data to be read are stored

    Returns
    ---------
        pandas dataframe: read data are stored in a pandas dataframe
    """
    logging.info(f"Data parsing {data_path}")
    data_path_as_url = urlparse(data_path)
    if data_path_as_url.scheme == "gs":
        dataset_location_path = urljoin(data_path_as_url.path, "poc_table")
        dataset_location_url = ParseResult(
            scheme=data_path_as_url.scheme,
            netloc=data_path_as_url.netloc,
            path=dataset_location_path,
            params=data_path_as_url.params,
            query=data_path_as_url.query,
            fragment=data_path_as_url.fragment,
        )
        dataset_location = dataset_location_url.geturl()
    else:
        data_location = Path(data_path)
        dataset_location = data_location / "poc_table"
    logging.info(f"Local data {dataset_location}")

    return pd.read_csv(dataset_location)


def main(data_path: str):
    df = load_data(data_path)
    logging.info("Preparing X and y")
    y = df["target"]
    X = df.drop(labels=["target"], axis=1)
    # Split dataset into training set and test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    # create output directory
    output_folder = os.getcwd() + "/outputs"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Convert to torch tensors
    X_train = torch.tensor(X_train, dtype=torch.float32)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.long)
    y_test = torch.tensor(y_test, dtype=torch.long)

    # Create datasets
    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)

    # Data loaders
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)

    model = Net()
    if torch.cuda.is_available():
        model.cuda()

    optimizer = optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.CrossEntropyLoss()

    def train(epoch):
        model.train()
        for batch_idx, (data, target) in enumerate(train_loader):
            if torch.cuda.is_available():
                data, target = data.cuda(), target.cuda()
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

            if batch_idx % 10 == 0:
                logging.info(f'Train Epoch: {epoch} [{batch_idx * len(data)}/{len(train_loader.dataset)} ({100. * batch_idx / len(train_loader):.0f}%)]\tLoss: {loss.item():.6f}')

    # Training for a few epochs
    for epoch in range(1, 6):
        train(epoch)


if __name__ == "__main__":
    typer.run(main)