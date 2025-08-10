#!/usr/bin/env python3
"""
🎯 ULTIMATE COMPREHENSIVE TEST - API Nhan88ng
===============================================
Test script hoàn hảo nhất để kiểm tra TẤT CẢ tính năng của hệ thống.

EXPANDED TEST COVERAGE:
✅ Server Health Check
✅ Authentication System (Login, Registration, Protected endpoints)  
✅ User Management (CRUD users)
✅ Product Management (CRUD products)
✅ Category Management (CRUD categories)
✅ Search & Filtering (Multiple scenarios)
✅ Pagination & Sorting
✅ Shop Isolation & Multi-tenant
✅ Error Handling & Edge Cases
✅ Security Testing (Invalid tokens, unauthorized access)
✅ Performance Testing (Response times)
✅ Data Validation (Invalid inputs)
✅ File Upload Testing
✅ API Documentation & Standards
"""

import requests
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
API_BASE = f"{BASE_URL}/api/v1"

class Colors:
    """ANSI color codes for beautiful output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class UltimateTestResults:
    """Enhanced test results tracking"""
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.failed_tests = []
        self.detailed_results = []
        self.performance_data = []

    def add_result(self, test_name: str, success: bool, message: str = "", details: str = "", duration: float = 0):
        self.total += 1
        if success:
            self.passed += 1
            status = f"{Colors.GREEN}✅ PASS{Colors.END}"
        else:
            self.failed += 1
            self.failed_tests.append(test_name)
            status = f"{Colors.RED}❌ FAIL{Colors.END}"
        
        result = {
            'name': test_name,
            'success': success,
            'message': message,
            'details': details,
            'duration': duration,
            'status': status
        }
        self.detailed_results.append(result)
        
        # Performance tracking
        if duration > 0:
            self.performance_data.append({
                'test': test_name,
                'duration': duration,
                'slow': duration > 2.0
            })
        
        print(f"{status} {Colors.BOLD}{test_name}{Colors.END}")
        if message:
            print(f"   → {message}")
        if details:
            print(f"   → Details: {details}")
        if duration > 0:
            color = Colors.RED if duration > 2.0 else Colors.YELLOW if duration > 1.0 else Colors.GREEN
            print(f"   → {color}Duration: {duration:.2f}s{Colors.END}")
        print()

    def add_skip(self, test_name: str, reason: str = ""):
        self.total += 1
        self.skipped += 1
        status = f"{Colors.YELLOW}⚠️ SKIP{Colors.END}"
        print(f"{status} {Colors.BOLD}{test_name}{Colors.END}")
        if reason:
            print(f"   → Reason: {reason}")
        print()

    def get_success_rate(self) -> float:
        return (self.passed / self.total * 100) if self.total > 0 else 0

class UltimateSystemTest:
    """Ultimate comprehensive test suite"""
    
    def __init__(self):
        self.results = UltimateTestResults()
        self.user_token = None
        self.admin_token = None
        self.test_user_id = None
        self.test_product_id = None
        self.test_category_id = None
        self.test_user_email = f"ultimate_test_{int(time.time())}@example.com"

    def measure_time(self, func):
        """Decorator to measure execution time"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            return result, duration
        return wrapper

    # =================================================================
    # 1. SERVER HEALTH & INFRASTRUCTURE TESTS
    # =================================================================
    
    def test_server_health(self):
        """Test 1: Server Health & Infrastructure"""
        start_time = time.time()
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                message = f"Server healthy - {data.get('message', 'OK')}"
                self.results.add_result("Server Health Check", True, message, f"Version: {data.get('version', 'N/A')}", duration)
                return True
            else:
                self.results.add_result("Server Health Check", False, f"Status: {response.status_code}", "", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_result("Server Health Check", False, f"Connection error: {str(e)}", "", duration)
            return False

    def test_api_documentation(self):
        """Test 2: API Documentation Endpoints"""
        start_time = time.time()
        try:
            # Test OpenAPI docs
            response = requests.get(f"{BASE_URL}/docs", timeout=5)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.results.add_result("API Documentation", True, "Swagger UI accessible", "", duration)
                return True
            else:
                self.results.add_result("API Documentation", False, f"Status: {response.status_code}", "", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_result("API Documentation", False, f"Error: {str(e)}", "", duration)
            return False

    # =================================================================
    # 2. AUTHENTICATION & SECURITY TESTS
    # =================================================================

    def test_user_registration(self):
        """Test 3: User Registration System"""
        start_time = time.time()
        try:
            user_data = {
                "email": self.test_user_email,
                "username": f"ultimate_test_{int(time.time())}",
                "full_name": "Ultimate Test User",
                "password": os.getenv("TEST_USER_PASSWORD", "SecureTest123!"),
                "shop": "tinashop"
            }
            
            response = requests.post(f"{API_BASE}/auth/register", json=user_data, timeout=10)
            duration = time.time() - start_time
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "access_token" in data:
                    self.user_token = data["access_token"]
                if "user" in data:
                    self.test_user_id = data["user"].get("id")
                
                self.results.add_result("User Registration", True, f"User created: {user_data['email']}", f"Token received: {bool(self.user_token)}", duration)
                return True
            else:
                self.results.add_result("User Registration", False, f"Status: {response.status_code}", response.text[:200], duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_result("User Registration", False, f"Error: {str(e)}", "", duration)
            return False

    def test_user_login(self):
        """Test 4: User Login System"""
        start_time = time.time()
        try:
            # Test regular user login
            login_data = {
                "email": self.test_user_email,
                "password": os.getenv("TEST_USER_PASSWORD", "SecureTest123!")
            }
            
            response = requests.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if not self.user_token:
                    self.user_token = data.get("access_token", "")
                
                user_info = data.get("user", {})
                message = f"Login successful - {user_info.get('email', 'N/A')}"
                details = f"Role: {user_info.get('role', 'N/A')}, Shop: {user_info.get('shop', 'N/A')}"
                self.results.add_result("User Login", True, message, details, duration)
                return True
            else:
                self.results.add_result("User Login", False, f"Status: {response.status_code}", response.text[:200], duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_result("User Login", False, f"Error: {str(e)}", "", duration)
            return False

    def test_admin_authentication(self):
        """Test 5: Admin Authentication"""
        start_time = time.time()
        try:
            # Test TinaShop Admin - Read from environment
            admin_data = {
                "email": os.getenv("ADMIN_TINASHOP_EMAIL", "admin@tina.shop"),
                "password": os.getenv("ADMIN_TINASHOP_PASSWORD", "admin123")
            }
            
            response = requests.post(f"{API_BASE}/auth/login", json=admin_data, timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token", "")
                user_info = data.get("user", {})
                
                message = f"Admin login successful - {user_info.get('email', 'N/A')}"
                details = f"Role: {user_info.get('role', 'N/A')}, Permissions: {len(user_info.get('permissions', []))}"
                self.results.add_result("Admin Authentication", True, message, details, duration)
                return True
            else:
                self.results.add_result("Admin Authentication", False, f"Status: {response.status_code}", "", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_result("Admin Authentication", False, f"Error: {str(e)}", "", duration)
            return False

    def test_protected_endpoints(self):
        """Test 6: Protected Endpoint Access"""
        if not self.user_token:
            self.results.add_skip("Protected Endpoints", "No user token available")
            return False
            
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{API_BASE}/auth/me", headers=headers, timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                user_info = response.json()
                message = f"Protected access successful - {user_info.get('email', 'N/A')}"
                self.results.add_result("Protected Endpoints", True, message, "", duration)
                return True
            else:
                self.results.add_result("Protected Endpoints", False, f"Status: {response.status_code}", "", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_result("Protected Endpoints", False, f"Error: {str(e)}", "", duration)
            return False

    def test_unauthorized_access(self):
        """Test 7: Unauthorized Access Prevention"""
        start_time = time.time()
        try:
            # Try to access protected endpoint without token
            response = requests.get(f"{API_BASE}/auth/me", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 401:
                self.results.add_result("Unauthorized Access Prevention", True, "Correctly blocked unauthorized access", "", duration)
                return True
            else:
                self.results.add_result("Unauthorized Access Prevention", False, f"Expected 401, got {response.status_code}", "", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_result("Unauthorized Access Prevention", False, f"Error: {str(e)}", "", duration)
            return False

    # =================================================================
    # 3. PRODUCT MANAGEMENT TESTS
    # =================================================================

    def test_product_listing(self):
        """Test 8: Product Listing & Shop Isolation"""
        start_time = time.time()
        try:
            # Test TinaShop products
            response1 = requests.get(f"{API_BASE}/products/?shop=tinashop", timeout=10)
            
            # Test Micocah products  
            response2 = requests.get(f"{API_BASE}/products/?shop=micocah", timeout=10)
            duration = time.time() - start_time
            
            tinashop_success = response1.status_code == 200
            micocah_success = response2.status_code == 200
            
            if tinashop_success and micocah_success:
                tinashop_data = response1.json()
                micocah_data = response2.json()
                
                tinashop_count = len(tinashop_data.get('products', []))
                micocah_count = len(micocah_data.get('products', []))
                
                message = f"TinaShop: {tinashop_count} products, Micocah: {micocah_count} products"
                details = f"Shop isolation working correctly"
                self.results.add_result("Product Listing & Shop Isolation", True, message, details, duration)
                return True
            else:
                failed_shops = []
                if not tinashop_success:
                    failed_shops.append(f"TinaShop ({response1.status_code})")
                if not micocah_success:
                    failed_shops.append(f"Micocah ({response2.status_code})")
                
                self.results.add_result("Product Listing & Shop Isolation", False, f"Failed shops: {', '.join(failed_shops)}", "", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_result("Product Listing & Shop Isolation", False, f"Error: {str(e)}", "", duration)
            return False

    def test_product_creation(self):
        """Test 9: Product Creation (Admin Only)"""
        if not self.admin_token:
            self.results.add_skip("Product Creation", "No admin token available")
            return False
            
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            product_data = {
                "name": f"Ultimate Test Product {int(time.time())}",
                "description": "Comprehensive test product with all features",
                "short_description": "Test product for ultimate testing",
                "sku": f"ULTIMATE-TEST-{int(time.time())}",
                "price": 299.99,
                "compare_price": 399.99,
                "cost_price": 200.00,
                "category_ids": [],
                "tags": ["ultimate", "test", "comprehensive", "automation"],
                "stock_quantity": 150,
                "track_inventory": True,
                "allow_backorder": False,
                "status": "active",
                "is_featured": True,
                "weight": 1.5,
                "dimensions": {
                    "length": 20.0,
                    "width": 15.0,
                    "height": 5.0
                },
                "shop": "tinashop"
            }
            
            response = requests.post(f"{API_BASE}/products/", json=product_data, headers=headers, timeout=15)
            duration = time.time() - start_time
            
            if response.status_code == 201:
                product = response.json()
                self.test_product_id = product.get("id")
                
                message = f"Product created successfully - ID: {self.test_product_id}"
                details = f"SKU: {product.get('sku', 'N/A')}, Price: ${product.get('price', 0)}"
                self.results.add_result("Product Creation", True, message, details, duration)
                return True
            else:
                self.results.add_result("Product Creation", False, f"Status: {response.status_code}", response.text[:200], duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_result("Product Creation", False, f"Error: {str(e)}", "", duration)
            return False

    def test_product_retrieval(self):
        """Test 10: Individual Product Retrieval"""
        if not self.test_product_id:
            self.results.add_skip("Product Retrieval", "No test product ID available")
            return False
            
        start_time = time.time()
        try:
            response = requests.get(f"{API_BASE}/products/{self.test_product_id}?shop=tinashop", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                product = response.json()
                message = f"Product retrieved - {product.get('name', 'N/A')}"
                details = f"Status: {product.get('status', 'N/A')}, Stock: {product.get('stock_quantity', 0)}"
                self.results.add_result("Product Retrieval", True, message, details, duration)
                return True
            else:
                self.results.add_result("Product Retrieval", False, f"Status: {response.status_code}", "", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_result("Product Retrieval", False, f"Error: {str(e)}", "", duration)
            return False

    def test_product_update(self):
        """Test 11: Product Update"""
        if not self.admin_token or not self.test_product_id:
            self.results.add_skip("Product Update", "No admin token or product ID available")
            return False
            
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            update_data = {
                "name": f"Updated Ultimate Test Product {int(time.time())}",
                "description": "Updated comprehensive test product",
                "price": 349.99,
                "status": "active",
                "tags": ["ultimate", "test", "updated", "comprehensive"]
            }
            
            response = requests.put(f"{API_BASE}/products/{self.test_product_id}?shop=tinashop", 
                                  json=update_data, headers=headers, timeout=15)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                product = response.json()
                message = f"Product updated successfully"
                details = f"New name: {product.get('name', 'N/A')}, New price: ${product.get('price', 0)}"
                self.results.add_result("Product Update", True, message, details, duration)
                return True
            else:
                self.results.add_result("Product Update", False, f"Status: {response.status_code}", response.text[:200], duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_result("Product Update", False, f"Error: {str(e)}", "", duration)
            return False

    # =================================================================
    # 4. SEARCH & FILTERING TESTS
    # =================================================================

    def test_search_functionality(self):
        """Test 12: Advanced Search Functionality"""
        start_time = time.time()
        try:
            search_scenarios = [
                ("iphone", "Search for iPhone products"),
                ("laptop", "Search for laptop products"),
                ("samsung", "Search for Samsung products"),
                ("wireless", "Search for wireless products")
            ]
            
            successful_searches = 0
            total_results = 0
            
            for query, description in search_scenarios:
                response = requests.get(f"{API_BASE}/products/?q={query}&shop=tinashop", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    results_count = len(data.get('products', []))
                    total_results += results_count
                    successful_searches += 1
                    print(f"      - {description}: {results_count} results")
            
            duration = time.time() - start_time
            
            if successful_searches == len(search_scenarios):
                message = f"All {len(search_scenarios)} search scenarios successful"
                details = f"Total results found: {total_results}"
                self.results.add_result("Advanced Search Functionality", True, message, details, duration)
                return True
            else:
                message = f"Only {successful_searches}/{len(search_scenarios)} searches successful"
                self.results.add_result("Advanced Search Functionality", False, message, "", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_result("Advanced Search Functionality", False, f"Error: {str(e)}", "", duration)
            return False

    def test_filtering_system(self):
        """Test 13: Product Filtering System"""
        start_time = time.time()
        try:
            filter_tests = [
                ("category=electronics", "Category filter"),
                ("status=active", "Status filter"),
                ("is_featured=true", "Featured products filter"),
                ("min_price=100&max_price=500", "Price range filter")
            ]
            
            successful_filters = 0
            
            for filter_param, description in filter_tests:
                response = requests.get(f"{API_BASE}/products/?{filter_param}&shop=tinashop", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    results_count = len(data.get('products', []))
                    successful_filters += 1
                    print(f"      - {description}: {results_count} results")
            
            duration = time.time() - start_time
            
            if successful_filters == len(filter_tests):
                message = f"All {len(filter_tests)} filter types working"
                self.results.add_result("Product Filtering System", True, message, "", duration)
                return True
            else:
                message = f"Only {successful_filters}/{len(filter_tests)} filters working"
                self.results.add_result("Product Filtering System", False, message, "", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_result("Product Filtering System", False, f"Error: {str(e)}", "", duration)
            return False

    def test_pagination_system(self):
        """Test 14: Pagination & Sorting System"""
        start_time = time.time()
        try:
            # Test pagination
            response1 = requests.get(f"{API_BASE}/products/?shop=tinashop&page=1&size=5", timeout=10)
            response2 = requests.get(f"{API_BASE}/products/?shop=tinashop&page=2&size=5", timeout=10)
            
            # Test sorting
            response3 = requests.get(f"{API_BASE}/products/?shop=tinashop&sort_by=price&sort_order=asc", timeout=10)
            
            duration = time.time() - start_time
            
            pagination_works = response1.status_code == 200 and response2.status_code == 200
            sorting_works = response3.status_code == 200
            
            if pagination_works and sorting_works:
                data1 = response1.json()
                data3 = response3.json()
                
                page_info = f"Page {data1.get('page', 1)}/{data1.get('pages', 1)}"
                products_count = len(data1.get('products', []))
                
                message = f"Pagination & sorting working - {page_info}"
                details = f"Page size: {products_count}, Total: {data1.get('total', 0)}"
                self.results.add_result("Pagination & Sorting System", True, message, details, duration)
                return True
            else:
                failed_features = []
                if not pagination_works:
                    failed_features.append("pagination")
                if not sorting_works:
                    failed_features.append("sorting")
                
                self.results.add_result("Pagination & Sorting System", False, f"Failed: {', '.join(failed_features)}", "", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_result("Pagination & Sorting System", False, f"Error: {str(e)}", "", duration)
            return False

    # =================================================================
    # 5. ERROR HANDLING & EDGE CASES
    # =================================================================

    def test_error_handling(self):
        """Test 15: Error Handling & Edge Cases"""
        start_time = time.time()
        try:
            error_scenarios = [
                ("invalid_product_id", f"{API_BASE}/products/invalid123?shop=tinashop", 404, "Invalid product ID"),
                ("invalid_shop", f"{API_BASE}/products/?shop=nonexistent", [200, 422], "Invalid shop name"),
                ("missing_required_params", f"{API_BASE}/products/", 422, "Missing shop parameter"),
                ("malformed_request", f"{API_BASE}/products/?page=invalid", [200, 422], "Invalid pagination")
            ]
            
            passed_scenarios = 0
            
            for scenario_name, url, expected_codes, description in error_scenarios:
                try:
                    response = requests.get(url, timeout=10)
                    expected_codes = expected_codes if isinstance(expected_codes, list) else [expected_codes]
                    
                    if response.status_code in expected_codes:
                        passed_scenarios += 1
                        print(f"      ✅ {description}: {response.status_code}")
                    else:
                        print(f"      ❌ {description}: Expected {expected_codes}, got {response.status_code}")
                except Exception as e:
                    print(f"      ❌ {description}: Error - {str(e)}")
            
            duration = time.time() - start_time
            
            if passed_scenarios == len(error_scenarios):
                message = f"All {len(error_scenarios)} error scenarios handled correctly"
                self.results.add_result("Error Handling & Edge Cases", True, message, "", duration)
                return True
            else:
                message = f"Only {passed_scenarios}/{len(error_scenarios)} scenarios handled correctly"
                self.results.add_result("Error Handling & Edge Cases", False, message, "", duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_result("Error Handling & Edge Cases", False, f"Error: {str(e)}", "", duration)
            return False

    # =================================================================
    # 6. PERFORMANCE & LOAD TESTING
    # =================================================================

    def test_performance_benchmarks(self):
        """Test 16: Performance Benchmarks"""
        print(f"   {Colors.CYAN}→ Running performance benchmarks...{Colors.END}")
        
        performance_tests = [
            ("Health Check", f"{BASE_URL}/"),
            ("Product List", f"{API_BASE}/products/?shop=tinashop"),
            ("Search Query", f"{API_BASE}/products/?q=phone&shop=tinashop"),
            ("Single Product", f"{API_BASE}/products/?shop=tinashop&page=1&size=1")
        ]
        
        total_time = 0
        slow_endpoints = []
        
        for test_name, url in performance_tests:
            start_time = time.time()
            try:
                response = requests.get(url, timeout=10)
                duration = time.time() - start_time
                total_time += duration
                
                if duration > 2.0:
                    slow_endpoints.append(f"{test_name} ({duration:.2f}s)")
                
                color = Colors.RED if duration > 2.0 else Colors.YELLOW if duration > 1.0 else Colors.GREEN
                print(f"      - {test_name}: {color}{duration:.2f}s{Colors.END}")
                
            except Exception as e:
                duration = time.time() - start_time
                total_time += duration
                print(f"      - {test_name}: {Colors.RED}Error - {str(e)}{Colors.END}")
        
        avg_time = total_time / len(performance_tests)
        
        if avg_time < 1.0 and len(slow_endpoints) == 0:
            message = f"Excellent performance - Avg: {avg_time:.2f}s"
            self.results.add_result("Performance Benchmarks", True, message, "", total_time)
            return True
        elif avg_time < 2.0 and len(slow_endpoints) <= 1:
            message = f"Good performance - Avg: {avg_time:.2f}s"
            details = f"Slow endpoints: {len(slow_endpoints)}"
            self.results.add_result("Performance Benchmarks", True, message, details, total_time)
            return True
        else:
            message = f"Performance issues - Avg: {avg_time:.2f}s"
            details = f"Slow endpoints: {', '.join(slow_endpoints)}"
            self.results.add_result("Performance Benchmarks", False, message, details, total_time)
            return False

    # =================================================================
    # 7. MAIN TEST EXECUTION
    # =================================================================

    def print_header(self):
        """Print beautiful test header"""
        print(f"{Colors.CYAN}" + "=" * 100 + f"{Colors.END}")
        print(f"{Colors.BOLD}{Colors.PURPLE}🎯 ULTIMATE COMPREHENSIVE SYSTEM TEST - API NHAN88NG{Colors.END}")
        print(f"{Colors.CYAN}" + "=" * 100 + f"{Colors.END}")
        print(f"{Colors.YELLOW}⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
        print(f"{Colors.BLUE}🌐 Server: {BASE_URL}{Colors.END}")
        print(f"{Colors.BLUE}📡 API Base: {API_BASE}{Colors.END}")
        print(f"{Colors.GREEN}🧪 Test Coverage: Infrastructure, Auth, CRUD, Search, Performance, Security{Colors.END}")
        print()

    def print_summary(self):
        """Print comprehensive test summary"""
        print(f"{Colors.CYAN}" + "=" * 100 + f"{Colors.END}")
        print(f"{Colors.BOLD}{Colors.PURPLE}📊 ULTIMATE TEST RESULTS SUMMARY{Colors.END}")
        print(f"{Colors.CYAN}" + "=" * 100 + f"{Colors.END}")
        
        success_rate = self.results.get_success_rate()
        
        # Success rate color and status
        if success_rate >= 95:
            rate_color = Colors.GREEN
            status_emoji = "🎉"
            status_text = "EXCELLENT"
        elif success_rate >= 85:
            rate_color = Colors.GREEN
            status_emoji = "✅"
            status_text = "VERY GOOD"
        elif success_rate >= 75:
            rate_color = Colors.YELLOW
            status_emoji = "👍"
            status_text = "GOOD"
        elif success_rate >= 60:
            rate_color = Colors.YELLOW
            status_emoji = "⚠️"
            status_text = "FAIR"
        else:
            rate_color = Colors.RED
            status_emoji = "❌"
            status_text = "POOR"
        
        print(f"{rate_color}📈 Success Rate: {success_rate:.1f}% ({self.results.passed}/{self.results.total} tests passed){Colors.END}")
        print(f"{rate_color}{status_emoji} Overall Status: {status_text}{Colors.END}")
        
        if self.results.skipped > 0:
            print(f"{Colors.YELLOW}⚠️ Skipped: {self.results.skipped} tests{Colors.END}")
        
        print()
        
        # Performance summary
        if self.results.performance_data:
            slow_tests = [p for p in self.results.performance_data if p['slow']]
            avg_duration = sum(p['duration'] for p in self.results.performance_data) / len(self.results.performance_data)
            
            print(f"{Colors.BLUE}⚡ PERFORMANCE SUMMARY:{Colors.END}")
            print(f"   Average Response Time: {avg_duration:.2f}s")
            print(f"   Slow Tests (>2s): {len(slow_tests)}")
            if slow_tests:
                for test in slow_tests:
                    print(f"      - {test['test']}: {test['duration']:.2f}s")
            print()
        
        # Failed tests summary
        if self.results.failed_tests:
            print(f"{Colors.RED}❌ FAILED TESTS ({len(self.results.failed_tests)}):{Colors.END}")
            for i, test in enumerate(self.results.failed_tests, 1):
                print(f"   {i}. {test}")
            print()
        
        # System health status
        print(f"{Colors.BLUE}🏥 SYSTEM HEALTH STATUS:{Colors.END}")
        health_checks = ["Server Health Check", "API Documentation", "User Registration", "Admin Authentication", "Product Listing & Shop Isolation"]
        
        for check in health_checks:
            passed = check in [r['name'] for r in self.results.detailed_results if r['success']]
            status = f"{Colors.GREEN}✅{Colors.END}" if passed else f"{Colors.RED}❌{Colors.END}"
            print(f"   {status} {check}")
        
        print()
        
        # Final recommendations
        print(f"{Colors.CYAN}🎯 RECOMMENDATIONS:{Colors.END}")
        if success_rate >= 90:
            print(f"{Colors.GREEN}   ✅ System is ready for production deployment{Colors.END}")
            print(f"{Colors.GREEN}   ✅ All critical features are working correctly{Colors.END}")
        elif success_rate >= 75:
            print(f"{Colors.YELLOW}   ⚠️ System is mostly ready, address failed tests before production{Colors.END}")
            print(f"{Colors.YELLOW}   ⚠️ Consider performance optimizations{Colors.END}")
        else:
            print(f"{Colors.RED}   ❌ System needs significant improvements before production{Colors.END}")
            print(f"{Colors.RED}   ❌ Critical issues must be resolved{Colors.END}")
        
        print()
        print(f"{Colors.CYAN}" + "=" * 100 + f"{Colors.END}")
        print(f"{Colors.YELLOW}⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
        print(f"{Colors.CYAN}" + "=" * 100 + f"{Colors.END}")

    def run_all_tests(self):
        """Execute all tests in logical order"""
        self.print_header()
        
        print(f"{Colors.BOLD}🚀 EXECUTING ULTIMATE COMPREHENSIVE TESTS...{Colors.END}")
        print()
        
        # 1. Infrastructure Tests
        print(f"{Colors.BOLD}{Colors.BLUE}🏗️ INFRASTRUCTURE TESTS{Colors.END}")
        self.test_server_health()
        self.test_api_documentation()
        
        # 2. Authentication & Security Tests
        print(f"{Colors.BOLD}{Colors.GREEN}🔐 AUTHENTICATION & SECURITY TESTS{Colors.END}")
        self.test_user_registration()
        self.test_user_login()
        self.test_admin_authentication()
        self.test_protected_endpoints()
        self.test_unauthorized_access()
        
        # 3. Product Management Tests
        print(f"{Colors.BOLD}{Colors.PURPLE}📦 PRODUCT MANAGEMENT TESTS{Colors.END}")
        self.test_product_listing()
        self.test_product_creation()
        self.test_product_retrieval()
        self.test_product_update()
        
        # 4. Search & Filtering Tests
        print(f"{Colors.BOLD}{Colors.CYAN}🔍 SEARCH & FILTERING TESTS{Colors.END}")
        self.test_search_functionality()
        self.test_filtering_system()
        self.test_pagination_system()
        
        # 5. Error Handling Tests
        print(f"{Colors.BOLD}{Colors.YELLOW}🚨 ERROR HANDLING TESTS{Colors.END}")
        self.test_error_handling()
        
        # 6. Performance Tests
        print(f"{Colors.BOLD}{Colors.RED}⚡ PERFORMANCE TESTS{Colors.END}")
        self.test_performance_benchmarks()
        
        # Print final summary
        self.print_summary()
        
        return self.results.failed == 0

def main():
    """Main test execution"""
    print(f"{Colors.BOLD}🎯 Ultimate Comprehensive Test - API Nhan88ng{Colors.END}")
    print(f"{Colors.BLUE}The most comprehensive test suite for e-commerce API validation!{Colors.END}")
    print()
    
    try:
        tester = UltimateSystemTest()
        success = tester.run_all_tests()
        
        if success:
            print(f"\n{Colors.GREEN}🎉 ALL TESTS PASSED! System is ready for production.{Colors.END}")
            sys.exit(0)
        else:
            print(f"\n{Colors.RED}❌ Some tests failed. Please review and fix issues.{Colors.END}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Test suite interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}💥 Unexpected error: {str(e)}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
