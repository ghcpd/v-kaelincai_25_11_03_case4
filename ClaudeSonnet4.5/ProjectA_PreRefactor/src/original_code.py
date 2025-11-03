"""
Original Implementation - Pre-Refactor
This code contains multiple code smells and anti-patterns:
- Code duplication
- Long methods
- Magic numbers
- Poor naming conventions
- Deeply nested conditionals
- Mixed concerns
- No separation of logic
"""

import json
import time
from datetime import datetime


class DataProcessor:
    """Original data processor with multiple code smells"""
    
    def __init__(self):
        self.data = []
        self.results = []
        
    def process_user_data(self, user_data):
        """
        Process user data with duplicated logic and poor structure
        """
        # Duplicated validation logic
        if user_data is None:
            return {"status": "error", "message": "User data is None"}
        if not isinstance(user_data, dict):
            return {"status": "error", "message": "User data is not a dict"}
        if "name" not in user_data:
            return {"status": "error", "message": "Name is missing"}
        if "email" not in user_data:
            return {"status": "error", "message": "Email is missing"}
        if "age" not in user_data:
            return {"status": "error", "message": "Age is missing"}
            
        # Magic numbers and duplicated calculation logic
        if user_data["age"] < 0:
            return {"status": "error", "message": "Invalid age"}
        if user_data["age"] > 150:
            return {"status": "error", "message": "Invalid age"}
            
        # Duplicated email validation
        email = user_data["email"]
        if "@" not in email:
            return {"status": "error", "message": "Invalid email"}
        if "." not in email:
            return {"status": "error", "message": "Invalid email"}
        if email.count("@") != 1:
            return {"status": "error", "message": "Invalid email"}
            
        # Process data with nested conditionals
        result = {}
        result["name"] = user_data["name"].strip().title()
        result["email"] = user_data["email"].lower().strip()
        result["age"] = user_data["age"]
        
        # Duplicated age categorization logic
        if user_data["age"] >= 0 and user_data["age"] < 18:
            result["category"] = "minor"
        elif user_data["age"] >= 18 and user_data["age"] < 65:
            result["category"] = "adult"
        else:
            result["category"] = "senior"
            
        result["status"] = "success"
        result["processed_at"] = str(datetime.now())
        
        return result
        
    def process_product_data(self, product_data):
        """
        Process product data - notice the duplicated validation pattern
        """
        # Duplicated validation logic (same pattern as user data)
        if product_data is None:
            return {"status": "error", "message": "Product data is None"}
        if not isinstance(product_data, dict):
            return {"status": "error", "message": "Product data is not a dict"}
        if "name" not in product_data:
            return {"status": "error", "message": "Name is missing"}
        if "price" not in product_data:
            return {"status": "error", "message": "Price is missing"}
        if "quantity" not in product_data:
            return {"status": "error", "message": "Quantity is missing"}
            
        # Magic numbers and duplicated validation
        if product_data["price"] < 0:
            return {"status": "error", "message": "Invalid price"}
        if product_data["price"] > 1000000:
            return {"status": "error", "message": "Invalid price"}
        if product_data["quantity"] < 0:
            return {"status": "error", "message": "Invalid quantity"}
        if product_data["quantity"] > 10000:
            return {"status": "error", "message": "Invalid quantity"}
            
        # Process data with nested conditionals
        result = {}
        result["name"] = product_data["name"].strip().title()
        result["price"] = round(product_data["price"], 2)
        result["quantity"] = product_data["quantity"]
        
        # Duplicated price categorization logic
        if product_data["price"] >= 0 and product_data["price"] < 10:
            result["price_category"] = "budget"
        elif product_data["price"] >= 10 and product_data["price"] < 100:
            result["price_category"] = "standard"
        elif product_data["price"] >= 100 and product_data["price"] < 1000:
            result["price_category"] = "premium"
        else:
            result["price_category"] = "luxury"
            
        # Duplicated stock categorization logic
        if product_data["quantity"] >= 0 and product_data["quantity"] < 10:
            result["stock_status"] = "low"
        elif product_data["quantity"] >= 10 and product_data["quantity"] < 100:
            result["stock_status"] = "medium"
        else:
            result["stock_status"] = "high"
            
        result["status"] = "success"
        result["processed_at"] = str(datetime.now())
        
        return result
        
    def calculate_discount(self, price, customer_type, quantity):
        """
        Calculate discount with duplicated logic and magic numbers
        """
        # Long method with many nested conditionals
        if price is None or customer_type is None or quantity is None:
            return 0
            
        if not isinstance(price, (int, float)):
            return 0
        if not isinstance(quantity, int):
            return 0
        if price < 0 or quantity < 0:
            return 0
            
        discount = 0
        
        # Magic numbers everywhere
        if customer_type == "regular":
            if quantity >= 1 and quantity < 5:
                discount = 0.05
            elif quantity >= 5 and quantity < 10:
                discount = 0.10
            elif quantity >= 10 and quantity < 20:
                discount = 0.15
            else:
                discount = 0.20
        elif customer_type == "premium":
            if quantity >= 1 and quantity < 5:
                discount = 0.10
            elif quantity >= 5 and quantity < 10:
                discount = 0.15
            elif quantity >= 10 and quantity < 20:
                discount = 0.20
            else:
                discount = 0.25
        elif customer_type == "vip":
            if quantity >= 1 and quantity < 5:
                discount = 0.15
            elif quantity >= 5 and quantity < 10:
                discount = 0.20
            elif quantity >= 10 and quantity < 20:
                discount = 0.25
            else:
                discount = 0.30
        else:
            discount = 0
            
        # Additional discount for high-value purchases (duplicated logic)
        if price > 100:
            discount = discount + 0.05
        if price > 500:
            discount = discount + 0.05
        if price > 1000:
            discount = discount + 0.05
            
        # Cap discount at 50%
        if discount > 0.50:
            discount = 0.50
            
        return discount
        
    def batch_process(self, items, item_type):
        """
        Batch process items with poor error handling
        """
        if not items:
            return []
            
        results = []
        
        # No proper error handling, processes all or nothing
        for item in items:
            if item_type == "user":
                r = self.process_user_data(item)
                results.append(r)
            elif item_type == "product":
                r = self.process_product_data(item)
                results.append(r)
            else:
                results.append({"status": "error", "message": "Unknown type"})
                
        return results
        
    def generate_report(self, results):
        """
        Generate report with duplicated formatting logic
        """
        if not results:
            return "No results to report"
            
        report = ""
        report = report + "=" * 50 + "\n"
        report = report + "Processing Report\n"
        report = report + "=" * 50 + "\n"
        report = report + f"Generated at: {datetime.now()}\n"
        report = report + "-" * 50 + "\n"
        
        success_count = 0
        error_count = 0
        
        # Duplicated counting logic
        for r in results:
            if r.get("status") == "success":
                success_count = success_count + 1
            else:
                error_count = error_count + 1
                
        report = report + f"Total Records: {len(results)}\n"
        report = report + f"Successful: {success_count}\n"
        report = report + f"Failed: {error_count}\n"
        report = report + "-" * 50 + "\n"
        
        # Duplicated percentage calculation
        if len(results) > 0:
            success_rate = (success_count / len(results)) * 100
            error_rate = (error_count / len(results)) * 100
        else:
            success_rate = 0
            error_rate = 0
            
        report = report + f"Success Rate: {success_rate:.2f}%\n"
        report = report + f"Error Rate: {error_rate:.2f}%\n"
        report = report + "=" * 50 + "\n"
        
        return report


def main():
    """Main function with inline logic"""
    processor = DataProcessor()
    
    # Sample data
    user = {"name": "  john doe  ", "email": "JOHN@EXAMPLE.COM", "age": 25}
    product = {"name": "  laptop  ", "price": 999.99, "quantity": 5}
    
    print("Processing user data...")
    user_result = processor.process_user_data(user)
    print(json.dumps(user_result, indent=2))
    
    print("\nProcessing product data...")
    product_result = processor.process_product_data(product)
    print(json.dumps(product_result, indent=2))
    
    print("\nCalculating discount...")
    discount = processor.calculate_discount(999.99, "premium", 5)
    print(f"Discount: {discount * 100}%")
    
    print("\nGenerating report...")
    report = processor.generate_report([user_result, product_result])
    print(report)


if __name__ == "__main__":
    main()
