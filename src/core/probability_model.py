import pickle
import os
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from src.config.features import FEATURE_COLUMNS

def train_probability_model(df, ticker):
    X = df[FEATURE_COLUMNS]
    y = df["Target"]

    pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000)),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    pipeline.fit(X_train, y_train)

    os.makedirs("models", exist_ok=True)
    pickle.dump(pipeline, open(f"models/{ticker}_model.pkl", "wb"))

    auc = roc_auc_score(
        y_test, pipeline.predict_proba(X_test)[:, 1]
    )
    return auc

def predict_probability(df, ticker):
    pipeline = pickle.load(open(f"models/{ticker}_model.pkl", "rb"))
    X = df[FEATURE_COLUMNS]
    return pipeline.predict_proba(X)[-1][1]

def train_model_in_memory(df):
    X = df[FEATURE_COLUMNS]
    y = df["Target"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_scaled, y)

    return model, scaler

def predict_with_model(df, model, scaler):
    X = df[FEATURE_COLUMNS]
    X_scaled = scaler.transform(X)
    return model.predict_proba(X_scaled)[-1][1]
