"""
Shop Configuration Manager
Handles dynamic shop loading and configuration management
"""
import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ThemeConfig:
    primary_color: str
    secondary_color: str
    logo: str
    favicon: str
    banner: str


@dataclass
class SettingsConfig:
    allow_guest_checkout: bool
    require_email_verification: bool
    enable_reviews: bool
    enable_wishlist: bool
    currency: str
    language: str
    timezone: str


@dataclass
class ContactConfig:
    email: str
    phone: str
    address: str


@dataclass
class ShopConfig:
    id: str
    name: str
    mongodb_url: str
    admin_email: str
    admin_password: str
    frontend_url: str
    domain: str
    description: str
    theme: ThemeConfig
    features: List[str]
    settings: SettingsConfig
    contact: ContactConfig
    social: Dict[str, str]
    
    @classmethod
    def from_dict(cls, shop_id: str, data: dict):
        """Create ShopConfig from dictionary data"""
        return cls(
            id=shop_id,
            name=data['name'],
            mongodb_url=data['mongodb_url'],
            admin_email=data['admin_email'],
            admin_password=data['admin_password'],
            frontend_url=data['frontend_url'],
            domain=data['domain'],
            description=data['description'],
            theme=ThemeConfig(**data['theme']),
            features=data['features'],
            settings=SettingsConfig(**data['settings']),
            contact=ContactConfig(**data['contact']),
            social=data['social']
        )


class ShopManager:
    """Manages shop configurations loaded from JSON file"""
    
    def __init__(self, config_file: str = "shops.json"):
        self.config_file = config_file
        self._shops: Dict[str, ShopConfig] = {}
        self._load_shops()
    
    def _load_shops(self):
        """Load shop configurations from JSON file or environment variable"""
        # Try to load from file first (preferred method)
        config_path = Path(self.config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    shops_data = json.load(f)
                
                self._shops = {}
                for shop_id, shop_data in shops_data.items():
                    self._shops[shop_id] = ShopConfig.from_dict(shop_id, shop_data)
                print(f"✅ Loaded {len(self._shops)} shops from file: {self.config_file}")
                return
                    
            except json.JSONDecodeError as e:
                print(f"⚠️ Invalid JSON in shop configuration file: {e}")
                raise ValueError(f"Invalid JSON in shop configuration file: {e}")
            except Exception as e:
                print(f"⚠️ Error loading shops from file: {e}")
                raise RuntimeError(f"Error loading shop configuration: {e}")
        
        # Fallback to environment variable if file doesn't exist
        shops_config_env = os.getenv('SHOPS_CONFIG')
        if shops_config_env:
            try:
                shops_data = json.loads(shops_config_env)
                self._shops = {}
                for shop_id, shop_data in shops_data.items():
                    self._shops[shop_id] = ShopConfig.from_dict(shop_id, shop_data)
                print(f"✅ Loaded {len(self._shops)} shops from environment variable")
                return
            except json.JSONDecodeError as e:
                print(f"⚠️ Invalid JSON in SHOPS_CONFIG environment variable: {e}")
            except Exception as e:
                print(f"⚠️ Error loading shops from environment: {e}")
        
        # Final fallback: create default shops
        print(f"⚠️ Shop configuration file not found: {self.config_file}")
        print("📝 Creating default shop configuration...")
        self._create_default_shops()
    
    def _create_default_shops(self):
        """Create default shop configurations when no config file exists"""
        default_shops = {
            "tinashop": {
                "name": "Tina Shop",
                "mongodb_url": os.getenv("MONGODB_SHARED_URL", ""),
                "admin_email": "admin@tina.shop",
                "admin_password": "admin123",
                "frontend_url": os.getenv("FRONTEND_URL", "http://localhost:3000"),
                "domain": "tina.shop",
                "description": "Fashion & Lifestyle Store"
            },
            "micocah": {
                "name": "Micocah",
                "mongodb_url": os.getenv("MONGODB_SHARED_URL", ""),
                "admin_email": "admin@micocah.vn", 
                "admin_password": "creator123",
                "frontend_url": os.getenv("FRONTEND_URL", "http://localhost:3000"),
                "domain": "micocah.vn",
                "description": "Technology & Electronics Hub"
            }
        }
        
        self._shops = {}
        for shop_id, shop_data in default_shops.items():
            self._shops[shop_id] = ShopConfig.from_dict(shop_id, shop_data)
        
        print(f"✅ Created {len(self._shops)} default shops")
    
    def get_shop(self, shop_id: str) -> Optional[ShopConfig]:
        """Get shop configuration by ID"""
        return self._shops.get(shop_id)
    
    def get_all_shops(self) -> Dict[str, ShopConfig]:
        """Get all shop configurations"""
        return self._shops.copy()
    
    def get_shop_ids(self) -> List[str]:
        """Get list of all shop IDs"""
        return list(self._shops.keys())
    
    def is_valid_shop(self, shop_id: str) -> bool:
        """Check if shop ID is valid"""
        return shop_id in self._shops
    
    def get_shop_by_domain(self, domain: str) -> Optional[ShopConfig]:
        """Get shop configuration by domain"""
        for shop in self._shops.values():
            if shop.domain == domain:
                return shop
        return None
    
    def reload(self):
        """Reload shop configurations from file"""
        self._load_shops()
    
    def add_shop(self, shop_id: str, shop_data: dict):
        """Add new shop configuration (runtime only, doesn't update file)"""
        self._shops[shop_id] = ShopConfig.from_dict(shop_id, shop_data)
    
    def get_shop_features(self, shop_id: str) -> List[str]:
        """Get enabled features for a shop"""
        shop = self.get_shop(shop_id)
        return shop.features if shop else []
    
    def has_feature(self, shop_id: str, feature: str) -> bool:
        """Check if shop has specific feature enabled"""
        features = self.get_shop_features(shop_id)
        return feature in features


# Global shop manager instance
shop_manager = ShopManager()


def get_shop_manager() -> ShopManager:
    """Get global shop manager instance"""
    return shop_manager


def get_shop_config(shop_id: str) -> Optional[ShopConfig]:
    """Convenience function to get shop config"""
    return shop_manager.get_shop(shop_id)


def get_all_shop_configs() -> Dict[str, ShopConfig]:
    """Convenience function to get all shop configs"""
    return shop_manager.get_all_shops()


def is_valid_shop_id(shop_id: str) -> bool:
    """Convenience function to validate shop ID"""
    return shop_manager.is_valid_shop(shop_id)
