#!/usr/bin/env python3
"""
RAG Server - HTTP search API for blog articles with TF-IDF ranking.
"""

import argparse
import json
import math
import re
from collections import Counter
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import List, Dict, Any, Set

import jieba

INDEX_FILE = Path(__file__).parent / "index_data" / "articles.json"

# Chinese stopwords - common words with low information value
STOPWORDS: Set[str] = {
    "的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个",
    "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好",
    "自己", "这", "那", "他", "她", "它", "们", "这个", "那个", "什么", "怎么",
    "为什么", "可以", "因为", "所以", "但是", "如果", "虽然", "还是", "或者", "而且",
    "然后", "之后", "之前", "现在", "时候", "年", "月", "日", "时", "分", "秒",
    "从", "向", "对", "把", "被", "让", "给", "跟", "比", "等", "等", "等等",
    "能", "能够", "可能", "应该", "必须", "需要", "想", "想要", "开始", "进行",
    "完成", "使用", "通过", "进行", "成为", "做", "成为", "之", "其", "及", "与",
    "而", "且", "并", "又", "再", "已", "已经", "曾", "曾经", "将", "将要",
    "只", "仅", "仅仅", "才", "刚", "刚刚", "正", "正在", "已", "一下", "一点",
    "一些", "几", "几个", "每", "各", "某", "这种", "那种", "如此", "这样",
    "那样", "怎样", "如何", "多", "少", "很多", "很少", "一些", "全部", "所有",
    "一些", "部分", "其中", "包括", "除了", "以外", "除了", "以为", "认为",
    "觉得", "知道", "发现", "看到", "听到", "感觉", "希望", "相信", "相信",
    "大家", "我们", "你们", "他们", "她们", "它们", "自己", "本身", "本人",
    "此处", "此时", "此地", "此地", "如此", "本", "该", "这款", "那款",
    "本文", "此", "彼", "其", "其余", "其他", "其它", "另", "另外", "其它",
}

# Title weight for relevance scoring
TITLE_WEIGHT = 2.0
EXCERPT_WEIGHT = 1.5
PATH_WEIGHT = 1.0
CONTENT_WEIGHT = 0.5

# Global IDF table and document count
_g_idf: Dict[str, float] = {}
_g_total_docs: int = 0


def tokenize_chinese(text: str) -> List[str]:
    """Tokenize Chinese text into words using jieba."""
    if not text:
        return []
    # jieba.lcut returns list of words
    words = jieba.lcut(text)
    # Filter out stopwords, punctuation, and single characters
    return [w for w in words if w not in STOPWORDS and len(w) > 1 and not re.match(r'^[^\w]+$', w)]


def calculate_idf(articles: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate IDF for all terms in the corpus."""
    global _g_total_docs

    _g_total_docs = len(articles)
    if _g_total_docs == 0:
        return {}

    # Count document frequency for each term
    doc_freq: Counter = Counter()

    for article in articles:
        # Combine all text fields
        text = " ".join([
            article.get("title", ""),
            article.get("excerpt", ""),
            article.get("content", "")
        ])

        # Get unique terms in this document
        words = set(tokenize_chinese(text))
        for word in words:
            doc_freq[word] += 1

    # Calculate IDF using standard formula: log(N / df)
    idf: Dict[str, float] = {}
    for word, df in doc_freq.items():
        # IDF with smoothing to avoid division by zero and handle unknown terms
        idf[word] = math.log(_g_total_docs / (df + 1)) + 1

    return idf


def load_index() -> Dict[str, Any]:
    """Load article index from file and precompute IDF."""
    global _g_idf

    if not INDEX_FILE.exists():
        return {"articles": []}

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        index_data = json.load(f)

    articles = index_data.get("articles", [])

    # Precompute IDF table
    _g_idf = calculate_idf(articles)

    return index_data


def calculate_relevance(query: str, article: Dict[str, Any]) -> float:
    """Calculate TF-IDF relevance score between query and article."""
    global _g_idf

    # Tokenize query
    query_words = tokenize_chinese(query)
    if not query_words:
        return 0.0

    # Get article text fields
    title = article.get("title", "")
    excerpt = article.get("excerpt", "")
    content = article.get("content", "")
    path = article.get("path", "")

    # Tokenize article fields
    title_words = tokenize_chinese(title)
    excerpt_words = tokenize_chinese(excerpt)
    content_words = tokenize_chinese(content)
    path_words = tokenize_chinese(path)

    # Count term frequencies
    title_freq = Counter(title_words)
    excerpt_freq = Counter(excerpt_words)
    content_freq = Counter(content_words)
    path_freq = Counter(path_words)

    score = 0.0

    for word in query_words:
        # Get IDF for this word (use average IDF if unknown)
        idf = _g_idf.get(word, math.log(_g_total_docs + 1) + 1)

        # Title matches (highest weight) - TF * IDF
        tf_title = title_freq.get(word, 0)
        score += tf_title * idf * TITLE_WEIGHT

        # Exact title match bonus
        if query in title:
            score += TITLE_WEIGHT * idf

        # Excerpt matches
        tf_excerpt = excerpt_freq.get(word, 0)
        score += tf_excerpt * idf * EXCERPT_WEIGHT

        # Path matches
        tf_path = path_freq.get(word, 0)
        score += tf_path * idf * PATH_WEIGHT

        # Content matches (capped contribution)
        tf_content = content_freq.get(word, 0)
        content_contribution = min(tf_content * idf * CONTENT_WEIGHT, 2.0 * idf)
        score += content_contribution

    return score


def search_articles(query: str, articles: List[Dict[str, Any]], max_results: int = 10) -> List[Dict[str, Any]]:
    """Search articles by query, returning ranked results."""
    if not query.strip():
        return []

    results = []
    for article in articles:
        relevance = calculate_relevance(query, article)
        if relevance > 0:
            result = {
                "title": article.get("title", ""),
                "path": article.get("path", ""),
                "date": article.get("date", ""),
                "categories": article.get("categories", []),
                "excerpt": article.get("excerpt", ""),
                "relevance": round(relevance, 3),
            }
            results.append(result)

    # Sort by relevance descending
    results.sort(key=lambda x: x["relevance"], reverse=True)

    return results[:max_results]


class RAGHandler(BaseHTTPRequestHandler):
    """HTTP request handler for RAG search API."""

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def send_json(self, data: Dict[str, Any], status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        """Handle GET requests."""
        index_data = load_index()
        articles = index_data.get("articles", [])

        if self.path.startswith("/search"):
            # Parse query parameter
            query = ""
            if "?" in self.path:
                query_part = self.path.split("?", 1)[1]
                for param in query_part.split("&"):
                    if param.startswith("q="):
                        query = param[2:]
                        break

            results = search_articles(query, articles)
            self.send_json({
                "query": query,
                "count": len(results),
                "results": results,
            })

        elif self.path == "/list":
            # List all articles
            article_list = [
                {
                    "title": a.get("title", ""),
                    "path": a.get("path", ""),
                    "date": a.get("date", ""),
                    "categories": a.get("categories", []),
                    "excerpt": a.get("excerpt", ""),
                }
                for a in articles
            ]
            self.send_json({
                "count": len(article_list),
                "articles": article_list,
            })

        elif self.path == "/health":
            self.send_json({"status": "ok"})

        else:
            self.send_json({"error": "Not found"}, 404)


def run_query(query: str, port: int = 8765):
    """Run a query against the index without starting server."""
    index_data = load_index()
    articles = index_data.get("articles", [])
    results = search_articles(query, articles)

    print(f"Query: {query}")
    print(f"Found {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   Path: {result['path']}")
        print(f"   Date: {result['date']}")
        print(f"   Relevance: {result['relevance']}")
        print(f"   Excerpt: {result['excerpt'][:100]}...")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="RAG Server - HTTP search API for blog articles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python server.py                      Start server (default port 8765)
  python server.py --port 9000           Start server on port 9000
  python server.py --query "关键词"       Run query in command line mode
  python server.py --help               Show this help message
        """,
    )
    parser.add_argument("--port", type=int, default=8765, help="Server port (default: 8765)")
    parser.add_argument("--query", type=str, help="Run query in command line mode")

    args = parser.parse_args()

    if args.query:
        run_query(args.query, args.port)
    else:
        server_address = ("", args.port)
        httpd = HTTPServer(server_address, RAGHandler)
        print(f"RAG Server started on http://localhost:{args.port}")
        print(f"  GET /search?q=<keyword>  - Search articles")
        print(f"  GET /list                - List all articles")
        print(f"  GET /health              - Health check")
        print(f"\nPress Ctrl+C to stop")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            httpd.shutdown()


if __name__ == "__main__":
    main()
