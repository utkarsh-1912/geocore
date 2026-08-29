# Author: Utkarsh Gupta
# License: GPL v3
"""
Lightweight Local Document Extraction & SQLite/FTS5 Search Indexer.
Enables offline RAG for local geotechnical reports, papers, standards, and notes
conforming to AGENTS.md §11 & §13 without heavyweight external vector databases.
"""

import os
import re
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict

from core.geoai.model_config import get_config_dir


@dataclass
class DocumentChunk:
    chunk_id: str
    doc_id: str
    doc_title: str
    file_path: str
    section_heading: str
    content: str
    page_number: Optional[int] = None
    chunk_index: int = 0


@dataclass
class SearchResult:
    chunk_id: str
    doc_title: str
    file_path: str
    section_heading: str
    content: str
    score: float
    page_number: Optional[int] = None


class LocalDocumentIndexer:
    """
    Lightweight SQLite FTS5 indexer for local engineering documents.
    """
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = get_config_dir() / "geoai_research.db"
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite database with FTS5 virtual table for full-text search."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Document metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    title TEXT,
                    file_path TEXT,
                    file_hash TEXT,
                    chunk_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # FTS5 Virtual Table for BM25 text search
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS document_chunks USING fts5(
                    chunk_id UNINDEXED,
                    doc_id UNINDEXED,
                    doc_title,
                    file_path UNINDEXED,
                    section_heading,
                    content,
                    page_number UNINDEXED,
                    tokenize = 'porter unicode61'
                )
            """)
            conn.commit()

    @staticmethod
    def _chunk_text(text: str, max_chunk_chars: int = 1000, overlap_chars: int = 150) -> List[Tuple[str, str]]:
        """
        Splits text into coherent paragraphs and sections while preserving headings.
        Returns List of (section_heading, chunk_text).
        """
        lines = text.splitlines()
        chunks: List[Tuple[str, str]] = []
        current_heading = "General"
        current_buffer: List[str] = []
        current_length = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Detect markdown or capitalized section headings
            if stripped.startswith('#') or (len(stripped) < 80 and stripped.isupper()):
                if current_buffer:
                    chunk_str = "\n".join(current_buffer)
                    if len(chunk_str) > 30:
                        chunks.append((current_heading, chunk_str))
                    current_buffer = []
                    current_length = 0
                current_heading = stripped.lstrip('#').strip()
                continue

            current_buffer.append(stripped)
            current_length += len(stripped)

            if current_length >= max_chunk_chars:
                chunk_str = "\n".join(current_buffer)
                chunks.append((current_heading, chunk_str))
                # Keep last paragraph for overlap
                current_buffer = current_buffer[-1:] if len(current_buffer) > 1 else []
                current_length = sum(len(s) for s in current_buffer)

        if current_buffer:
            chunk_str = "\n".join(current_buffer)
            if len(chunk_str) > 20:
                chunks.append((current_heading, chunk_str))

        return chunks

    def index_text_content(
        self,
        doc_id: str,
        title: str,
        content: str,
        file_path: str = "memory"
    ) -> int:
        """Indexes raw text or markdown content into the FTS5 database."""
        file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        raw_chunks = self._chunk_text(content)
        if not raw_chunks:
            return 0

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Remove previous chunks if re-indexing same doc_id
            cursor.execute("DELETE FROM document_chunks WHERE doc_id = ?", (doc_id,))
            cursor.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))

            # Insert document record
            cursor.execute("""
                INSERT INTO documents (doc_id, title, file_path, file_hash, chunk_count)
                VALUES (?, ?, ?, ?, ?)
            """, (doc_id, title, file_path, file_hash, len(raw_chunks)))

            # Insert chunks into FTS5
            for idx, (heading, chunk_text) in enumerate(raw_chunks):
                chunk_id = f"{doc_id}_c{idx}"
                cursor.execute("""
                    INSERT INTO document_chunks (chunk_id, doc_id, doc_title, file_path, section_heading, content, page_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (chunk_id, doc_id, title, file_path, heading, chunk_text, 1))

            conn.commit()

        return len(raw_chunks)

    def index_file(self, file_path: Path) -> int:
        """Extracts and indexes text from a local file (.txt, .md, .csv, .json)."""
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"File '{file_path}' does not exist.")

        title = path_obj.stem.replace("_", " ").title()
        doc_id = path_obj.name

        try:
            with open(path_obj, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return self.index_text_content(doc_id=doc_id, title=title, content=content, file_path=str(path_obj))
        except Exception as e:
            logger.warning(f"Could not index file {file_path}: {e}")
            return 0

    def index_directory(self, dir_path: Path) -> Dict[str, int]:
        """Scans and indexes all supported engineering documents in a directory."""
        dir_obj = Path(dir_path)
        if not dir_obj.exists() or not dir_obj.is_dir():
            return {}

        results = {}
        for file in dir_obj.iterdir():
            if file.is_file() and file.suffix.lower() in ('.txt', '.md', '.csv', '.json', '.ags'):
                count = self.index_file(file)
                results[file.name] = count
        return results

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Executes BM25 ranked full-text query over indexed chunks.
        """
        clean_query = re.sub(r'[^a-zA-Z0-9\s]', ' ', query).strip()
        if not clean_query:
            return []

        # Format FTS5 query with prefix search
        tokens = [t for t in clean_query.split() if len(t) > 1]
        if not tokens:
            return []
        fts_query = " OR ".join(f'"{t}"*' for t in tokens)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT chunk_id, doc_title, file_path, section_heading, content, page_number, rank
                FROM document_chunks
                WHERE document_chunks MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (fts_query, top_k))
            rows = cursor.fetchall()

        results = []
        for r in rows:
            results.append(SearchResult(
                chunk_id=r[0],
                doc_title=r[1],
                file_path=r[2],
                section_heading=r[3],
                content=r[4],
                page_number=r[5],
                score=float(r[6])
            ))
        return results

    def get_document_count(self) -> int:
        """Returns total number of indexed documents."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents")
            row = cursor.fetchone()
            return int(row[0]) if row else 0


# Global local indexer instance
local_indexer = LocalDocumentIndexer()
