#!/home/lubancat/.pyenv/versions/3.12.9/bin/python3.12
#
# RAG search - Query articles from command line
#

import sys
import os

# Add parent directory to path so we can import rag_struct
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

if __name__ == "__main__":
    # Original bash script: python rag_struct/server.py --query "$1"
    # We need to pass --query explicitly since the query is a positional arg
    query = sys.argv[1] if len(sys.argv) > 1 else None
    if query:
        sys.argv = [sys.argv[0], "--query", query]
    from rag_struct.server import main
    main()
