from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from src.recommendation.recommender import Recommender
import models
from database import engine, get_db

recommender = Recommender()

# Create database tables automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ecommerce Backend API")

# --- Pydantic Schemas ---
class ReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = None

class ProductCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    brand: Optional[str] = None
    category_id: int


# --- API Endpoints ---

# 1. Root Welcome Endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to Ecommerce Backend API"}

# 2. Get All Products (Database)
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products

# 3. Get Single Product Detail by ID
@app.get("/products/{id}")
def get_product(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

# 4. Create Product (Database)
@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = models.Product(
        title=product.title,
        description=product.description,
        price=product.price,
        brand=product.brand,
        category_id=product.category_id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# 5. Get Product Reviews by Product ID
@app.get("/products/{id}/reviews")
def get_product_reviews(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product.reviews

# 6. Get Categories (Database)
@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    return categories

@app.get("/recommendations")
def get_recommendations_by_title(title: str):
    recommendations = recommender.recommend(title)
    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product title not found in recommendations dataset"
        )
    return recommendations

@app.get("/products/{id}/recommendations")
def get_recommendations(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    recommendations = recommender.recommend(product.title)
    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recommendations found for this product"
        )
    return recommendations