#!/bin/bash
#
# Generate/update RAG index for blog articles
#

cd "$(dirname "$0")/.."
python rag_struct/indexer.py "$@"
