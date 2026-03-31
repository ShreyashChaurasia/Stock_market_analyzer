from src.verification.service import verification_service


def run_backtest_pipeline(
    ticker: str,
    start: str | None = None,
    end: str | None = None,
    model_type: str = "logistic",
):
    print(f"[INFO] Running backtest pipeline for {ticker}")

    report = verification_service.get_backtest_report(
        ticker=ticker,
        model_type=model_type,
        start_date=start,
        end_date=end,
        refresh=True,
    )
    metrics = report["metrics"]

    print("[BACKTEST RESULTS]")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    print("[SUCCESS] Backtest completed")
    return report
