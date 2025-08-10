# 🔐 Admin Users Information

## Multi-Shop Admin Users

Hệ thống API Nhan88ng sử dụng **2 admin users** riêng biệt cho từng shop:

### 1. TinaShop Admin
```
Email: admin@tina.shop
Password: [Set during deployment]
Role: admin
Shop: tinashop
Permissions: full access to tinashop products/categories/orders
```

### 2. Micocah Admin  
```
Email: admin@micocah.vn
Password: [Set during deployment]
Role: admin
Shop: micocah
Permissions: full access to micocah products/categories/orders
```

## Authentication Usage

### Login TinaShop Admin
```json
POST /api/v1/auth/login
{
    "email": "admin@tina.shop",
    "password": "your_admin_password"
}
```

### Login Micocah Admin
```json
POST /api/v1/auth/login
{
    "email": "admin@micocah.vn", 
    "password": "your_admin_password"
}
```

## Shop Isolation

- **TinaShop Admin** chỉ có thể quản lý data của TinaShop
- **Micocah Admin** chỉ có thể quản lý data của Micocah
- Data giữa 2 shops được cách ly hoàn toàn
- Mỗi admin không thể truy cập data của shop khác

## Test Files Usage

Các file test sử dụng admin users:
- `comprehensive_test.py` - Sử dụng admin@tinashop.com
- Các API calls cần authentication sẽ dùng JWT token từ login

## Security Notes

- **Production passwords**: Must be set during deployment with strong passwords
- **Development passwords**: Contact team for current development credentials  
- JWT tokens have expiration time
- Role-based access control (RBAC) implemented
- All passwords encrypted with bcrypt

## Deployment Setup

### Creating Admin Users
```bash
# Use the registration endpoint with admin role
curl -X POST "http://your-domain/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@tina.shop",
    "password": "your_secure_password",
    "full_name": "TinaShop Admin",
    "shop": "tinashop",
    "role": "admin"
  }'
```

## Current Status

✅ **TinaShop:** Hoạt động hoàn hảo với 17 products
⚠️ **Micocah:** Products đã tạo nhưng API có lỗi serialization

## Database

Admins được lưu trong MongoDB collection `users` với:
- Encrypted passwords (bcrypt)
- Role assignment
- Shop assignment  
- Permissions array
