# 📚 API Reference - API Nhan88ng

**Complete API documentation for the Nhan88ng e-commerce platform**

**Base URL**: `http://localhost:8000`  
**API Version**: v1  
**Authentication**: JWT Bearer Token  

---

## 🔐 **Authentication**

All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### **Get Authentication Token**
```bash
# Login to get token
curl -X POST "/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@tinashop.com", "password": "password"}'
```

---

## 📊 **Response Format**

### **Success Response**
```json
{
  "data": { ... },
  "message": "Success message",
  "status": "success"
}
```

### **Error Response**
```json
{
  "detail": "Error description",
  "status": "error",
  "code": 400
}
```

### **Validation Error Response**
```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "Field is required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🏥 **Health & Status**

### **GET /health**
Check application health status.

**Response:**
```json
{
  "status": "healthy"
}
```

**Example:**
```bash
curl "http://localhost:8000/health"
```

---

## 🔐 **Authentication Endpoints**

### **POST /api/v1/auth/register**
Register a new user account.

**Request Body:**
```json
{
  "email": "user@tinashop.com",
  "password": "password123",
  "full_name": "User Name",
  "shop": "tinashop",
  "role": "customer"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "60f7b3b3b3b3b3b3b3b3b3b3",
    "email": "user@tinashop.com",
    "full_name": "User Name",
    "shop": "tinashop",
    "role": "customer",
    "permissions": ["product:read", "order:read", "order:write"],
    "is_active": true,
    "is_verified": false,
    "created_at": "2025-08-10T08:00:00Z"
  }
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@tinashop.com",
    "password": "securepass123",
    "full_name": "New User",
    "shop": "tinashop"
  }'
```

### **POST /api/v1/auth/login**
Login with email and password.

**Request Body:**
```json
{
  "email": "user@tinashop.com",
  "password": "password123"
}
```

**Response:** Same as register response.

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@tinashop.com",
    "password": "admin123"
  }'
```

### **POST /api/v1/auth/refresh**
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### **POST /api/v1/auth/logout**
Logout and invalidate tokens.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

---

## 👥 **User Management**

### **GET /api/v1/users/me**
Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "60f7b3b3b3b3b3b3b3b3b3b3",
  "email": "user@tinashop.com",
  "full_name": "User Name",
  "shop": "tinashop",
  "role": "customer",
  "permissions": ["product:read", "order:read"],
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-08-10T08:00:00Z"
}
```

**Example:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/users/me"
```

### **PUT /api/v1/users/me**
Update current user profile.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "full_name": "Updated Name",
  "phone": "+1234567890"
}
```

**Response:** Updated user object.

---

## 📦 **Product Management**

### **GET /api/v1/products/**
List products with filtering and pagination.

**Query Parameters:**
- `shop` (required): Shop name (tinashop, micocah, shared)
- `page` (optional): Page number (default: 1)
- `size` (optional): Items per page (default: 20, max: 100)
- `search` (optional): Search in name and description
- `category` (optional): Filter by category slug
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter
- `status` (optional): Product status (active, draft, discontinued)
- `is_featured` (optional): Featured products only (true/false)
- `sort` (optional): Sort by (name, price, created_at, updated_at)
- `order` (optional): Sort order (asc, desc)

**Response:**
```json
{
  "products": [
    {
      "id": "60f7b3b3b3b3b3b3b3b3b3b3",
      "name": "iPhone 15 Pro",
      "description": "Latest iPhone with advanced features",
      "short_description": "Premium smartphone",
      "slug": "iphone-15-pro",
      "sku": "IPHONE-15-PRO-001",
      "price": 999.99,
      "compare_price": 1199.99,
      "cost_price": 800.00,
      "category_ids": ["60f7b3b3b3b3b3b3b3b3b3b4"],
      "categories": [
        {
          "id": "60f7b3b3b3b3b3b3b3b3b3b4",
          "name": "Electronics",
          "slug": "electronics"
        }
      ],
      "tags": ["smartphone", "apple", "ios"],
      "images": [
        "/static/images/tinashop/products/iphone-15-pro.jpg"
      ],
      "variants": [],
      "stock_quantity": 10,
      "track_inventory": true,
      "allow_backorder": false,
      "weight": 0.2,
      "dimensions": {
        "length": 14.76,
        "width": 7.15,
        "height": 0.83
      },
      "status": "active",
      "is_featured": true,
      "meta_title": "iPhone 15 Pro - Latest Apple Smartphone",
      "meta_description": "Get the latest iPhone 15 Pro with advanced features...",
      "shop": "tinashop",
      "created_by": "admin_user_id",
      "created_at": "2025-08-10T08:00:00Z",
      "updated_at": "2025-08-10T08:00:00Z",
      "view_count": 150,
      "sales_count": 25
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1,
  "has_next": false,
  "has_prev": false
}
```

**Example:**
```bash
# List all products for tinashop
curl "http://localhost:8000/api/v1/products/?shop=tinashop"

# Search products
curl "http://localhost:8000/api/v1/products/?shop=tinashop&search=iphone"

# Filter by category and price
curl "http://localhost:8000/api/v1/products/?shop=tinashop&category=electronics&min_price=500&max_price=1500"

# Paginated results
curl "http://localhost:8000/api/v1/products/?shop=tinashop&page=2&size=10"
```

### **GET /api/v1/products/{product_id}**
Get detailed product information.

**Path Parameters:**
- `product_id`: Product ID

**Response:**
```json
{
  "id": "60f7b3b3b3b3b3b3b3b3b3b3",
  "name": "iPhone 15 Pro",
  "description": "Detailed product description...",
  "categories": [...],
  "images": [...],
  "variants": [...],
  // ... full product details
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/products/60f7b3b3b3b3b3b3b3b3b3b3"
```

### **POST /api/v1/products/**
Create a new product (Admin only).

**Headers:** `Authorization: Bearer <admin_token>`

**Request Body:**
```json
{
  "name": "New Product",
  "description": "Product description",
  "short_description": "Short description",
  "sku": "NEW-PROD-001",
  "price": 299.99,
  "compare_price": 399.99,
  "cost_price": 200.00,
  "category_ids": ["60f7b3b3b3b3b3b3b3b3b3b4"],
  "tags": ["new", "product"],
  "stock_quantity": 50,
  "track_inventory": true,
  "allow_backorder": false,
  "weight": 1.5,
  "dimensions": {
    "length": 10.0,
    "width": 5.0,
    "height": 2.0
  },
  "status": "active",
  "is_featured": false,
  "meta_title": "New Product - Buy Now",
  "meta_description": "Amazing new product available now",
  "shop": "tinashop"
}
```

**Response:** Created product object with ID.

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "description": "A test product",
    "sku": "TEST-001",
    "price": 99.99,
    "shop": "tinashop",
    "category_ids": ["60f7b3b3b3b3b3b3b3b3b3b4"]
  }'
```

### **PUT /api/v1/products/{product_id}**
Update an existing product (Admin only).

**Headers:** `Authorization: Bearer <admin_token>`
**Path Parameters:** `product_id`

**Request Body:** Partial product data to update.

**Example:**
```bash
curl -X PUT "http://localhost:8000/api/v1/products/60f7b3b3b3b3b3b3b3b3b3b3" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Product Name",
    "price": 199.99
  }'
```

### **DELETE /api/v1/products/{product_id}**
Delete a product (Admin only).

**Headers:** `Authorization: Bearer <admin_token>`
**Path Parameters:** `product_id`

**Response:**
```json
{
  "message": "Product deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/products/60f7b3b3b3b3b3b3b3b3b3b3" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## 🏷️ **Category Management**

### **GET /api/v1/products/categories/**
List categories for a shop.

**Query Parameters:**
- `shop` (required): Shop name
- `parent_id` (optional): Filter by parent category
- `is_active` (optional): Filter by active status
- `include_children` (optional): Include child categories

**Response:**
```json
[
  {
    "id": "60f7b3b3b3b3b3b3b3b3b3b4",
    "name": "Electronics",
    "description": "Electronic devices and accessories",
    "slug": "electronics",
    "parent_id": null,
    "is_active": true,
    "shop": "tinashop",
    "product_count": 25,
    "children": [
      {
        "id": "60f7b3b3b3b3b3b3b3b3b3b5",
        "name": "Smartphones",
        "slug": "smartphones",
        "parent_id": "60f7b3b3b3b3b3b3b3b3b3b4"
      }
    ],
    "created_at": "2025-08-10T08:00:00Z",
    "updated_at": "2025-08-10T08:00:00Z"
  }
]
```

**Example:**
```bash
# List all categories
curl "http://localhost:8000/api/v1/products/categories/?shop=tinashop"

# List with children
curl "http://localhost:8000/api/v1/products/categories/?shop=tinashop&include_children=true"
```

### **POST /api/v1/products/categories/**
Create a new category (Admin only).

**Headers:** `Authorization: Bearer <admin_token>`

**Request Body:**
```json
{
  "name": "New Category",
  "description": "Category description",
  "slug": "new-category",
  "parent_id": null,
  "is_active": true,
  "shop": "tinashop"
}
```

**Response:** Created category object.

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/products/categories/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Accessories",
    "description": "Product accessories",
    "shop": "tinashop"
  }'
```

### **PUT /api/v1/products/categories/{category_id}**
Update a category (Admin only).

**Example:**
```bash
curl -X PUT "http://localhost:8000/api/v1/products/categories/60f7b3b3b3b3b3b3b3b3b3b4" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Electronics",
    "description": "Updated description"
  }'
```

### **DELETE /api/v1/products/categories/{category_id}**
Delete a category (Admin only).

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/products/categories/60f7b3b3b3b3b3b3b3b3b3b4" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## 🖼️ **Image Upload**

### **GET /api/v1/upload/upload/health**
Check image service health.

**Response:**
```json
{
  "status": "healthy",
  "shops": {
    "tinashop": true,
    "micocah": true,
    "shared": true
  },
  "directories_created": true,
  "service_available": true
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/upload/upload/health"
```

### **POST /api/v1/upload/upload/{shop}/{category}/**
Upload an image file (Admin only).

**Headers:** `Authorization: Bearer <admin_token>`

**Path Parameters:**
- `shop`: Shop name (tinashop, micocah, shared)
- `category`: Image category (products, categories, users)

**Request Body:** Form data with file
- `file`: Image file (JPG, PNG, GIF, WebP)
- `create_thumbnails` (optional): Boolean (default: true)

**Response:**
```json
{
  "success": true,
  "message": "Image uploaded successfully to tinashop/products",
  "data": {
    "shop": "tinashop",
    "category": "products",
    "filename": "uuid-generated-filename.jpg",
    "original_url": "/static/images/tinashop/products/uuid-filename.jpg",
    "file_size": 1024576,
    "content_type": "image/jpeg",
    "thumbnails": {
      "small": "/static/images/tinashop/products/thumbnails/small_uuid-filename.jpg",
      "medium": "/static/images/tinashop/products/thumbnails/medium_uuid-filename.jpg"
    }
  }
}
```

**Example:**
```bash
# Upload product image
curl -X POST "http://localhost:8000/api/v1/upload/upload/tinashop/products/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@product_image.jpg"

# Upload category image
curl -X POST "http://localhost:8000/api/v1/upload/upload/tinashop/categories/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@category_image.png"

# Upload without thumbnails
curl -X POST "http://localhost:8000/api/v1/upload/upload/tinashop/products/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@image.jpg" \
  -F "create_thumbnails=false"
```

### **GET /api/v1/upload/list/{shop}/{category}/**
List uploaded images (Admin only).

**Headers:** `Authorization: Bearer <admin_token>`

**Response:**
```json
{
  "images": [
    {
      "filename": "uuid-filename.jpg",
      "url": "/static/images/tinashop/products/uuid-filename.jpg",
      "size": 1024576,
      "uploaded_at": "2025-08-10T08:00:00Z"
    }
  ],
  "total": 1,
  "shop": "tinashop",
  "category": "products"
}
```

**Example:**
```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost:8000/api/v1/upload/list/tinashop/products/"
```

### **DELETE /api/v1/upload/delete/{shop}/{category}/{filename}**
Delete an uploaded image (Admin only).

**Headers:** `Authorization: Bearer <admin_token>`

**Example:**
```bash
curl -X DELETE \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost:8000/api/v1/upload/delete/tinashop/products/uuid-filename.jpg"
```

### **GET /static/images/{shop}/{category}/{filename}**
Access uploaded images directly.

**Path Parameters:**
- `shop`: Shop name
- `category`: Image category
- `filename`: Image filename

**Response:** Image file with appropriate Content-Type header.

**Example:**
```bash
# Access image directly
curl "http://localhost:8000/static/images/tinashop/products/uuid-filename.jpg"

# Check image headers
curl -I "http://localhost:8000/static/images/tinashop/products/uuid-filename.jpg"
```

---

## 📊 **Search & Filtering**

### **GET /api/v1/products/search**
Advanced product search.

**Query Parameters:**
- `q` (required): Search query
- `shop` (required): Shop name
- `category`: Category filter
- `min_price`, `max_price`: Price range
- `in_stock`: Only in-stock products
- `featured`: Only featured products
- `sort`: Sort field
- `order`: Sort order

**Example:**
```bash
# Search for "phone" in electronics
curl "http://localhost:8000/api/v1/products/search?q=phone&shop=tinashop&category=electronics"

# Search with price range
curl "http://localhost:8000/api/v1/products/search?q=laptop&shop=tinashop&min_price=500&max_price=2000"
```

---

## 🔒 **Permission Levels**

### **Customer Permissions**
- `product:read` - View products and categories
- `order:read` - View own orders
- `order:write` - Create and update own orders

### **Admin Permissions**
- All customer permissions plus:
- `user:read` - View users
- `user:write` - Create and update users
- `product:write` - Create and update products
- `product:delete` - Delete products
- `order:delete` - Delete orders
- `admin:panel` - Access admin features

### **Example Permission Check**
```bash
# This will fail with customer token
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer $CUSTOMER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Product"}'

# Response: 403 Forbidden
# {"detail": "Insufficient role. Required: UserRole.ADMIN or higher"}
```

---

## 🏪 **Multi-Shop Support**

### **Shop Isolation**
Data is completely isolated between shops:
- `tinashop` - Primary shop
- `micocah` - Secondary shop  
- `shared` - Shared resources

### **Shop-Specific Endpoints**
All product and category endpoints require `shop` parameter:

```bash
# TinaShop products
curl "http://localhost:8000/api/v1/products/?shop=tinashop"

# Micocah products  
curl "http://localhost:8000/api/v1/products/?shop=micocah"

# Shared products
curl "http://localhost:8000/api/v1/products/?shop=shared"
```

### **Image Storage Isolation**
Images are stored in shop-specific directories:
- `/static/images/tinashop/products/`
- `/static/images/micocah/products/`
- `/static/images/shared/products/`

---

## ⚡ **Rate Limiting**

### **Default Limits**
- **Authentication**: 5 requests per minute per IP
- **Product Creation**: 10 requests per minute per user
- **Image Upload**: 20 requests per hour per user
- **General API**: 1000 requests per hour per user

### **Rate Limit Headers**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1628766000
```

---

## 🚨 **Error Codes**

| Code | Description | Example |
|------|-------------|---------|
| **200** | Success | Request completed successfully |
| **201** | Created | Resource created successfully |
| **400** | Bad Request | Invalid request data |
| **401** | Unauthorized | Invalid or missing authentication |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource does not exist |
| **422** | Validation Error | Request data validation failed |
| **429** | Rate Limited | Too many requests |
| **500** | Server Error | Internal server error |

### **Common Error Examples**

#### **Validation Error (422)**
```json
{
  "detail": [
    {
      "loc": ["body", "price"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt",
      "ctx": {"limit_value": 0}
    }
  ]
}
```

#### **Permission Error (403)**
```json
{
  "detail": "Insufficient role. Required: UserRole.ADMIN or higher"
}
```

#### **Not Found Error (404)**
```json
{
  "detail": "Product not found"
}
```

---

## 🔧 **API Versioning**

### **Current Version: v1**
- Base path: `/api/v1/`
- Stable and production-ready
- Backward compatibility maintained

### **Version Headers**
```
API-Version: v1
Accept: application/json
Content-Type: application/json
```

---

## 📈 **Performance Guidelines**

### **Best Practices**
1. **Pagination**: Use `page` and `size` parameters for large datasets
2. **Filtering**: Apply filters to reduce response size
3. **Caching**: Utilize browser caching for static content
4. **Compression**: Enable gzip compression for responses

### **Response Time Expectations**
- **Health checks**: < 10ms
- **Authentication**: < 50ms
- **Product listing**: < 100ms
- **Product creation**: < 200ms
- **Image upload**: < 1s

---

## 🧪 **Testing Your Integration**

### **Postman Collection**
Import the API collection for testing:
```json
{
  "info": {
    "name": "API Nhan88ng",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
```

### **Sample Integration Test**
```bash
#!/bin/bash
# Complete API integration test

BASE_URL="http://localhost:8000"

# 1. Health check
echo "Testing health endpoint..."
curl -f "$BASE_URL/health" || exit 1

# 2. Register user
echo "Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User",
    "shop": "tinashop"
  }')

TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.access_token')

# 3. Get products
echo "Getting products..."
curl -f -H "Authorization: Bearer $TOKEN" \
  "$BASE_URL/api/v1/products/?shop=tinashop" || exit 1

# 4. Get categories
echo "Getting categories..."
curl -f -H "Authorization: Bearer $TOKEN" \
  "$BASE_URL/api/v1/products/categories/?shop=tinashop" || exit 1

echo "✅ All tests passed!"
```

---

## 🔗 **SDK & Libraries**

### **JavaScript/TypeScript**
```typescript
// API client example
class NhanAPI {
  constructor(baseURL: string, token?: string) {
    this.baseURL = baseURL;
    this.token = token;
  }

  async getProducts(shop: string, params?: any) {
    const url = new URL(`${this.baseURL}/api/v1/products/`);
    url.searchParams.append('shop', shop);
    
    if (params) {
      Object.keys(params).forEach(key => 
        url.searchParams.append(key, params[key])
      );
    }

    const response = await fetch(url.toString(), {
      headers: this.token ? {
        'Authorization': `Bearer ${this.token}`
      } : {}
    });

    return response.json();
  }
}

// Usage
const api = new NhanAPI('http://localhost:8000', 'your-token');
const products = await api.getProducts('tinashop', { limit: 10 });
```

### **Python**
```python
import requests

class NhanAPI:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })

    def get_products(self, shop, **params):
        url = f"{self.base_url}/api/v1/products/"
        params['shop'] = shop
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def create_product(self, product_data):
        url = f"{self.base_url}/api/v1/products/"
        response = self.session.post(url, json=product_data)
        response.raise_for_status()
        return response.json()

# Usage
api = NhanAPI('http://localhost:8000', 'your-token')
products = api.get_products('tinashop', limit=10)
```

---

## 📞 **Support & Resources**

### **Documentation**
- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

### **Community & Support**
- **GitHub Issues**: Report bugs and feature requests
- **Email Support**: api-support@nhan88ng.com
- **Discord**: Join our developer community

### **Useful Links**
- **Changelog**: Track API updates and changes
- **Status Page**: Monitor API uptime and performance
- **Developer Blog**: Learn about new features and best practices

---

**📚 This completes the comprehensive API reference for Nhan88ng e-commerce platform. For additional examples and advanced usage, visit the interactive documentation at `/docs`.**
