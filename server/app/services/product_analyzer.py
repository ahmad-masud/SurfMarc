from typing import List, Dict, Any
import json
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from transformers import pipeline
import faiss
import numpy as np
from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import asyncio
import aiohttp
from slugify import slugify
import traceback

class ProductAnalyzer:
    def __init__(self):
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                revision="af0f99b",
                force_download=True
            )
            self.zero_shot_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                revision="c626438",
                force_download=True
            )
        except Exception as e:
            raise Exception(f"Failed to initialize ProductAnalyzer: {str(e)}\n{traceback.format_exc()}")

    async def scrape_product(self, url: str) -> Dict[str, Any]:
        """Scrape product information using Playwright"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                )
                page = await context.new_page()
                
                try:
                    # Set a shorter timeout for navigation
                    await page.goto(url, timeout=10000)
                    
                    # Wait for the page to be interactive
                    await page.wait_for_load_state("domcontentloaded", timeout=10000)
                    
                    # Extract product information with a more robust selector strategy
                    product_data = await page.evaluate("""() => {
                        const getText = (selector) => {
                            const element = document.querySelector(selector);
                            return element ? element.textContent.trim() : '';
                        };
                        
                        const getSpecs = () => {
                            const specs = [];
                            // Look for common specification patterns
                            const specElements = document.querySelectorAll('table, dl, .specifications, .product-specs');
                            specElements.forEach(element => {
                                const rows = element.querySelectorAll('tr, dt, .spec-row');
                                rows.forEach(row => {
                                    const name = row.querySelector('th, dt, .spec-name')?.textContent.trim();
                                    const value = row.querySelector('td, dd, .spec-value')?.textContent.trim();
                                    if (name && value) {
                                        specs.push({ name, value });
                                    }
                                });
                            });
                            return specs;
                        };
                        
                        return {
                            title: document.title,
                            price: getText('[data-price], .price, .product-price, [itemprop="price"]'),
                            description: getText('[data-description], .description, .product-description, [itemprop="description"]'),
                            specifications: getSpecs()
                        };
                    }""")
                    
                    return product_data
                    
                except Exception as e:
                    print(f"Error during page scraping: {str(e)}")
                    # Return a basic product data structure if scraping fails
                    return {
                        'title': 'Product Title Not Found',
                        'price': 'Price Not Found',
                        'description': 'Description Not Found',
                        'specifications': []
                    }
                finally:
                    await context.close()
                    await browser.close()
                    
        except Exception as e:
            raise Exception(f"Failed to scrape product: {str(e)}\n{traceback.format_exc()}")

    async def analyze_sentiment(self, reviews: List[str]) -> Dict[str, Any]:
        """Analyze sentiment of product reviews"""
        try:
            sentiments = []
            for review in reviews:
                result = self.sentiment_analyzer(review)
                sentiments.append(result[0])
            
            # Calculate overall sentiment
            positive_count = sum(1 for s in sentiments if s['label'] == 'POSITIVE')
            negative_count = sum(1 for s in sentiments if s['label'] == 'NEGATIVE')
            
            return {
                'overall_sentiment': 'POSITIVE' if positive_count > negative_count else 'NEGATIVE',
                'positive_count': positive_count,
                'negative_count': negative_count,
                'sentiment_details': sentiments
            }
        except Exception as e:
            raise Exception(f"Failed to analyze sentiment: {str(e)}\n{traceback.format_exc()}")

    async def classify_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify product using zero-shot classification"""
        try:
            product_text = f"{product_data['title']} {product_data['description']}"
            categories = [
                "electronics", "clothing", "home", "beauty", "sports",
                "books", "toys", "food", "automotive", "health"
            ]
            
            result = self.zero_shot_classifier(product_text, categories)
            return {
                'categories': dict(zip(result['labels'], result['scores']))
            }
        except Exception as e:
            raise Exception(f"Failed to classify product: {str(e)}\n{traceback.format_exc()}")

    async def analyze_product(self, url: str) -> Dict[str, Any]:
        """Main method to analyze a product"""
        try:
            # Scrape product data
            product_data = await self.scrape_product(url)
            
            # Analyze sentiment (assuming we have reviews)
            sentiment_analysis = await self.analyze_sentiment([])  # Add actual reviews here
            
            # Classify product
            classification = await self.classify_product(product_data)
            
            return {
                'product': product_data,
                'sentiment_analysis': sentiment_analysis,
                'classification': classification
            }
        except Exception as e:
            raise Exception(f"Failed to analyze product: {str(e)}\n{traceback.format_exc()}")

class ProductSpider(Spider):
    name = 'product_spider'
    
    def __init__(self, url=None, *args, **kwargs):
        super(ProductSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []
        self.product_data = {}

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract product data (customize based on target website)
        self.product_data = {
            'title': soup.select_one('h1').text.strip(),
            'price': soup.select_one('[data-price]').text.strip(),
            'description': soup.select_one('[data-description]').text.strip(),
            'images': [img['src'] for img in soup.select('img[data-product-image]')],
            'specifications': [
                {
                    'name': spec.select_one('[data-spec-name]').text.strip(),
                    'value': spec.select_one('[data-spec-value]').text.strip()
                }
                for spec in soup.select('[data-specification]')
            ]
        }
        
        return self.product_data

async def scrape_with_scrapy(url: str) -> Dict[str, Any]:
    """Scrape product data using Scrapy"""
    process = CrawlerProcess(get_project_settings())
    spider = ProductSpider(url=url)
    process.crawl(spider)
    process.start()
    return spider.product_data 