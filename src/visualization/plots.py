import matplotlib.pyplot as plt


def plot_price_with_predictions(price_df, results_df, ticker):
    """
    Price chart with UP/DOWN predictions overlaid.
    """

    fig, ax = plt.subplots(figsize=(14, 6))

    # Price
    ax.plot(price_df.index, price_df["Close"], label="Close Price", color="black")

    # Align results with price index
    preds = results_df.set_index("date")

    # UP predictions
    up = preds[preds["prediction"] == 1]
    ax.scatter(
        up.index,
        price_df.loc[up.index, "Close"],
        color="green",
        label="Predicted UP",
        marker="^",
        alpha=0.7,
    )

    # DOWN predictions
    down = preds[preds["prediction"] == 0]
    ax.scatter(
        down.index,
        price_df.loc[down.index, "Close"],
        color="red",
        label="Predicted DOWN",
        marker="v",
        alpha=0.7,
    )

    ax.set_title(f"{ticker} — Price with Model Predictions")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()

    plt.tight_layout()
    plt.show()

def plot_probability_over_time(results_df, ticker):
    fig, ax = plt.subplots(figsize=(14, 4))

    ax.plot(
        results_df["date"],
        results_df["probability_up"],
        label="P(UP)",
        color="blue",
    )

    ax.axhline(0.5, linestyle="--", color="gray", alpha=0.5)

    ax.set_title(f"{ticker} — Predicted Probability of UP")
    ax.set_ylabel("Probability")
    ax.set_xlabel("Date")
    ax.legend()

    plt.tight_layout()
    plt.show()
