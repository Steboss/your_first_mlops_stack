import mlflow
import mlflow.sklearn
from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_curve, auc, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from sklearn.preprocessing import label_binarize
from mlflow.tracking.client import MlflowClient
from datetime import datetime

iris = datasets.load_iris()
X = iris.data
y = iris.target
class_names = iris.target_names

y_bin = label_binarize(y, classes=[0, 1, 2])
n_classes = y_bin.shape[1]
print(f"Detected {n_classes} classes")

X_train, X_test, y_train, y_test = train_test_split(X,
                                                    y,
                                                    test_size=0.3,
                                                    random_state=42)

rf = RandomForestClassifier(n_estimators=20, max_depth=3, random_state=42)

# Set up MLflow specs
today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
experiment_name = "randomforest-experiments"
client = MlflowClient(tracking_uri="http://localhost:5000")
experiment_exists = client.get_experiment_by_name(experiment_name)
if not experiment_exists:
    experiment_id = client.create_experiment(experiment_name)
else:
    experiment_id = experiment_exists.experiment_id
run_name = f"stefano-{today}"
mlflow.set_tracking_uri("http://localhost:5000")

# Start MLflow run
with mlflow.start_run(experiment_id=experiment_id,
                      run_name=run_name,
                      nested=False,
                      tags=None) as run:
    rf.fit(X_train, y_train)
    y_probs = rf.predict_proba(X_test)

    # Log model and parameters
    mlflow.sklearn.log_model(rf, "random_forest_iris")
    mlflow.log_params({"n_estimators": 100, "max_depth": 3})

    # Compute ROC curve and ROC area for each class
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_test == i, y_probs[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

    # Plot ROC curve
    plt.figure()
    for i, color in zip(range(n_classes), ['blue', 'red', 'green']):
        plt.plot(fpr[i], tpr[i], color=color, label=f'Class {i} (area = {roc_auc[i]:.2f})')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curves for each class')
    plt.legend(loc='lower right')
    plt.savefig('/tmp/roc_curve.png')
    mlflow.log_artifact('/tmp/roc_curve.png')

    # Log accuracy
    accuracy = accuracy_score(y_test, rf.predict(X_test))
    mlflow.log_metric("accuracy", accuracy)

    # Plot and log confusion matrix
    cm = confusion_matrix(y_test, rf.predict(X_test))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot()
    plt.savefig('/tmp/confusion_matrix.png')
    mlflow.log_artifact('/tmp/confusion_matrix.png')

# MLflow UI can be viewed by running `mlflow ui` in the terminal from the directory where this script is run.
