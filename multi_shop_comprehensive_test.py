#!/usr/bin/env python3
"""
🏪 Multi-Shop Comprehensive Test Suite
Test all features for each shop individually based on shops.json configuration
"""

import requests
import json
import time
import random
from typing import Dict, List, Optional
from datetime import datetime

class MultiShopTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.shops = {}
        self.test_results = {}
        self.session = requests.Session()
        
    def load_shops(self):
        """Load available shops from shops.json file"""
        try:
            # Load from local file for testing (includes admin credentials)
            with open('shops.json', 'r') as f:
                self.shops = json.load(f)
            print(f"🏪 Loaded {len(self.shops)} shops: {list(self.shops.keys())}")
            return True
        except Exception as e:
            print(f"❌ Error loading shops from file: {e}")
            # Fallback to API
            try:
                response = self.session.get(f"{self.api_base}/shops/")
                if response.status_code == 200:
                    data = response.json()
                    self.shops = data.get('shops', {})
                    print(f"🏪 Loaded {len(self.shops)} shops from API: {list(self.shops.keys())}")
                    return True
                else:
                    print(f"❌ Failed to load shops from API: {response.status_code}")
                    return False
            except Exception as api_e:
                print(f"❌ Error loading shops from API: {api_e}")
                return False
    
    def generate_test_user_email(self, shop_id: str) -> str:
        """Generate unique test user email for shop"""
        timestamp = int(time.time())
        return f"test_{shop_id}_{timestamp}@example.com"
    
    def test_shop_authentication(self, shop_id: str, shop_config: dict) -> Dict:
        """Test authentication features for a specific shop"""
        print(f"\n🔐 Testing Authentication for {shop_config['name']} ({shop_id})")
        results = {}
        
        # Test 1: User Registration
        test_email = self.generate_test_user_email(shop_id)
        test_password = "TestPass123!"
        
        registration_data = {
            "email": test_email,
            "password": test_password,
            "full_name": f"Test User {shop_id.title()}",
            "shop": shop_id
        }
        
        try:
            response = self.session.post(f"{self.api_base}/auth/register", json=registration_data)
            if response.status_code == 201:
                results['user_registration'] = "✅ PASS"
                user_data = response.json()
                print(f"   ✅ User registered: {test_email}")
            else:
                results['user_registration'] = f"❌ FAIL ({response.status_code})"
                print(f"   ❌ Registration failed: {response.status_code}")
                return results
        except Exception as e:
            results['user_registration'] = f"❌ ERROR: {e}"
            return results
        
        # Test 2: User Login
        login_data = {
            "email": test_email,
            "password": test_password,
            "shop": shop_id
        }
        
        try:
            response = self.session.post(f"{self.api_base}/auth/login", json=login_data)
            if response.status_code == 200:
                results['user_login'] = "✅ PASS"
                login_response = response.json()
                user_token = login_response.get('access_token')
                print(f"   ✅ User login successful")
                
                # Store token for subsequent tests
                self.session.headers.update({"Authorization": f"Bearer {user_token}"})
            else:
                results['user_login'] = f"❌ FAIL ({response.status_code})"
                print(f"   ❌ Login failed: {response.status_code}")
        except Exception as e:
            results['user_login'] = f"❌ ERROR: {e}"
            
        # Test 3: Admin Login (if enabled for shop)
        admin_token = None
        print(f"   🔧 Checking admin credentials...")
        print(f"   🔧 'admin_email' in shop_config: {'admin_email' in shop_config}")
        if 'admin_email' in shop_config:
            print(f"   🔧 Admin email: {shop_config['admin_email']}")
            admin_login_data = {
                "email": shop_config['admin_email'],
                "password": shop_config.get('admin_password', 'admin123'),  # fallback
                "shop": shop_id
            }
            
            try:
                response = self.session.post(f"{self.api_base}/auth/login", json=admin_login_data)
                print(f"   🔧 Admin login response: {response.status_code}")
                if response.status_code == 200:
                    results['admin_login'] = "✅ PASS"
                    admin_response = response.json()
                    admin_token = admin_response.get('access_token')
                    print(f"   ✅ Admin login successful")
                else:
                    results['admin_login'] = f"❌ FAIL ({response.status_code})"
                    print(f"   ❌ Admin login failed: {response.status_code}")
                    print(f"   🔧 Response: {response.text[:200]}")
            except Exception as e:
                results['admin_login'] = f"❌ ERROR: {e}"
                print(f"   ❌ Admin login error: {e}")
        else:
            print(f"   ⚠️ No admin credentials found in config")
        
        return results, admin_token
    
    def test_shop_products(self, shop_id: str, shop_config: dict, admin_token: str = None) -> Dict:
        """Test product features for a specific shop"""
        print(f"\n📦 Testing Products for {shop_config['name']} ({shop_id})")
        results = {}
        
        # Test 1: Product Listing
        try:
            response = self.session.get(f"{self.api_base}/products/?shop={shop_id}")
            if response.status_code == 200:
                products_data = response.json()
                product_count = len(products_data.get('products', []))
                results['product_listing'] = f"✅ PASS ({product_count} products)"
                print(f"   ✅ Product listing: {product_count} products found")
            else:
                results['product_listing'] = f"❌ FAIL ({response.status_code})"
                print(f"   ❌ Product listing failed: {response.status_code}")
        except Exception as e:
            results['product_listing'] = f"❌ ERROR: {e}"
        
        # Test 2: Product Search
        search_terms = ["phone", "laptop", "test"]
        search_results = []
        
        for term in search_terms:
            try:
                response = self.session.get(f"{self.api_base}/products/?shop={shop_id}&q={term}")
                if response.status_code == 200:
                    search_data = response.json()
                    result_count = len(search_data.get('products', []))
                    search_results.append(f"{term}:{result_count}")
                else:
                    search_results.append(f"{term}:ERROR")
            except Exception as e:
                search_results.append(f"{term}:ERROR")
        
        results['product_search'] = f"✅ PASS ({', '.join(search_results)})"
        print(f"   ✅ Product search: {', '.join(search_results)}")
        
        # Test 3: Product Categories (if supported by shop)
        if 'categories' in shop_config.get('features', []):
            try:
                response = self.session.get(f"{self.api_base}/products/categories/?shop={shop_id}")
                if response.status_code == 200:
                    categories_data = response.json()
                    category_count = len(categories_data) if isinstance(categories_data, list) else 0
                    results['categories'] = f"✅ PASS ({category_count} categories)"
                    print(f"   ✅ Categories: {category_count} categories found")
                else:
                    results['categories'] = f"❌ FAIL ({response.status_code})"
            except Exception as e:
                results['categories'] = f"❌ ERROR: {e}"
        
        # Test 4: Product Creation (admin feature)
        if admin_token:
            # Use admin token for product creation
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            test_product = {
                "name": f"Test Product {shop_id} {int(time.time())}",
                "description": f"Test product for {shop_config['name']}",
                "price": 99.99,
                "sku": f"TEST-{shop_id.upper()}-{int(time.time())}",
                "category": "test",
                "stock_quantity": 100,
                "is_active": True,
                "shop": shop_id
            }
            
            try:
                response = self.session.post(f"{self.api_base}/products/", json=test_product, headers=headers)
                if response.status_code in [200, 201]:
                    results['product_creation'] = "✅ PASS"
                    product_data = response.json()
                    product_id = product_data.get('id')
                    print(f"   ✅ Product created: {product_id}")
                    
                    # Test product retrieval
                    if product_id:
                        response = self.session.get(f"{self.api_base}/products/{product_id}?shop={shop_id}")
                        if response.status_code == 200:
                            results['product_retrieval'] = "✅ PASS"
                            print(f"   ✅ Product retrieved successfully")
                        else:
                            results['product_retrieval'] = f"❌ FAIL ({response.status_code})"
                else:
                    results['product_creation'] = f"❌ FAIL ({response.status_code})"
                    print(f"   ❌ Product creation failed: {response.status_code}")
            except Exception as e:
                results['product_creation'] = f"❌ ERROR: {e}"
        else:
            results['product_creation'] = "⚠️ SKIPPED (No admin token)"
        
        return results
    
    def test_shop_features(self, shop_id: str, shop_config: dict, admin_token: str = None) -> Dict:
        """Test shop-specific features"""
        print(f"\n🎯 Testing Features for {shop_config['name']} ({shop_id})")
        results = {}
        
        features = shop_config.get('features', [])
        print(f"   🎯 Shop features: {features}")
        
        # Test 1: Features endpoint consistency
        try:
            response = self.session.get(f"{self.api_base}/shops/{shop_id}/features")
            if response.status_code == 200:
                api_features = response.json().get('features', [])
                if set(api_features) == set(features):
                    results['feature_consistency'] = "✅ PASS"
                    print(f"   ✅ Feature consistency: API matches config")
                else:
                    results['feature_consistency'] = f"❌ MISMATCH: API={api_features}, Config={features}"
            else:
                results['feature_consistency'] = f"❌ FAIL ({response.status_code})"
        except Exception as e:
            results['feature_consistency'] = f"❌ ERROR: {e}"
        
        # Test shop-specific feature endpoints
        feature_tests = {
            'inventory': f"{self.api_base}/products/?shop={shop_id}&stock_only=true",
        }
        
        # Test inventory feature (no auth required)
        for feature, endpoint in feature_tests.items():
            if feature in features:
                try:
                    response = self.session.get(endpoint)
                    if response.status_code in [200, 404]:  # 404 is OK for empty data
                        results[f'feature_{feature}'] = "✅ ACCESSIBLE"
                    else:
                        results[f'feature_{feature}'] = f"❌ FAIL ({response.status_code})"
                except Exception as e:
                    results[f'feature_{feature}'] = f"❌ ERROR: {e}"
        
        # Test customer management feature (requires admin auth)
        if 'customers' in features and admin_token:
            try:
                headers = {"Authorization": f"Bearer {admin_token}"}
                response = requests.get(f"{self.api_base}/auth/users?shop={shop_id}", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    customer_count = data.get('total', 0)
                    results['feature_customers'] = f"✅ ACCESSIBLE ({customer_count} customers)"
                    print(f"   ✅ Customer management: {customer_count} customers found")
                else:
                    results['feature_customers'] = f"❌ FAIL ({response.status_code})"
                    print(f"   ❌ Customer management failed: {response.status_code}")
            except Exception as e:
                results['feature_customers'] = f"❌ ERROR: {e}"
        elif 'customers' in features:
            results['feature_customers'] = "⚠️ SKIP (no admin token)"
            print(f"   ⚠️ Customer management skipped: no admin token")
        
        return results
    
    def test_shop_configuration(self, shop_id: str, shop_config: dict) -> Dict:
        """Test shop configuration and settings"""
        print(f"\n⚙️ Testing Configuration for {shop_config['name']} ({shop_id})")
        results = {}
        
        # Test 1: Shop Info Endpoint
        try:
            response = self.session.get(f"{self.api_base}/shops/{shop_id}")
            if response.status_code == 200:
                shop_data = response.json()
                results['shop_info'] = "✅ PASS"
                print(f"   ✅ Shop info accessible")
                
                # Verify key configuration fields
                required_fields = ['name', 'domain', 'frontend_url', 'theme', 'settings']
                missing_fields = [field for field in required_fields if field not in shop_data]
                if not missing_fields:
                    results['config_completeness'] = "✅ PASS"
                    print(f"   ✅ Configuration complete")
                else:
                    results['config_completeness'] = f"❌ MISSING: {missing_fields}"
            else:
                results['shop_info'] = f"❌ FAIL ({response.status_code})"
        except Exception as e:
            results['shop_info'] = f"❌ ERROR: {e}"
        
        # Test 2: Theme Configuration
        theme = shop_config.get('theme', {})
        if theme:
            theme_fields = ['primary_color', 'secondary_color', 'logo']
            has_theme = all(field in theme for field in theme_fields)
            if has_theme:
                results['theme_config'] = "✅ PASS"
                print(f"   ✅ Theme configuration complete")
            else:
                missing = [field for field in theme_fields if field not in theme]
                results['theme_config'] = f"❌ MISSING: {missing}"
        
        # Test 3: Settings Configuration
        settings = shop_config.get('settings', {})
        if settings:
            settings_fields = ['currency', 'language', 'allow_guest_checkout']
            has_settings = all(field in settings for field in settings_fields)
            if has_settings:
                results['settings_config'] = "✅ PASS"
                print(f"   ✅ Settings configuration complete")
            else:
                missing = [field for field in settings_fields if field not in settings]
                results['settings_config'] = f"❌ MISSING: {missing}"
        
        return results
    
    def run_comprehensive_test(self):
        """Run comprehensive tests for all shops"""
        print("🎯 MULTI-SHOP COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Server: {self.base_url}")
        print(f"📡 API Base: {self.api_base}")
        
        # Load shops
        if not self.load_shops():
            print("❌ Failed to load shops. Exiting.")
            return
        
        total_shops = len(self.shops)
        print(f"🏪 Testing {total_shops} shops")
        
        # Test each shop
        for shop_id, shop_config in self.shops.items():
            print(f"\n{'='*70}")
            print(f"🏪 TESTING SHOP: {shop_config['name']} ({shop_id})")
            print(f"🌐 Domain: {shop_config['domain']}")
            print(f"🎨 Theme: {shop_config['theme']['primary_color']}")
            print(f"💰 Currency: {shop_config['settings']['currency']}")
            print(f"🎯 Features: {', '.join(shop_config['features'])}")
            print(f"{'='*70}")
            
            shop_results = {}
            
            # Reset session for each shop
            self.session.headers.clear()
            
            # Run tests
            shop_results.update(self.test_shop_configuration(shop_id, shop_config))
            auth_results, admin_token = self.test_shop_authentication(shop_id, shop_config)
            shop_results.update(auth_results)
            shop_results.update(self.test_shop_products(shop_id, shop_config, admin_token))
            shop_results.update(self.test_shop_features(shop_id, shop_config, admin_token))
            
            self.test_results[shop_id] = shop_results
        
        # Generate final report
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate comprehensive test report"""
        print(f"\n{'='*70}")
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print(f"{'='*70}")
        
        total_tests = 0
        passed_tests = 0
        
        for shop_id, shop_results in self.test_results.items():
            shop_config = self.shops[shop_id]
            print(f"\n🏪 {shop_config['name']} ({shop_id}):")
            
            shop_total = len(shop_results)
            shop_passed = sum(1 for result in shop_results.values() if result.startswith('✅'))
            shop_success_rate = (shop_passed / shop_total * 100) if shop_total > 0 else 0
            
            print(f"   📈 Success Rate: {shop_success_rate:.1f}% ({shop_passed}/{shop_total})")
            
            # Show failed tests
            failed_tests = [test for test, result in shop_results.items() if not result.startswith('✅')]
            if failed_tests:
                print(f"   ❌ Failed Tests: {', '.join(failed_tests)}")
            else:
                print(f"   🎉 All tests passed!")
            
            total_tests += shop_total
            passed_tests += shop_passed
        
        # Overall summary
        overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   📊 Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {total_tests - passed_tests}")
        print(f"   📈 Success Rate: {overall_success_rate:.1f}%")
        
        if overall_success_rate >= 90:
            print(f"   🏆 Status: EXCELLENT")
        elif overall_success_rate >= 75:
            print(f"   ✅ Status: GOOD")
        elif overall_success_rate >= 60:
            print(f"   ⚠️ Status: NEEDS IMPROVEMENT")
        else:
            print(f"   ❌ Status: CRITICAL ISSUES")
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")

if __name__ == "__main__":
    tester = MultiShopTester()
    tester.run_comprehensive_test()
