"""
Combined Critical Categories Test
================================

This script runs tests for all five critical FMP data categories:
1. Financial Statements (Category B)
2. Enterprise Values (Category E)
3. DCF Valuations (Category C)
4. Owner Earnings (Category F)

Tests are executed in dependency order, all using the same set of test symbols.
"""

import sys
import subprocess

# Define the tests to run - in appropriate order
TESTS = [
    # First, make sure stock profiles exist (Category A)
    ["py", "comprehensive_test_framework.py", "--category", "A"],
    
    # Financial Statements (Category B)
    ["py", "comprehensive_test_framework.py", "--tests", "financial_statements"],
    
    # Enterprise Values (Category E)
    ["py", "comprehensive_test_framework.py", "--category", "E"],
    
    # DCF Valuations (Category C)
    ["py", "comprehensive_test_framework.py", "--category", "C"],
    
    # Owner Earnings (Category F)
    ["py", "comprehensive_test_framework.py", "--category", "F"]
]

def run_tests():
    """Run all critical tests in sequence"""
    
    print("==========================================================")
    print("🚀 STARTING COMPREHENSIVE TEST FOR ALL CRITICAL CATEGORIES")
    print("==========================================================")
    
    results = []
    
    # Run each test
    for test_cmd in TESTS:
        test_name = test_cmd[-1] if len(test_cmd) > 3 else test_cmd[-2]
        print(f"\n[RUNNING TEST: {test_name}]")
        print(f"Command: {' '.join(test_cmd)}")
        
        try:
            result = subprocess.run(test_cmd, check=False)
            success = result.returncode == 0
            results.append((test_name, success))
            
            if success:
                print(f"✅ Test '{test_name}' PASSED")
            else:
                print(f"❌ Test '{test_name}' FAILED (return code: {result.returncode})")
                
        except Exception as e:
            print(f"❌ Error running test '{test_name}': {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n==========================================================")
    print("📊 TEST SUMMARY")
    print("==========================================================")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"TOTAL: {passed}/{total} tests passed")
    
    for name, success in results:
        print(f"{'✅' if success else '❌'} {name}")
    
    # Return success only if all tests passed
    return all(success for _, success in results)

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
