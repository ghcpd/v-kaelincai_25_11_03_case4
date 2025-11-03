"""
Test suite for refactored implementation (Post-Refactor)
"""

import sys
import json
import time
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from refactored_code import DataProcessor


class TestRunner:
    def __init__(self):
        self.processor = DataProcessor()
        self.test_results = []
        self.start_time = None
        self.end_time = None
        
    def load_test_data(self):
        """Load test data from JSON file"""
        data_path = Path(__file__).parent.parent / "data" / "test_data.json"
        with open(data_path, 'r') as f:
            return json.load(f)
            
    def run_test(self, test_case):
        """Run a single test case"""
        test_name = test_case["name"]
        test_type = test_case["type"]
        input_data = test_case["input"]
        expected = test_case["expected"]
        
        start = time.time()
        
        try:
            if test_type == "user":
                actual = self.processor.process_user_data(input_data)
            elif test_type == "product":
                actual = self.processor.process_product_data(input_data)
            elif test_type == "discount":
                actual = self.processor.calculate_discount(
                    input_data["price"],
                    input_data["customer_type"],
                    input_data["quantity"]
                )
            elif test_type == "batch":
                actual = self.processor.batch_process(
                    input_data["items"],
                    input_data["item_type"]
                )
            else:
                actual = {"status": "error", "message": "Unknown test type"}
                
            end = time.time()
            execution_time = end - start
            
            # Compare results
            if test_type == "discount":
                # For discount, compare float values with tolerance
                passed = abs(actual - expected) < 0.001
            else:
                # For other types, check status and key fields
                if isinstance(expected, dict) and isinstance(actual, dict):
                    passed = expected.get("status") == actual.get("status")
                elif isinstance(expected, list) and isinstance(actual, list):
                    passed = len(expected) == len(actual)
                    if passed:
                        for e, a in zip(expected, actual):
                            if e.get("status") != a.get("status"):
                                passed = False
                                break
                else:
                    passed = expected == actual
                    
            result = {
                "test_name": test_name,
                "test_type": test_type,
                "passed": passed,
                "execution_time": execution_time,
                "expected": expected,
                "actual": actual
            }
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            end = time.time()
            execution_time = end - start
            
            result = {
                "test_name": test_name,
                "test_type": test_type,
                "passed": False,
                "execution_time": execution_time,
                "expected": expected,
                "actual": {"error": str(e)}
            }
            
            self.test_results.append(result)
            return result
            
    def run_all_tests(self):
        """Run all test cases"""
        print("=" * 70)
        print("Running Tests for Refactored Implementation (Post-Refactor)")
        print("=" * 70)
        
        self.start_time = time.time()
        
        test_data = self.load_test_data()
        
        for i, test_case in enumerate(test_data["test_cases"], 1):
            print(f"\n[Test {i}/{len(test_data['test_cases'])}] {test_case['name']}")
            result = self.run_test(test_case)
            
            status = "PASSED" if result["passed"] else "FAILED"
            print(f"  Status: {status}")
            print(f"  Execution Time: {result['execution_time']:.4f}s")
            
            if not result["passed"]:
                print(f"  Expected: {result['expected']}")
                print(f"  Actual: {result['actual']}")
                
        self.end_time = time.time()
        
    def generate_report(self):
        """Generate test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["passed"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        total_time = self.end_time - self.start_time
        avg_time = total_time / total_tests if total_tests > 0 else 0
        
        report = "\n" + "=" * 70 + "\n"
        report += "Test Summary (Refactored Implementation)\n"
        report += "=" * 70 + "\n"
        report += f"Total Tests: {total_tests}\n"
        report += f"Passed: {passed_tests}\n"
        report += f"Failed: {failed_tests}\n"
        report += f"Success Rate: {success_rate:.2f}%\n"
        report += f"Total Execution Time: {total_time:.4f}s\n"
        report += f"Average Test Time: {avg_time:.4f}s\n"
        report += "=" * 70 + "\n"
        
        print(report)
        
        # Save report
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        with open(log_dir / "test_log_refactored.txt", 'w') as f:
            f.write(report)
            f.write("\n\nDetailed Results:\n")
            f.write("-" * 70 + "\n")
            for result in self.test_results:
                f.write(f"\nTest: {result['test_name']}\n")
                f.write(f"Status: {'PASSED' if result['passed'] else 'FAILED'}\n")
                f.write(f"Time: {result['execution_time']:.4f}s\n")
                if not result['passed']:
                    f.write(f"Expected: {result['expected']}\n")
                    f.write(f"Actual: {result['actual']}\n")
                f.write("-" * 70 + "\n")
                
        # Save performance metrics
        perf_dir = Path(__file__).parent.parent / "performance"
        perf_dir.mkdir(exist_ok=True)
        
        metrics = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": success_rate,
            "total_time": total_time,
            "average_time": avg_time,
            "test_times": [r["execution_time"] for r in self.test_results]
        }
        
        with open(perf_dir / "metrics_refactored.json", 'w') as f:
            json.dump(metrics, f, indent=2)
            
        return metrics


def main():
    runner = TestRunner()
    runner.run_all_tests()
    metrics = runner.generate_report()
    
    # Exit with error code if tests failed
    if metrics["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
