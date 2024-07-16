from sklearn.datasets import make_classification
import pandas as pd

# Generating a synthetic dataset
X, y = make_classification(n_samples=10000, n_features=20, n_informative=15, n_redundant=5, random_state=42)

# Creating a DataFrame
data = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(1, 21)])
data['target'] = y  # Adding the target column

# Saving to CSV
data.to_csv('fake_dataset.csv', index=False)

