"""
Refactored Implementation - Post-Refactor
This code demonstrates best practices:
- DRY (Don't Repeat Yourself) principle
- Single Responsibility Principle
- Clear naming conventions
- Configuration constants
- Proper separation of concerns
- Type hints for better code clarity
- Modular design
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum


# Configuration Constants
class ValidationRules:
    """Centralized validation rules to avoid magic numbers"""
    MIN_AGE = 0
    MAX_AGE = 150
    MIN_PRICE = 0
    MAX_PRICE = 1_000_000
    MIN_QUANTITY = 0
    MAX_QUANTITY = 10_000
    MAX_DISCOUNT = 0.50


class AgeCategory(Enum):
    """Age categories with clear boundaries"""
    MINOR = (0, 18)
    ADULT = (18, 65)
    SENIOR = (65, 151)
    
    @classmethod
    def get_category(cls, age: int) -> str:
        """Get age category for given age"""
        for category in cls:
            min_age, max_age = category.value
            if min_age <= age < max_age:
                return category.name.lower()
        return "unknown"


class PriceCategory(Enum):
    """Price categories with clear boundaries"""
    BUDGET = (0, 10)
    STANDARD = (10, 100)
    PREMIUM = (100, 1000)
    LUXURY = (1000, float('inf'))
    
    @classmethod
    def get_category(cls, price: float) -> str:
        """Get price category for given price"""
        for category in cls:
            min_price, max_price = category.value
            if min_price <= price < max_price:
                return category.name.lower()
        return "unknown"


class StockStatus(Enum):
    """Stock status categories"""
    LOW = (0, 10)
    MEDIUM = (10, 100)
    HIGH = (100, float('inf'))
    
    @classmethod
    def get_status(cls, quantity: int) -> str:
        """Get stock status for given quantity"""
        for status in cls:
            min_qty, max_qty = status.value
            if min_qty <= quantity < max_qty:
                return status.name.lower()
        return "unknown"


@dataclass
class DiscountTier:
    """Discount tier configuration"""
    min_quantity: int
    discount_rate: float


class DiscountCalculator:
    """Separate class for discount calculation logic"""
    
    # Discount tiers by customer type
    DISCOUNT_TIERS = {
        "regular": [
            DiscountTier(1, 0.05),
            DiscountTier(5, 0.10),
            DiscountTier(10, 0.15),
            DiscountTier(20, 0.20),
        ],
        "premium": [
            DiscountTier(1, 0.10),
            DiscountTier(5, 0.15),
            DiscountTier(10, 0.20),
            DiscountTier(20, 0.25),
        ],
        "vip": [
            DiscountTier(1, 0.15),
            DiscountTier(5, 0.20),
            DiscountTier(10, 0.25),
            DiscountTier(20, 0.30),
        ],
    }
    
    # High-value purchase thresholds
    HIGH_VALUE_THRESHOLDS = [
        (100, 0.05),
        (500, 0.05),
        (1000, 0.05),
    ]
    
    @classmethod
    def calculate(cls, price: float, customer_type: str, quantity: int) -> float:
        """
        Calculate discount based on customer type, quantity, and price
        
        Args:
            price: Item price
            customer_type: Type of customer (regular, premium, vip)
            quantity: Number of items
            
        Returns:
            Discount rate (0.0 to 0.5)
        """
        if not cls._validate_inputs(price, quantity):
            return 0.0
            
        # Get base discount from customer tier
        base_discount = cls._get_tier_discount(customer_type, quantity)
        
        # Add high-value purchase bonuses
        bonus_discount = cls._get_high_value_bonus(price)
        
        # Calculate total discount and cap at maximum
        total_discount = base_discount + bonus_discount
        return min(total_discount, ValidationRules.MAX_DISCOUNT)
    
    @staticmethod
    def _validate_inputs(price: float, quantity: int) -> bool:
        """Validate input parameters"""
        if not isinstance(price, (int, float)) or not isinstance(quantity, int):
            return False
        return price >= 0 and quantity >= 0
    
    @classmethod
    def _get_tier_discount(cls, customer_type: str, quantity: int) -> float:
        """Get discount based on customer tier and quantity"""
        tiers = cls.DISCOUNT_TIERS.get(customer_type, [])
        
        # Find applicable tier (highest tier where quantity >= min_quantity)
        applicable_discount = 0.0
        for tier in tiers:
            if quantity >= tier.min_quantity:
                applicable_discount = tier.discount_rate
                
        return applicable_discount
    
    @classmethod
    def _get_high_value_bonus(cls, price: float) -> float:
        """Calculate bonus discount for high-value purchases"""
        bonus = 0.0
        for threshold, discount in cls.HIGH_VALUE_THRESHOLDS:
            if price > threshold:
                bonus += discount
        return bonus


class Validator:
    """Centralized validation logic"""
    
    @staticmethod
    def validate_dict(data: Any, required_fields: List[str]) -> Optional[Dict[str, str]]:
        """
        Validate that data is a dict with required fields
        
        Returns:
            Error dict if validation fails, None if successful
        """
        if data is None:
            return {"status": "error", "message": "Data is None"}
            
        if not isinstance(data, dict):
            return {"status": "error", "message": "Data is not a dictionary"}
            
        for field in required_fields:
            if field not in data:
                return {"status": "error", "message": f"Missing required field: {field}"}
                
        return None
    
    @staticmethod
    def validate_range(value: Union[int, float], min_val: Union[int, float], 
                      max_val: Union[int, float], field_name: str) -> Optional[Dict[str, str]]:
        """
        Validate that value is within specified range
        
        Returns:
            Error dict if validation fails, None if successful
        """
        if value < min_val or value > max_val:
            return {"status": "error", "message": f"Invalid {field_name}: must be between {min_val} and {max_val}"}
        return None
    
    @staticmethod
    def validate_email(email: str) -> Optional[Dict[str, str]]:
        """
        Validate email format
        
        Returns:
            Error dict if validation fails, None if successful
        """
        if not isinstance(email, str):
            return {"status": "error", "message": "Email must be a string"}
            
        email = email.strip()
        
        if "@" not in email or "." not in email:
            return {"status": "error", "message": "Invalid email format"}
            
        if email.count("@") != 1:
            return {"status": "error", "message": "Email must contain exactly one @ symbol"}
            
        return None


class DataProcessor:
    """Refactored data processor with clean, modular design"""
    
    def __init__(self):
        self.validator = Validator()
        self.discount_calculator = DiscountCalculator()
        
    def process_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate user data
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            Processed user data or error dict
        """
        # Validate structure
        error = self.validator.validate_dict(user_data, ["name", "email", "age"])
        if error:
            return error
            
        # Validate age range
        error = self.validator.validate_range(
            user_data["age"], 
            ValidationRules.MIN_AGE, 
            ValidationRules.MAX_AGE, 
            "age"
        )
        if error:
            return error
            
        # Validate email
        error = self.validator.validate_email(user_data["email"])
        if error:
            return error
            
        # Process and return result
        return self._build_user_result(user_data)
    
    def _build_user_result(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build processed user result"""
        return {
            "name": user_data["name"].strip().title(),
            "email": user_data["email"].lower().strip(),
            "age": user_data["age"],
            "category": AgeCategory.get_category(user_data["age"]),
            "status": "success",
            "processed_at": datetime.now().isoformat()
        }
        
    def process_product_data(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate product data
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Processed product data or error dict
        """
        # Validate structure
        error = self.validator.validate_dict(product_data, ["name", "price", "quantity"])
        if error:
            return error
            
        # Validate price range
        error = self.validator.validate_range(
            product_data["price"],
            ValidationRules.MIN_PRICE,
            ValidationRules.MAX_PRICE,
            "price"
        )
        if error:
            return error
            
        # Validate quantity range
        error = self.validator.validate_range(
            product_data["quantity"],
            ValidationRules.MIN_QUANTITY,
            ValidationRules.MAX_QUANTITY,
            "quantity"
        )
        if error:
            return error
            
        # Process and return result
        return self._build_product_result(product_data)
    
    def _build_product_result(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build processed product result"""
        price = round(product_data["price"], 2)
        quantity = product_data["quantity"]
        
        return {
            "name": product_data["name"].strip().title(),
            "price": price,
            "quantity": quantity,
            "price_category": PriceCategory.get_category(price),
            "stock_status": StockStatus.get_status(quantity),
            "status": "success",
            "processed_at": datetime.now().isoformat()
        }
        
    def calculate_discount(self, price: float, customer_type: str, quantity: int) -> float:
        """
        Calculate discount (delegates to DiscountCalculator)
        
        Args:
            price: Item price
            customer_type: Type of customer
            quantity: Number of items
            
        Returns:
            Discount rate
        """
        return self.discount_calculator.calculate(price, customer_type, quantity)
        
    def batch_process(self, items: List[Dict[str, Any]], item_type: str) -> List[Dict[str, Any]]:
        """
        Process multiple items with proper error handling
        
        Args:
            items: List of items to process
            item_type: Type of items ('user' or 'product')
            
        Returns:
            List of processed results
        """
        if not items:
            return []
            
        # Map item types to processing methods
        processors = {
            "user": self.process_user_data,
            "product": self.process_product_data
        }
        
        processor = processors.get(item_type)
        if not processor:
            return [{"status": "error", "message": f"Unknown item type: {item_type}"}]
            
        # Process each item, continuing on errors
        return [processor(item) for item in items]
        
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate formatted report from results
        
        Args:
            results: List of processing results
            
        Returns:
            Formatted report string
        """
        if not results:
            return "No results to report"
            
        stats = self._calculate_statistics(results)
        return self._format_report(stats)
    
    def _calculate_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics from results"""
        total = len(results)
        success_count = sum(1 for r in results if r.get("status") == "success")
        error_count = total - success_count
        
        return {
            "total": total,
            "success": success_count,
            "errors": error_count,
            "success_rate": (success_count / total * 100) if total > 0 else 0,
            "error_rate": (error_count / total * 100) if total > 0 else 0
        }
    
    def _format_report(self, stats: Dict[str, Any]) -> str:
        """Format statistics into report string"""
        separator = "=" * 50
        sub_separator = "-" * 50
        
        lines = [
            separator,
            "Processing Report",
            separator,
            f"Generated at: {datetime.now().isoformat()}",
            sub_separator,
            f"Total Records: {stats['total']}",
            f"Successful: {stats['success']}",
            f"Failed: {stats['errors']}",
            sub_separator,
            f"Success Rate: {stats['success_rate']:.2f}%",
            f"Error Rate: {stats['error_rate']:.2f}%",
            separator
        ]
        
        return "\n".join(lines)


def main():
    """Main function demonstrating usage"""
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
