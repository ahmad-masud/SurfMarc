from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel, HttpUrl
from app.services.product_analyzer import ProductAnalyzer
from app.api.deps import get_current_user
from app.schemas.user import User
import traceback
import sys

router = APIRouter()
product_analyzer = ProductAnalyzer()

class ProductAnalysisRequest(BaseModel):
    url: HttpUrl

class ProductAnalysisResponse(BaseModel):
    product: Dict[str, Any]
    sentiment_analysis: Dict[str, Any]
    classification: Dict[str, Any]

@router.post("/analyze", response_model=ProductAnalysisResponse)
async def analyze_product(
    request: ProductAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """Analyze a product from a given URL"""
    try:
        analyzer = ProductAnalyzer()
        result = await analyzer.analyze_product(request.url)
        
        return ProductAnalysisResponse(
            product=result['product'],
            sentiment_analysis=result['sentiment_analysis'],
            classification=result['classification']
        )
    except Exception as e:
        # Get the full traceback and print to terminal
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("\n=== Error Details ===")
        print(f"Error Type: {exc_type.__name__}")
        print(f"Error Message: {str(exc_value)}")
        print("\nTraceback:")
        traceback.print_exc()
        print("===================\n")
        
        # Return a simple error message to the client
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze product: {str(e)}"
        ) 