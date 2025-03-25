"use client";

import { useState } from "react";

interface ProductUrlFormProps {
  onSubmit: (url: string, pages: number, model: string) => Promise<void>;
  isLoading: boolean;
}

export default function ProductUrlForm({ onSubmit, isLoading }: ProductUrlFormProps) {
  const [url, setUrl] = useState("");
  const [pages, setPages] = useState(1);
  const [model, setModel] = useState("distilbert-base-uncased-finetuned-sst-2-english");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!url) {
      setError("Please enter a product URL");
      return;
    }

    try {
      await onSubmit(url, pages, model);
      setUrl("");
    } catch {
      setError("Failed to analyze product. Please try again.");
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-10">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Analyze a Product</h2>

      {/* Info Section */}
      <div className="mb-6 text-sm text-gray-700 dark:text-gray-300 space-y-2">
        <p>
          Paste the URL of a product page (e.g., from Amazon) to analyze customer reviews using AI.
        </p>
        <p>
          You can select how many pages of reviews to analyze (each page typically includes ~10
          reviews), and choose the sentiment analysis model you prefer.
        </p>
        <p>
          The analysis will include sentiment classification, bias detection, credibility scoring,
          and summary insights such as average rating and rating distribution.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* URL input */}
        <div>
          <label
            htmlFor="url"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >
            Product URL
          </label>
          <div className="flex gap-2">
            <input
              type="url"
              id="url"
              value={url}
              onChange={e => setUrl(e.target.value)}
              placeholder="https://example.com/product"
              className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2 text-gray-900 dark:text-white"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? "Analyzing..." : "Analyze"}
            </button>
          </div>
          {error && <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>}
        </div>

        {/* Number of Pages */}
        <div>
          <label
            htmlFor="pages"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Number of Pages (10 reviews per page)
          </label>
          <select
            id="pages"
            value={pages}
            onChange={e => setPages(parseInt(e.target.value))}
            className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2 text-gray-900 dark:text-white"
            disabled={isLoading}
          >
            {[1, 2, 3, 4, 5].map(p => (
              <option key={p} value={p}>
                {p} Page{p > 1 && "s"}
              </option>
            ))}
          </select>
        </div>

        {/* Model Selection */}
        <div>
          <label
            htmlFor="model"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Sentiment Model
          </label>
          <select
            id="model"
            value={model}
            onChange={e => setModel(e.target.value)}
            className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2 text-gray-900 dark:text-white"
            disabled={isLoading}
          >
            <option value="distilbert-base-uncased-finetuned-sst-2-english">
              DistilBERT (SST-2)
            </option>
            <option value="nlptown/bert-base-multilingual-uncased-sentiment">
              BERT Multilingual
            </option>
            <option value="cardiffnlp/twitter-roberta-base-sentiment">RoBERTa Twitter</option>
          </select>
        </div>
      </form>
    </div>
  );
}
