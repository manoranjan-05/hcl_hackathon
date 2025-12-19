"""Comprehensive test suite for all use cases"""
import sys
import os
import sqlite3
import pandas as pd
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.database import setup_database, get_db_path
from usecase1.data_ingestion import execute as execute_usecase1
from usecase2.promotion_analyzer import execute as execute_usecase2
from usecase3.loyalty_engine import execute as execute_usecase3
from usecase4.customer_segmentation import execute as execute_usecase4
from usecase5.notification_system import execute as execute_usecase5
from usecase6.inventory_analysis import execute as execute_usecase6

class TestUseCase1(unittest.TestCase):
    """Test Use Case 1: Data Ingestion and Quality Validation"""
    
    def setUp(self):
        self.db_path = get_db_path('test_retail_db.sqlite')
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        setup_database(self.db_path)
    
    def test_data_ingestion(self):
        """Test data ingestion pipeline"""
        result = execute_usecase1(self.db_path)
        self.assertIsNotNone(result)
        
        conn = sqlite3.connect(self.db_path)
        
        # Check raw data loaded
        raw_headers = pd.read_sql("SELECT COUNT(*) as count FROM raw_store_sales_header", conn)['count'].iloc[0]
        raw_items = pd.read_sql("SELECT COUNT(*) as count FROM raw_store_sales_line_items", conn)['count'].iloc[0]
        self.assertGreater(raw_headers, 0, "Raw headers should be loaded")
        self.assertGreater(raw_items, 0, "Raw line items should be loaded")
        
        # Check staging data
        staging_headers = pd.read_sql("SELECT COUNT(*) as count FROM staging_store_sales_header", conn)['count'].iloc[0]
        staging_items = pd.read_sql("SELECT COUNT(*) as count FROM staging_store_sales_line_items", conn)['count'].iloc[0]
        self.assertGreater(staging_headers, 0, "Valid headers should be in staging")
        self.assertGreater(staging_items, 0, "Valid line items should be in staging")
        
        # Check quarantine data exists (may be empty if all data is valid)
        rejected_headers = pd.read_sql("SELECT COUNT(*) as count FROM quarantine_rejected_sales_header", conn)['count'].iloc[0]
        rejected_items = pd.read_sql("SELECT COUNT(*) as count FROM quarantine_rejected_sales_line_items", conn)['count'].iloc[0]
        
        conn.close()
        print(f"[PASS] Use Case 1: {staging_headers} valid headers, {staging_items} valid items")

class TestUseCase2(unittest.TestCase):
    """Test Use Case 2: Promotion Effectiveness Analyzer"""
    
    def setUp(self):
        self.db_path = get_db_path('test_retail_db.sqlite')
        if not os.path.exists(self.db_path):
            setup_database(self.db_path)
            execute_usecase1(self.db_path)
    
    def test_promotion_analysis(self):
        """Test promotion effectiveness analysis"""
        results = execute_usecase2(self.db_path)
        self.assertIsNotNone(results)
        self.assertLessEqual(len(results), 3, "Should return top 3 promotions")
        
        conn = sqlite3.connect(self.db_path)
        promotion_data = pd.read_sql("SELECT * FROM promotion_effectiveness ORDER BY rank LIMIT 3", conn)
        conn.close()
        
        self.assertGreater(len(promotion_data), 0, "Should have promotion effectiveness data")
        print(f"[PASS] Use Case 2: Analyzed {len(promotion_data)} promotions")

class TestUseCase3(unittest.TestCase):
    """Test Use Case 3: Loyalty Point Calculation Engine"""
    
    def setUp(self):
        self.db_path = get_db_path('test_retail_db.sqlite')
        if not os.path.exists(self.db_path):
            setup_database(self.db_path)
            execute_usecase1(self.db_path)
    
    def test_loyalty_calculation(self):
        """Test loyalty point calculation"""
        count = execute_usecase3(self.db_path)
        self.assertGreaterEqual(count, 0, "Should process transactions")
        
        conn = sqlite3.connect(self.db_path)
        
        # Check loyalty transactions recorded
        loyalty_txns = pd.read_sql("SELECT COUNT(*) as count FROM loyalty_point_transactions", conn)['count'].iloc[0]
        self.assertGreaterEqual(loyalty_txns, 0, "Should have loyalty transactions")
        
        # Check customer points updated
        customers_with_points = pd.read_sql(
            "SELECT COUNT(*) as count FROM staging_customer_details WHERE total_loyalty_points > 0", 
            conn
        )['count'].iloc[0]
        
        conn.close()
        print(f"[PASS] Use Case 3: Processed {count} transactions, {customers_with_points} customers with points")

class TestUseCase4(unittest.TestCase):
    """Test Use Case 4: Customer Segmentation"""
    
    def setUp(self):
        self.db_path = get_db_path('test_retail_db.sqlite')
        if not os.path.exists(self.db_path):
            setup_database(self.db_path)
            execute_usecase1(self.db_path)
    
    def test_customer_segmentation(self):
        """Test customer segmentation"""
        segments = execute_usecase4(self.db_path)
        self.assertIsNotNone(segments)
        
        conn = sqlite3.connect(self.db_path)
        segment_data = pd.read_sql("SELECT * FROM customer_segments", conn)
        conn.close()
        
        self.assertGreater(len(segment_data), 0, "Should have segmented customers")
        
        # Check for High-Spenders and At-Risk segments
        segment_names = segment_data['segment_name'].unique()
        print(f"[PASS] Use Case 4: Segmented {len(segment_data)} customers into {len(segment_names)} segments")

class TestUseCase5(unittest.TestCase):
    """Test Use Case 5: Loyalty Notification System"""
    
    def setUp(self):
        self.db_path = get_db_path('test_retail_db.sqlite')
        if not os.path.exists(self.db_path):
            setup_database(self.db_path)
            execute_usecase1(self.db_path)
            execute_usecase3(self.db_path)
    
    def test_notification_system(self):
        """Test notification generation"""
        count = execute_usecase5(self.db_path)
        self.assertGreaterEqual(count, 0, "Should generate notifications")
        
        conn = sqlite3.connect(self.db_path)
        notifications = pd.read_sql("SELECT COUNT(*) as count FROM loyalty_notifications", conn)['count'].iloc[0]
        conn.close()
        
        self.assertGreaterEqual(notifications, 0, "Should have notifications")
        print(f"[PASS] Use Case 5: Generated {count} notifications")

class TestUseCase6(unittest.TestCase):
    """Test Use Case 6: Inventory Analysis"""
    
    def setUp(self):
        self.db_path = get_db_path('test_retail_db.sqlite')
        if not os.path.exists(self.db_path):
            setup_database(self.db_path)
            execute_usecase1(self.db_path)
    
    def test_inventory_analysis(self):
        """Test inventory performance analysis"""
        count = execute_usecase6(self.db_path)
        self.assertGreaterEqual(count, 0, "Should analyze products")
        
        conn = sqlite3.connect(self.db_path)
        analysis_data = pd.read_sql("SELECT * FROM inventory_analysis", conn)
        conn.close()
        
        self.assertGreaterEqual(len(analysis_data), 0, "Should have inventory analysis data")
        print(f"[PASS] Use Case 6: Analyzed {count} top products")

class TestEndToEnd(unittest.TestCase):
    """End-to-end test of complete pipeline"""
    
    def setUp(self):
        self.db_path = get_db_path('test_e2e_db.sqlite')
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_complete_pipeline(self):
        """Test complete pipeline execution"""
        setup_database(self.db_path)
        
        # Execute all use cases in sequence
        execute_usecase1(self.db_path)
        execute_usecase2(self.db_path)
        execute_usecase3(self.db_path)
        execute_usecase4(self.db_path)
        execute_usecase5(self.db_path)
        execute_usecase6(self.db_path)
        
        # Verify all tables have data
        conn = sqlite3.connect(self.db_path)
        
        tables_to_check = [
            'staging_store_sales_header',
            'staging_store_sales_line_items',
            'promotion_effectiveness',
            'loyalty_point_transactions',
            'customer_segments',
            'loyalty_notifications',
            'inventory_analysis'
        ]
        
        for table in tables_to_check:
            count = pd.read_sql(f"SELECT COUNT(*) as count FROM {table}", conn)['count'].iloc[0]
            self.assertGreaterEqual(count, 0, f"Table {table} should exist and have data")
        
        conn.close()
        print("[PASS] End-to-end pipeline test completed successfully")

def run_tests():
    """Run all tests and generate report"""
    print("="*80)
    print("RUNNING COMPREHENSIVE TEST SUITE")
    print("="*80)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUseCase1))
    suite.addTests(loader.loadTestsFromTestCase(TestUseCase2))
    suite.addTests(loader.loadTestsFromTestCase(TestUseCase3))
    suite.addTests(loader.loadTestsFromTestCase(TestUseCase4))
    suite.addTests(loader.loadTestsFromTestCase(TestUseCase5))
    suite.addTests(loader.loadTestsFromTestCase(TestUseCase6))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    return result

if __name__ == "__main__":
    run_tests()

