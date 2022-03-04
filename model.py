import csv
from functools import reduce
from itertools import combinations_with_replacement, chain
from operator import mul

import joblib
import pandas
from pandas import DataFrame
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV, train_test_split


def encoder(label: str) -> int:
    lookup = {
        "Barbarian": 1,
        "Bard": 2,
        "Rogue": 3,
        "Wizard": 4,
        "Warlock": 5,
        "Necromancer": 6,
        "Archer": 7,
        "Ninja": 8,
        "Paladin": 9,
        "Druid": 10,
        "Monk": 11,
        "Pirate": 12,
    }
    return lookup.get(label, 0)


def get_data():
    combat_logs = pandas.read_csv("combat_log.csv")
    target = combat_logs["Winner"]
    features = combat_logs.drop(columns=["Winner"])
    features["Attacker"] = features["Attacker"].apply(encoder)
    features["Defender"] = features["Defender"].apply(encoder)
    return features, target


def find_best_fit():
    features, target = get_data()
    param_dist = {
        "criterion": ["gini", "entropy"],
        "max_depth": [8, 10, 12, 14],
    }
    model = RandomizedSearchCV(
        RandomForestClassifier(
            n_estimators=299,
            random_state=25377689,
            n_jobs=1,
        ),
        n_jobs=-1,
        cv=5,
        random_state=25377689,
        param_distributions=param_dist,
        n_iter=reduce(mul, map(len, param_dist.values())),
    )
    model.fit(features, target)
    return model.best_score_, model.best_estimator_


def make_model():
    features, target = get_data()
    X_train, X_test, y_train, y_test = train_test_split(
        features,
        target,
        random_state=25377689,
        test_size=0.15,
        stratify=target,
    )
    model = RandomForestClassifier(
        criterion='entropy',
        max_depth=10,
        n_jobs=-1,
        random_state=25377689,
        n_estimators=299,
    )
    model.fit(X_train, y_train)
    joblib.dump(model, "model.joblib")
    print(model.score(X_train, y_train))
    print(model.score(X_test, y_test))
    return model


def prediction(attacker, attacker_level, defender, defender_level):
    model = joblib.load("gbc_model.joblib")
    basis = DataFrame([{
        "Attacker": encoder(attacker),
        "AttackerLevel": attacker_level,
        "Defender": encoder(defender),
        "DefenderLevel": defender_level
    }])
    pred, *_ = model.predict(basis)
    prob, *_ = model.predict_proba(basis)
    return pred, max(prob)


def prediction_str(attacker, attacker_level, defender, defender_level):
    pred, prob = prediction(attacker, attacker_level, defender, defender_level)
    return f"{pred:>11} {prob:.1%}"


def prediction_outputs(group, level):
    with open(f"predictions.csv", "a") as csv_file:
        file = csv.writer(csv_file, delimiter=',')
        file.writerow((
            "Attacker", "AttackerLevel",
            "Defender", "DefenderLevel",
            "Prediction", "Confidence",
        ))
        for player_1, player_2 in combinations_with_replacement(group, 2):
            pred, proba = prediction(
                player_1, level,
                player_2, level,
            )
            file.writerow((
                player_1, level,
                player_2, level,
                pred, round(proba, 2),
            ))


class_list = [
    "Barbarian",
    "Bard",
    "Rogue",
    "Wizard",
    "Warlock",
    "Necromancer",
    "Archer",
    "Ninja",
    "Paladin",
    "Druid",
    "Monk",
    "Pirate",
]


def do_all_predictions():
    for level in range(1, 21):
        prediction_outputs(class_list, level)


if __name__ == '__main__':
    # model = make_model()
    # challenger = "Ninja"
    for challenger in class_list:
        for opponent in class_list:
            print(f"{challenger:>11} vs {opponent:<11}", end=" => ")
            print(prediction_str(challenger, 20, opponent, 20))
    # do_all_predictions()
