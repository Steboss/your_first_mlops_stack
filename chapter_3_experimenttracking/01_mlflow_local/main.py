import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import lightning as L
from torch.nn import functional as F
import mlflow
import mlflow.pytorch
from datetime import datetime
from mlflow.tracking.client import MlflowClient


class Net(L.LightningModule):
    # NB: mlflow doesn't work for general pytorch models, only for LightningModule
    def __init__(self):
        """Constructor"""
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=5)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=5)
        self.dropout1 = nn.Dropout2d(0.25)
        self.dropout2 = nn.Dropout2d(0.5)
        self.fc1 = nn.Linear(1024, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        """Forward pass

        Args
            x: Input tensor
        """
        x = self.conv1(x)
        x = nn.functional.relu(nn.functional.max_pool2d(x, 2))
        x = self.conv2(x)
        x = nn.functional.relu(nn.functional.max_pool2d(self.dropout1(x), 2))
        x = torch.flatten(x, 1)
        x = self.fc1(self.dropout2(x))
        x = nn.functional.relu(x)

        return self.fc2(x)

    def cross_entropy_loss(self, logits, labels):
        """
        Initializes the loss function

        Returns:
            output: Initialized cross entropy loss function.
        """
        return F.nll_loss(logits, labels)

    def training_step(self, train_batch, batch_idx):
        """
        Training the data as batches and returns training loss on each batch

        Args:
            train_batch: Batch data
            batch_idx: Batch indices

        Returns:
            output - Training loss
        """
        x, y = train_batch
        logits = self.forward(x)
        loss = self.cross_entropy_loss(logits, y)
        return {"loss": loss}

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=0.02)


today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Data transformations and loaders
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

train_dataset = datasets.MNIST(root='./data', train=True, transform=transform, download=True)
test_dataset = datasets.MNIST(root='./data', train=False, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)

#model = Net().to(device)
mnist_model = Net()
# Define optimizer and loss function
optimizer = optim.Adam(mnist_model.parameters())
loss_fn = nn.CrossEntropyLoss()
trainer = L.Trainer(max_epochs=5)

experiment_name = "pytorch-lightning-MNIST" #127.0.0.1
client = MlflowClient(tracking_uri="http://localhost:5000")
experiment_exists = client.get_experiment_by_name(experiment_name)
if not experiment_exists:
    experiment_id = client.create_experiment(experiment_name)
else:
    experiment_id = experiment_exists.experiment_id
run_name = f"stefano-{today}"
mlflow.set_tracking_uri("http://localhost:5000")

mlflow.pytorch.autolog(log_every_n_epoch=1,
                       log_every_n_step=50,
                       log_models=True)
with mlflow.start_run(experiment_id=experiment_id,
                      run_name=run_name,
                      nested=False,
                      tags=None) as run:
    trainer.fit(mnist_model, train_loader)
