# Author: Utkarsh Gupta
# License: GPL v3
"""
Canonical Pydantic Schemas for Local Document Research & RAG Tools.
"""

from typing import List, Optional, Dict, Any
from pydantic import Field, AliasChoices
from core.geoai.schemas.base import GeoAIBaseModel, GeoAIOutputModel, GeotechnicalField


class SearchLocalDocumentsInput(GeoAIBaseModel):
    """
    Searches indexed local geotechnical documents, papers, reports, and standards
    using BM25 full-text search.
    """
    query: str = GeotechnicalField(
        ...,
        description="Engineering search keywords or phrase",
        validation_alias=AliasChoices('query', 'search_term', 'keywords', 'q')
    )
    top_k: int = GeotechnicalField(
        5,
        ge=1,
        le=20,
        unit="-",
        description="Maximum number of relevant document excerpts to retrieve",
        validation_alias=AliasChoices('top_k', 'limit', 'k')
    )


class SearchLocalDocumentsOutput(GeoAIOutputModel):
    query: str = GeotechnicalField(..., description="Original search query")
    total_found: int = GeotechnicalField(..., unit="-", description="Number of matching passages found")
    results: List[Dict[str, Any]] = GeotechnicalField(..., description="List of matching document excerpts with source metadata")


class IndexDocumentTextInput(GeoAIBaseModel):
    """
    Indexes raw text or markdown technical content into the local SQLite/FTS5 search database.
    """
    doc_id: str = GeotechnicalField(..., description="Unique document identifier or filename")
    title: str = GeotechnicalField(..., description="Human-readable document title")
    content: str = GeotechnicalField(..., description="Full text or markdown content to index")


class IndexDocumentTextOutput(GeoAIOutputModel):
    doc_id: str = GeotechnicalField(..., description="Document identifier")
    indexed_chunks: int = GeotechnicalField(..., unit="-", description="Number of semantic chunks indexed")
    status: str = GeotechnicalField("indexed", description="Indexing operation status")
