"use client";

import { useState, useEffect } from "react";

interface ProductAnalysisProps {
  data?: {
    product_reviews?: Array<{
      product_review?: string;
      rating?: number;
      sentiment?: {
        label: string;
        score: number;
      };
      bias_scores?: Record<string, number>;
      credibility_score?: number;
    }>;
  };
}

export default function ProductAnalysis({ data }: ProductAnalysisProps) {
  const [showMoreReviews, setShowMoreReviews] = useState(false);
  const [averageRating, setAverageRating] = useState(0);
  const [averageCredibility, setAverageCredibility] = useState(0);
  const [ratingDistribution, setRatingDistribution] = useState<Record<number, number>>({});

  useEffect(() => {
    if (data?.product_reviews?.length) {
      const ratings = data.product_reviews.map(r => r.rating ?? 0);
      const credibility = data.product_reviews.map(r => r.credibility_score ?? 0);

      const avgRating = ratings.reduce((sum, val) => sum + val, 0) / ratings.length;
      const avgCredibility = credibility.reduce((sum, val) => sum + val, 0) / credibility.length;

      const distribution: Record<number, number> = {};
      ratings.forEach(r => {
        const key = Math.round(r);
        distribution[key] = (distribution[key] || 0) + 1;
      });

      setAverageRating(Number(avgRating.toFixed(2)));
      setAverageCredibility(Number(avgCredibility.toFixed(2)));
      setRatingDistribution(distribution);
    }
  }, [data]);

  if (!data) {
    return <div className="text-red-500">No product data available.</div>;
  }

  return (
    <div className="space-y-8">
      {/* Summary Stats */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Analysis Summary</h2>
        <p className="text-gray-700 dark:text-gray-300">Total Reviews Analyzed: {data.product_reviews?.length}</p>
        <p className="text-gray-700 dark:text-gray-300">Average Rating: {averageRating} ★</p>
        <p className="text-gray-700 dark:text-gray-300">Average Credibility: {averageCredibility}%</p>

        <div className="mt-4">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Rating Distribution</h3>
          <div className="space-y-1">
            {[5, 4, 3, 2, 1].map(star => (
              <div key={star} className="flex items-center gap-2">
                <span className="w-8 text-sm font-medium text-gray-700 dark:text-gray-300">{star}★</span>
                <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${(ratingDistribution[star] || 0) / (data.product_reviews?.length || 1) * 100}%` }}
                  ></div>
                </div>
                <span className="text-sm text-gray-600 dark:text-gray-300">{ratingDistribution[star] || 0}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Product Reviews */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Product Reviews</h2>
        <div className="grid grid-cols-1 gap-4">
          {(showMoreReviews ? data.product_reviews : data.product_reviews?.slice(0, 5))?.map((review, index) => {
            const rating = review.rating ?? 0;
            return (
              <div key={index} className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                <p className="text-gray-600 dark:text-gray-300">{review.product_review}</p>

                <div className="flex items-center gap-2 mt-2">
                  {/* Star Rating */}
                  <div className="flex items-center">
                    {rating > 0 ? (
                      Array.from({ length: 5 }).map((_, i) => (
                        <span key={i} className={`text-lg ${i < rating ? "text-yellow-500" : "text-gray-300"}`}>
                          ★
                        </span>
                      ))
                    ) : (
                      <span className="text-gray-400 text-sm">No Rating</span>
                    )}
                  </div>

                  {/* Sentiment */}
                  {review.sentiment && (
                    <p className={`text-sm font-semibold ${
                      review.sentiment.label === "POSITIVE"
                        ? "text-green-600 dark:text-green-400"
                        : "text-red-600 dark:text-red-400"
                    }`}>
                      {review.sentiment.label} ({(review.sentiment.score * 100).toFixed(1)}%)
                    </p>
                  )}
                </div>

                {/* Bias Scores */}
                {review.bias_scores && (
                  <div className="mt-2 text-sm text-gray-500">
                    {Object.entries(review.bias_scores).map(([bias, score]) => (
                      <p key={bias}>{bias}: {(score * 100).toFixed(1)}%</p>
                    ))}
                  </div>
                )}

                {/* Credibility Score */}
                {review.credibility_score !== undefined && (
                  <p className="mt-2 text-sm text-blue-600 dark:text-blue-400">
                    Credibility: {review.credibility_score}%
                  </p>
                )}
              </div>
            );
          })}
        </div>
        {data.product_reviews && data.product_reviews.length > 5 && (
          <button 
            onClick={() => setShowMoreReviews(!showMoreReviews)}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            {showMoreReviews ? "Show Less" : "Show More"}
          </button>
        )}
      </div>
    </div>
  );
}