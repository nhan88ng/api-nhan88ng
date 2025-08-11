# 🏪 Shop Configuration Guide

This guide explains how to configure shops for the Nhan88ng API multi-tenant e-commerce platform.

## 📋 Setup Instructions

### 1. Copy Configuration Files

```bash
# Copy environment template
cp .env.example .env

# Copy shops configuration template  
cp shops.json.example shops.json
```

### 2. Configure Environment Variables

Edit `.env` file with your actual values:

```bash
# Shop Configuration
SHOPS_CONFIG_FILE=shops.json

# MongoDB Atlas Configuration
MONGODB_SHARED_URL=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@cluster.mongodb.net/shared_db

# JWT Configuration
SECRET_KEY=your-super-secret-key-generate-a-strong-one

# Other configurations...
```

### 3. Configure Shops

Edit `shops.json` file to define your shops:

```json
{
  "your_shop_id": {
    "name": "Your Shop Name",
    "mongodb_url": "mongodb+srv://...",
    "admin_email": "admin@yourshop.com",
    "admin_password": "secure_password",
    "frontend_url": "http://localhost:3001",
    "domain": "yourshop.com",
    "description": "Your shop description",
    "theme": {
      "primary_color": "#007bff",
      "secondary_color": "#6c757d",
      "logo": "/static/images/yourshop/logo.png"
    },
    "features": ["products", "orders", "inventory"],
    "settings": {
      "currency": "USD",
      "language": "en",
      "allow_guest_checkout": true
    }
  }
}
```

## 🎨 Shop Configuration Options

### Required Fields
- `name`: Shop display name
- `mongodb_url`: MongoDB connection string for shop database
- `admin_email`: Shop admin email
- `admin_password`: Shop admin password
- `frontend_url`: Shop frontend URL
- `domain`: Shop domain name

### Theme Configuration
- `primary_color`: Main brand color
- `secondary_color`: Secondary color
- `logo`: Path to shop logo
- `favicon`: Path to favicon
- `banner`: Path to banner image

### Available Features
- `products`: Product management
- `orders`: Order processing
- `inventory`: Inventory tracking
- `categories`: Category management
- `customers`: Customer management
- `reviews`: Product reviews
- `wishlist`: Customer wishlist
- `brands`: Brand management
- `specifications`: Product specifications

### Settings Options
- `allow_guest_checkout`: Allow checkout without registration
- `require_email_verification`: Require email verification
- `enable_reviews`: Enable product reviews
- `enable_wishlist`: Enable customer wishlist
- `currency`: Shop currency (USD, EUR, VND, etc.)
- `language`: Shop language (en, vi, fr, etc.)
- `timezone`: Shop timezone

## 🔒 Security Notes

- `shops.json` contains sensitive information and is excluded from Git
- Always use strong passwords for admin accounts
- Use environment-specific MongoDB databases
- Keep production credentials secure

## 🚀 Adding New Shops

1. Add new shop configuration to `shops.json`
2. Create MongoDB database for the shop
3. Restart the API server
4. The shop will be automatically available

## 📡 API Endpoints

```bash
# Get all shops
GET /api/v1/shops/

# Get specific shop info
GET /api/v1/shops/{shop_id}

# Get shop features
GET /api/v1/shops/{shop_id}/features
```

## 🛠️ Development vs Production

### Development
- Use localhost URLs for frontend_url
- Use development MongoDB databases
- Keep DEBUG=True in .env

### Production
- Use actual domain URLs
- Use production MongoDB databases  
- Set DEBUG=False in .env
- Use strong SECRET_KEY
- Configure SMTP for emails

## 📞 Support

For configuration help, check the main documentation or create an issue in the repository.
