import sys
import os
from datetime import datetime

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def test_imports():
    """Test if all imports work"""
    print_section("TEST 1: Checking Imports")
    
    try:
        print("Testing FastAPI import...")
        import fastapi
        print("FastAPI imported successfully")
        
        print("Testing pandas import...")
        import pandas
        print("Pandas imported successfully")
        
        print("Testing scikit-learn import...")
        import sklearn
        print("Scikit-learn imported successfully")
        
        print("Testing yfinance import...")
        import yfinance
        print("YFinance imported successfully")
        
        print("Testing project imports...")
        from src.core.data_fetcher import fetch_stock_data
        from src.pipelines.inference_pipeline import run_inference_pipeline
        print("Project modules imported successfully")
        
        return True
        
    except Exception as e:
        print(f"Import failed: {str(e)}")
        return False


def test_data_fetcher():
    """Test the data fetcher"""
    print_section("TEST 2: Testing Data Fetcher")
    
    try:
        from src.core.data_fetcher import fetch_stock_data
        
        print("Fetching test data for AAPL (last 90 days)...")
        df = fetch_stock_data('AAPL', period='3mo')
        
        print(f"Data fetched successfully!")
        print(f"   → Rows: {len(df)}")
        print(f"   → Columns: {list(df.columns)}")
        print(f"   → Date range: {df.index[0].date()} to {df.index[-1].date()}")
        
        return True
        
    except Exception as e:
        print(f"Data fetcher test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_inference_pipeline():
    """Test the inference pipeline"""
    print_section("TEST 3: Testing Inference Pipeline")
    
    try:
        from src.pipelines.inference_pipeline import run_inference_pipeline
        
        print("Running inference for MSFT...")
        result = run_inference_pipeline('MSFT')
        
        print(f"\nInference pipeline completed!")
        print(f"   → Ticker: {result['ticker']}")
        print(f"   → Prediction: {result['prediction']}")
        print(f"   → Probability UP: {result['probability_up']}")
        print(f"   → Confidence: {result['confidence_percent']}")
        print(f"   → Model AUC: {result['model_auc']}")
        
        return True
        
    except Exception as e:
        print(f"Inference pipeline test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_file_structure():
    """Test if required files and directories exist"""
    print_section("TEST 4: Checking File Structure")
    
    required_dirs = ['data', 'models', 'outputs', 'src']
    required_files = ['app.py', 'requirements.txt']
    
    all_good = True
    
    print("Checking directories:")
    for dir_name in required_dirs:
        exists = os.path.exists(dir_name)
        status = "yes" if exists else "no"
        print(f"   {status} {dir_name}/")
        if not exists:
            all_good = False
    
    print("\nChecking files:")
    for file_name in required_files:
        exists = os.path.exists(file_name)
        status = "yes" if exists else "no"
        print(f"   {status} {file_name}")
        if not exists:
            all_good = False
    
    return all_good


def test_api_app():
    """Test if FastAPI app can be imported"""
    print_section("TEST 5: Testing FastAPI App")
    
    try:
        print("Importing FastAPI app...")
        from app import app
        
        print("FastAPI app imported successfully!")
        print(f"   → App title: {app.title}")
        print(f"   → App version: {app.version}")
        
        # Count routes
        routes = [route.path for route in app.routes]
        print(f"   → Total routes: {len(routes)}")
        print(f"   → Routes: {routes[:5]}...")  # Show first 5
        
        return True
        
    except Exception as e:
        print(f"FastAPI app test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print("  STOCK MARKET ANALYZER - SETUP TEST SUITE")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)
    
    results = {
        "Imports": test_imports(),
        "File Structure": test_file_structure(),
        "Data Fetcher": test_data_fetcher(),
        "Inference Pipeline": test_inference_pipeline(),
        "FastAPI App": test_api_app()
    }
    
    # Summary
    print_section("TEST SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print("Results:")
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"   {status}  {test_name}")
    
    print(f"\n{'='*70}")
    print(f"  Total: {total} | Passed: {passed} | Failed: {failed}")
    
    if failed == 0:
        print(f"  ALL TESTS PASSED! Your setup is ready!")
    else:
        print(f"   {failed} test(s) failed. Please review the errors above.")
    
    print(f"{'='*70}\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)