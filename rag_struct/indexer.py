#!/usr/bin/env python3
"""
RAG Indexer - Generate and update article index for Hexo blog.
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

POSTS_DIR = Path(__file__).parent.parent / "source" / "_posts"
PAGES_DIR = Path(__file__).parent.parent / "source"
INDEX_FILE = Path(__file__).parent / "index_data" / "articles.json"


def slugify(text):
    """Convert text to URL-safe slug."""
    # Normalize unicode characters
    text = unicodedata.normalize('NFKC', text)
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')



def extract_frontmatter(content):
    """Extract frontmatter from markdown content."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter


def extract_excerpt(content, max_length=200):
    """Extract excerpt from markdown content, removing HTML tags."""
    # Remove frontmatter
    content = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL)

    # Remove code blocks
    content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)

    # Remove inline code
    content = re.sub(r"`[^`]+`", "", content)

    # Remove HTML tags
    content = re.sub(r"<[^>]+>", "", content)

    # Remove markdown images and links
    content = re.sub(r"!\[.*?\]\(.*?\)", "", content)
    content = re.sub(r"\[.*?\]\(.*?\)", "", content)

    # Remove headers markers
    content = re.sub(r"^#+\s*", "", content, flags=re.MULTILINE)

    # Remove special markers like <!-- more -->
    content = re.sub(r"<!--\s*more\s*-->", "", content)

    # Clean up whitespace
    content = re.sub(r"\n+", " ", content)
    content = re.sub(r"\s+", " ", content)

    return content.strip()[:max_length]


def parse_markdown_file(filepath):
    """Parse a markdown file and extract article metadata."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    frontmatter = extract_frontmatter(content)
    excerpt = extract_excerpt(content)

    # Get full content (without frontmatter)
    full_content = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL)

    return {
        "title": frontmatter.get("title", filepath.stem),
        "path": str(filepath.relative_to(Path(__file__).parent.parent)),
        "date": frontmatter.get("date", ""),
        "updated": frontmatter.get("updated", ""),
        "categories": [],  # Can be extended to parse categories
        "excerpt": excerpt,
        "content": full_content,
        "filename": filepath.name,
    }


def scan_articles():
    """Scan all markdown files in the posts and pages directories."""
    articles = []

    # Scan posts directory
    if POSTS_DIR.exists():
        for filepath in sorted(POSTS_DIR.glob("*.md")):
            try:
                article = parse_markdown_file(filepath)
                articles.append(article)
            except Exception as e:
                print(f"Error parsing {filepath}: {e}")

    # Scan pages directory (source/*.md, excluding subdirectories like _posts)
    if PAGES_DIR.exists():
        for filepath in sorted(PAGES_DIR.glob("*.md")):
            # Skip files in _posts and other subdirectories
            if filepath.parent == PAGES_DIR:
                try:
                    article = parse_markdown_file(filepath)
                    articles.append(article)
                except Exception as e:
                    print(f"Error parsing {filepath}: {e}")

    return articles


def load_existing_index():
    """Load existing index from file."""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_index(articles, output_path=None, output_format=None):
    """Save articles index to file."""
    if output_format == "hexo" and output_path:
        # Generate NexT local_search compatible format
        hexo_articles = []
        for article in articles:
            # Convert path like "source/_posts/xxx.md" to "/xxx/" format
            path = article["path"]
            # Remove "source/" prefix and file extension
            # Build URL based on permalink format: :year/:month/:day/:title/
            date_str = article.get("date", "")
            if date_str:
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    date_str = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                    # Generate URL from date and title
                    year = dt.strftime("%Y")
                    month = dt.strftime("%m")
                    day = dt.strftime("%d")
                    title_slug = slugify(article.get("title", ""))
                    if path.startswith("source/_posts/"):
                        slug = f"/{year}/{month}/{day}/{title_slug}/"
                    else:
                        slug = "/" + slugify(path.replace("source/", "").replace(".md", ""))
                except ValueError:
                    date_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
                    title_slug = slugify(article.get("title", ""))
                    slug = f"/{title_slug}/"
            else:
                date_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
                title_slug = slugify(article.get("title", ""))
                if path.startswith("source/_posts/"):
                    slug = f"/{title_slug}/"
                else:
                    slug = "/" + slugify(path.replace("source/", "").replace(".md", ""))

            hexo_articles.append({
                "title": article["title"],
                "url": slug,
                "content": article.get("content", article.get("excerpt", "")),
                "date": date_str,
            })

        INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(hexo_articles, f, ensure_ascii=False, indent=2)
        print(f"Hexo search index saved to {output_path} ({len(hexo_articles)} articles)")
    else:
        INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump({"articles": articles, "updated": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
        print(f"Index saved to {INDEX_FILE} ({len(articles)} articles)")


def verify_index(articles):
    """Verify index integrity."""
    if not articles:
        print("Warning: Index is empty")
        return False

    for i, article in enumerate(articles):
        required_fields = ["title", "path", "content"]
        missing = [f for f in required_fields if f not in article]
        if missing:
            print(f"Article {i} missing fields: {missing}")
            return False

        if not article["title"]:
            print(f"Article {i} has empty title")
            return False

    print(f"Index verification passed ({len(articles)} articles)")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="RAG Indexer - Generate and update article index",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python indexer.py              Generate/update index
  python indexer.py --rebuild    Force rebuild index
  python indexer.py --verify      Verify index integrity
  python indexer.py --format hexo --output source/search.json --rebuild
        """,
    )
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild index")
    parser.add_argument("--verify", action="store_true", help="Verify index integrity")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--format", type=str, choices=["hexo"], help="Output format (hexo for NexT local_search)")

    args = parser.parse_args()

    if args.verify:
        articles = load_existing_index()
        if articles is None:
            print("Error: No existing index found")
            sys.exit(1)
        success = verify_index(articles["articles"])
        sys.exit(0 if success else 1)

    existing = None
    if not args.rebuild:
        existing = load_existing_index()

    print(f"Scanning articles in {POSTS_DIR}...")
    articles = scan_articles()

    if not articles:
        print("No articles found")
        sys.exit(1)

    save_index(articles, args.output, args.format)

    if args.rebuild:
        print("Index rebuilt successfully")
    else:
        print("Index updated successfully")


if __name__ == "__main__":
    main()
