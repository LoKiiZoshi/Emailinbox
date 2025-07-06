from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import django
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token

# Initialize Django
django.setup()

from .models import Product, Category, Order, User

router = APIRouter()
security = HTTPBearer()

# Pydantic models
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool

    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    price: float
    stock: int
    is_active: bool
    category_name: str

    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str
    description: str
    category_id: int
    price: float
    stock: int

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = Token.objects.get(key=credentials.credentials)
        return token.user
    except Token.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# FastAPI Routes
@router.get("/")
async def fastapi_root():
    return {"message": "FastAPI routes are working!", "version": "1.0.0"}

@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)

@router.get("/products", response_model=List[ProductResponse])
async def get_products(skip: int = 0, limit: int = 100):
    products = Product.objects.filter(is_active=True)[skip:skip + limit]
    return [
        ProductResponse(
            id=p.id,
            name=p.name,
            slug=p.slug,
            description=p.description,
            price=float(p.price),
            stock=p.stock,
            is_active=p.is_active,
            category_name=p.category.name
        ) for p in products
    ]

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    try:
        product = Product.objects.get(id=product_id, is_active=True)
        return ProductResponse(
            id=product.id,
            name=product.name,
            slug=product.slug,
            description=product.description,
            price=float(product.price),
            stock=product.stock,
            is_active=product.is_active,
            category_name=product.category.name
        )
    except Product.DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")

@router.post("/products", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    try:
        category = Category.objects.get(id=product.category_id)
        new_product = Product.objects.create(
            name=product.name,
            slug=product.name.lower().replace(' ', '-'),
            description=product.description,
            category=category,
            price=product.price,
            stock=product.stock
        )
        return ProductResponse(
            id=new_product.id,
            name=new_product.name,
            slug=new_product.slug,
            description=new_product.description,
            price=float(new_product.price),
            stock=new_product.stock,
            is_active=new_product.is_active,
            category_name=new_product.category.name
        )
    except Category.DoesNotExist:
        raise HTTPException(status_code=400, detail="Category not found")

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories():
    categories = Category.objects.filter(is_active=True)
    return [CategoryResponse.from_orm(cat) for cat in categories]

@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    new_category = Category.objects.create(
        name=category.name,
        slug=category.name.lower().replace(' ', '-'),
        description=category.description
    )
    return CategoryResponse.from_orm(new_category)

@router.get("/stats")
async def get_stats(current_user: User = Depends(get_current_user)):
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return {
        "total_users": User.objects.count(),
        "total_products": Product.objects.count(),
        "total_categories": Category.objects.count(),
        "total_orders": Order.objects.count(),
        "active_products": Product.objects.filter(is_active=True).count(),
    }
