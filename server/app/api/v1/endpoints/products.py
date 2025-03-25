from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
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
    pages: int = 1
    model: str = "distilbert-base-uncased-finetuned-sst-2-english"

class ProductAnalysisResponse(BaseModel):
    product_reviews: List[Dict[str, Any]]
    sentiment_analysis: Optional[List[Dict[str, Any]]] = []
    aspect_analysis: Optional[List[Dict[str, Any]]] = []
    credibility_scores: Optional[List[Dict[str, Any]]] = []

@router.post("/analyze", response_model=ProductAnalysisResponse)
async def analyze_product(
    request: ProductAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        analyzer = ProductAnalyzer(model_name=request.model)

        product_reviews = await analyzer.extract_reviews(request.url, request.pages)
        if not product_reviews:
            raise HTTPException(status_code=400, detail="No reviews found for analysis.")

        sentiment_analysis = await analyzer.analyze_sentiment(product_reviews)
        aspect_analysis = analyzer.detect_bias(product_reviews)
        credibility_scores = analyzer.assess_credibility(product_reviews)

        processed_reviews = []
        for i, review in enumerate(product_reviews):
            processed_reviews.append({
                "product_review": review.get("product_review", ""),
                "rating": review.get("rating", 0),
                "sentiment": sentiment_analysis[i] if i < len(sentiment_analysis) else None,
                "bias_scores": aspect_analysis[i]["bias_scores"] if i < len(aspect_analysis) else {},
                "credibility_score": credibility_scores[i]["credibility_score"] if i < len(credibility_scores) else 0
            })

        return ProductAnalysisResponse(
            product_reviews=processed_reviews,
            sentiment_analysis=sentiment_analysis,
            aspect_analysis=aspect_analysis,
            credibility_scores=credibility_scores
        )

    except Exception as e:
        print(f"\n=== Error Details ===\nError Type: {type(e).__name__}\nError Message: {str(e)}\n")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze product reviews: {str(e)}"
        )
