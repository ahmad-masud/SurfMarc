from typing import List, Dict, Any
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from transformers import pipeline
from collections import Counter
import traceback
import re
import torch

class ProductAnalyzer:
    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        try:
            device = 0 if torch.cuda.is_available() else -1

            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model=model_name,
                device=device
            )
            self.bias_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=device
            )
        except Exception as e:
            raise Exception(f"Failed to initialize ProductAnalyzer: {str(e)}\n{traceback.format_exc()}")

    async def extract_reviews(self, url: str, pages: int = 1) -> List[Dict[str, Any]]:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                await page.goto(url, timeout=15000)
                await page.wait_for_load_state("domcontentloaded")

                all_reviews = []
                for _ in range(pages):
                    # Scrape reviews on current page
                    reviews = await page.evaluate("""() => {
                        return Array.from(document.querySelectorAll('.review')).map(review => ({
                            text: review.querySelector('.review-text, .a-size-base.review-text-content')?.innerText.trim() || '',
                            rating: review.querySelector('.review-rating')?.innerText.trim().charAt(0) || '0'
                        })).filter(review => review.text.length > 10);
                    }""")
                    all_reviews.extend(reviews)

                    # Try to go to the next page
                    next_button = await page.query_selector("li.a-last a")
                    if next_button:
                        await next_button.click()
                        await page.wait_for_timeout(1500)  # slight wait for content to load
                    else:
                        break

                await browser.close()

                return [
                    {"product_review": r["text"], "rating": int(r["rating"])}
                    for r in all_reviews if r["text"]
                ]
        except Exception as e:
            print(f"Error extracting reviews: {str(e)}")
            return []

    async def analyze_sentiment(self, reviews: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment of product reviews, ensuring text truncation and correct output format"""
        try:
            sentiments = []
            for review in reviews:
                if not isinstance(review, str):  # Ensure review is a string
                    continue
                
                # Truncate long reviews to prevent exceeding model limits
                truncated_review = review[:450]  

                result = self.sentiment_analyzer(truncated_review)
                sentiments.append({
                    "review": review, 
                    "sentiment": result[0]  # Ensure this is properly formatted
                })
            
            return sentiments  # Must return a list, not a dict
        except Exception as e:
            raise Exception(f"Failed to analyze sentiment: {str(e)}\n{traceback.format_exc()}")

    def detect_bias(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect bias in reviews using zero-shot classification."""
        bias_labels = ["exaggeration", "subjectivity", "overly emotional", "neutral"]
        results = []

        for review_data in reviews:
            review = review_data.get("product_review", "")

            if not isinstance(review, str) or not review.strip():  # Ensure it's a non-empty string
                continue
            
            classification = self.bias_classifier(review, bias_labels)
            
            results.append({
                "review": review,
                "bias_scores": dict(zip(classification["labels"], classification["scores"]))
            })
        
        return results
    
    def assess_credibility(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assess credibility of reviews based on various linguistic factors."""
        results = []
        review_texts = [r.get("product_review", "").strip().lower() for r in reviews]

        # Count duplicate reviews
        review_counts = Counter(review_texts)

        for review_data in reviews:
            review = review_data.get("product_review", "").strip()
            
            if not isinstance(review, str) or not review:
                continue
            
            credibility_score = 100  # Start with a perfect score

            # 1️⃣ Short reviews (less than 20 words) are suspicious
            if len(review.split()) < 20:
                credibility_score -= 30
            
            # 2️⃣ Fake-sounding words (exaggeration, marketing words)
            if re.search(r'\b(BUY|SCAM|FAKE|BEST|AMAZING|PERFECT|MUST-HAVE|LIFE-CHANGING|WASTE OF MONEY|DO NOT BUY|GARBAGE)\b', review, re.IGNORECASE):
                credibility_score -= 25

            # 3️⃣ Excessive punctuation or capitalization
            if re.search(r'!{3,}|\?{3,}|\b[A-Z]{5,}\b', review):
                credibility_score -= 20
            
            # 4️⃣ Repetitive words (e.g., "best best best")
            words = review.lower().split()
            most_common_word, count = Counter(words).most_common(1)[0]
            if count > 3:
                credibility_score -= 20  # Overuse of a word looks fake

            # 5️⃣ Duplicate reviews are penalized
            if review_counts[review.lower()] > 1:
                credibility_score -= 40  # Identical reviews = likely spam
            
            credibility_score = max(0, credibility_score)  # Ensure score isn't negative

            results.append({
                "review": review,
                "credibility_score": credibility_score
            })
        
        return results
