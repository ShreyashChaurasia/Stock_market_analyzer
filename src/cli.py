import argparse

from src.pipelines.inference_pipeline import run_inference_pipeline
from src.pipelines.backtest_pipeline import run_backtest_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Stock Market Analyzer CLI"
    )

    parser.add_argument(
        "--ticker",
        type=str,
        required=True,
        help="Stock ticker symbol (e.g. AAPL, TSLA)"
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["inference", "backtest"],
        default="inference",
        help="Run mode: inference or backtest"
    )

    parser.add_argument(
        "--start",
        type=str,
        default=None,
        help="Start date (YYYY-MM-DD)"
    )

    parser.add_argument(
        "--end",
        type=str,
        default=None,
        help="End date (YYYY-MM-DD)"
    )

    parser.add_argument(
        "--model-type",
        type=str,
        default="logistic",
        help="Model type for backtesting (logistic, random_forest, xgboost, gradient_boosting)"
    )

    args = parser.parse_args()

    if args.mode == "inference":
        run_inference_pipeline(
            ticker=args.ticker,
            start=args.start,
            end=args.end
        )

    elif args.mode == "backtest":
        run_backtest_pipeline(
            ticker=args.ticker,
            start=args.start,
            end=args.end,
            model_type=args.model_type,
        )


if __name__ == "__main__":
    main()
