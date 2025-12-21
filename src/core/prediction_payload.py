import json
import os

def save_prediction_payload(df, ticker, prob):
    payload = {
        "ticker": ticker,
        "date": str(df.index[-1].date()),
        "latest_close": float(df["Close"].iloc[-1].item()),
        "probability_up": round(prob, 4)
    }

    os.makedirs("outputs", exist_ok=True)
    with open(f"outputs/{ticker}.json", "w") as f:
        json.dump(payload, f, indent=4)
