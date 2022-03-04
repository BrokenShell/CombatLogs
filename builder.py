from joblib import dump
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier

from model import get_data


features, target = get_data()
X_train, X_test, y_train, y_test = train_test_split(
    features,
    target,
    random_state=25377689,
    test_size=0.15,
    stratify=target,
)

# model = svm.SVC(
#     class_weight="balanced",
#     probability=True,
#     random_state=25377689,
# )
model = HistGradientBoostingClassifier()
model.fit(X_train, y_train)
dump(model, "gbc_model.joblib")

print(f"Training Accuracy: {model.score(X_train, y_train):.3%}")
print(f"Validation Accuracy: {model.score(X_test, y_test):.3%}")
