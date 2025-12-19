"""Main pipeline orchestrator for all use cases"""
import sys
import os
from common.database import setup_database, get_db_path
from usecase1.data_ingestion import execute as execute_usecase1
from usecase2.promotion_analyzer import execute as execute_usecase2
from usecase3.loyalty_engine import execute as execute_usecase3
from usecase4.customer_segmentation import execute as execute_usecase4
from usecase5.notification_system import execute as execute_usecase5
from usecase6.inventory_analysis import execute as execute_usecase6

def run_all_usecases():
    """Run all use cases in sequence"""
    print("="*80)
    print("RETAIL DATA PROCESSING PIPELINE - ALL USE CASES")
    print("="*80)
    
    # Setup database
    db_path = setup_database()
    print(f"\n[OK] Database initialized: {db_path}")
    
    # Execute all use cases
    results = {}
    
    try:
        results['usecase1'] = execute_usecase1(db_path)
        results['usecase2'] = execute_usecase2(db_path)
        results['usecase3'] = execute_usecase3(db_path)
        results['usecase4'] = execute_usecase4(db_path)
        results['usecase5'] = execute_usecase5(db_path)
        results['usecase6'] = execute_usecase6(db_path)
        
        print("\n" + "="*80)
        print("ALL USE CASES COMPLETED SUCCESSFULLY")
        print("="*80)
        
        return results
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    run_all_usecases()

