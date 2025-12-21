import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import pickle
import os

def train_probability_model(df, ticker):
    feature_cols = [col for col in df.columns if col not in ["Target"]]

    X = df[feature_cols]
    y = df["Target"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, shuffle=False
    )

    model = LogisticRegression()
    model.fit(X_train, y_train)

    os.makedirs("models", exist_ok=True)
    pickle.dump(model, open(f"models/{ticker}_model.pkl", "wb"))
    pickle.dump(scaler, open("models/scaler.pkl", "wb"))

    score = model.score(X_test, y_test)
    return score


def predict_probability(df, ticker):
    feature_cols = [col for col in df.columns if col != "Target"]

    model = pickle.load(open(f"models/{ticker}_model.pkl", "rb"))
    scaler = pickle.load(open("models/scaler.pkl", "rb"))

    X = df[feature_cols]
    X_scaled = scaler.transform(X)

    prob = model.predict_proba(X_scaled)[-1][1]

    return prob
