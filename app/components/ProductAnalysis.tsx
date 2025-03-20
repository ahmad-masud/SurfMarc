'use client';

import { useState } from 'react';

interface ProductAnalysisProps {
  data: {
    product: {
      title: string;
      price: string;
      description: string;
      specifications: Array<{
        name: string;
        value: string;
      }>;
    };
    sentiment_analysis: {
      overall_sentiment: string;
      positive_count: number;
      negative_count: number;
      sentiment_details: Array<{
        label: string;
        score: number;
      }>;
    };
    classification: {
      categories: Record<string, number>;
    };
  };
}

export default function ProductAnalysis({ data }: ProductAnalysisProps) {
  return (
    <div className="space-y-8 mb-[10px]">
      {/* Main Product Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="space-y-4">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {data.product.title}
          </h1>
          <p className="text-2xl font-semibold text-blue-600 dark:text-blue-400">
            {data.product.price}
          </p>
          <p className="text-gray-600 dark:text-gray-300">
            {data.product.description}
          </p>

          {/* Specifications */}
          <div className="mt-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Specifications
            </h2>
            <div className="grid grid-cols-2 gap-4">
              {data.product.specifications.map((spec, index) => (
                <div
                  key={index}
                  className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg"
                >
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {spec.name}
                  </p>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {spec.value}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Sentiment Analysis */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Sentiment Analysis
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Overall Sentiment
            </p>
            <p
              className={`text-xl font-semibold ${
                data.sentiment_analysis.overall_sentiment === 'POSITIVE'
                  ? 'text-green-600 dark:text-green-400'
                  : 'text-red-600 dark:text-red-400'
              }`}
            >
              {data.sentiment_analysis.overall_sentiment}
            </p>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Positive Reviews
            </p>
            <p className="text-xl font-semibold text-green-600 dark:text-green-400">
              {data.sentiment_analysis.positive_count}
            </p>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Negative Reviews
            </p>
            <p className="text-xl font-semibold text-red-600 dark:text-red-400">
              {data.sentiment_analysis.negative_count}
            </p>
          </div>
        </div>
      </div>

      {/* Product Classification */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Product Classification
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {Object.entries(data.classification.categories).map(([category, score]) => (
            <div
              key={category}
              className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg"
            >
              <p className="text-sm text-gray-500 dark:text-gray-400 capitalize">
                {category}
              </p>
              <div className="mt-2">
                <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                  <div
                    className="bg-blue-600 dark:bg-blue-400 h-2 rounded-full"
                    style={{ width: `${score * 100}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                  {(score * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 