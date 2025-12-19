"""Run all tests and generate reports"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.test_all_usecases import run_tests
from tests.generate_report import generate_coverage_report
from common.database import get_db_path

if __name__ == "__main__":
    print("="*80)
    print("RUNNING COMPLETE TEST SUITE WITH COVERAGE REPORT")
    print("="*80)
    print()
    
    # Run tests
    result = run_tests()
    
    # Generate coverage report
    print("\n" + "="*80)
    print("GENERATING COVERAGE REPORT")
    print("="*80)
    print()
    
    # Try to generate report from main database
    db_path = get_db_path('retail_db.sqlite')
    if not os.path.exists(db_path):
        # Try test database
        db_path = get_db_path('test_retail_db.sqlite')
    
    if os.path.exists(db_path):
        generate_coverage_report(db_path)
    else:
        print("[WARN] No database found for coverage report generation")
    
    # Exit with appropriate code
    if result.wasSuccessful():
        print("\n" + "="*80)
        print("ALL TESTS PASSED")
        print("="*80)
        sys.exit(0)
    else:
        print("\n" + "="*80)
        print("SOME TESTS FAILED")
        print("="*80)
        sys.exit(1)

