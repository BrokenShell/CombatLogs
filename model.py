from functools import reduce
from operator import mul

import joblib
import pandas
from pandas import DataFrame
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV


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
    return model.best_estimator_


def make_model():
    features, target = get_data()
    model = RandomForestClassifier(
        criterion='entropy',
        max_depth=10,
        n_jobs=-1,
        random_state=25377689,
        n_estimators=299,
    )
    model.fit(features, target)
    joblib.dump(model, "model.joblib")


def prediction(attacker, attacker_level, defender, defender_level):
    model = joblib.load("model.joblib")
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


if __name__ == '__main__':
    # make_model()
    model = joblib.load("model.joblib")
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
    for opponent in lookup.keys():
        print(f"Barbarian vs {opponent:<11}", end=" => ")
        print(prediction_str("Barbarian", 20, opponent, 20))
