"""
specsentinel/vectordb/store/chroma_client.py

ChromaDB vector store client for SpecSentinel rule base.
Manages 5 rule collections: security, design, error_handling, documentation, governance.
"""

import json
import os
import logging
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

# ── Collection names (one per scoring category) ──────────────────────────────
COLLECTIONS = {
    "security":      "specsentinel_security_rules",
    "design":        "specsentinel_design_rules",
    "error_handling":"specsentinel_error_handling_rules",
    "documentation": "specsentinel_documentation_rules",
    "governance":    "specsentinel_governance_rules",
}

# ── Category → seed file mapping ─────────────────────────────────────────────
SEED_FILES = {
    "security":       "owasp_rules.json",
    "design":         "openapi_rules.json",
    "error_handling": "governance_rules.json",   # error rules are in this file
    "documentation":  "governance_rules.json",   # doc rules are in this file
    "governance":     "governance_rules.json",
}

SEED_DIR = Path(__file__).parent.parent.parent.parent / "data" / "rules"
CHROMA_DB_PATH = Path(__file__).parent.parent.parent.parent / ".chromadb"


class SpecSentinelVectorStore:
    """
    Manages ChromaDB collections for SpecSentinel rule base.

    Usage:
        store = SpecSentinelVectorStore()
        store.initialize()                  # Creates collections and seeds them
        results = store.query_rules(
            category="security",
            query_text="missing 401 response on authenticated endpoint",
            n_results=5
        )
    """

    def __init__(self, persist_path: Optional[str] = None):
        db_path = persist_path or str(CHROMA_DB_PATH)
        os.makedirs(db_path, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False),
        )
        self._collections: dict = {}
        logger.info(f"ChromaDB initialized at: {db_path}")

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _get_or_create_collection(self, name: str):
        """Get existing collection or create a new one."""
        col = self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},   # cosine similarity for semantic search
        )
        return col

    def _load_seed_rules(self, category: str) -> list[dict]:
        """Load seed rules JSON for a category, filtering by category field."""
        seed_file = SEED_FILES.get(category)
        if not seed_file:
            return []

        path = SEED_DIR / seed_file
        if not path.exists():
            logger.warning(f"Seed file not found: {path}")
            return []

        with open(path) as f:
            all_rules = json.load(f)

        # Filter by category (e.g., only ErrorHandling rules for error_handling collection)
        category_map = {
            "security":       "Security",
            "design":         "Design",
            "error_handling": "ErrorHandling",
            "documentation":  "Documentation",
            "governance":     "Governance",
        }
        expected = category_map.get(category, "")
        filtered = [r for r in all_rules if r.get("category", "") == expected]

        # For security, include OWASP rules even if file has all categories
        if category == "security" and not filtered:
            filtered = all_rules  # owasp_rules.json is already all Security

        return filtered

    def _rule_to_document(self, rule: dict) -> str:
        """Convert a rule dict to a rich text document for embedding."""
        return (
            f"Title: {rule.get('title', '')}. "
            f"Description: {rule.get('description', '')}. "
            f"Check for: {rule.get('check_pattern', '')}. "
            f"Fix: {rule.get('fix_guidance', '')}. "
            f"Tags: {', '.join(rule.get('tags', []))}."
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def initialize(self, force_reseed: bool = False):
        """
        Initialize all collections and seed them with rules.
        If force_reseed=True, existing documents are cleared and re-added.
        """
        for cat, col_name in COLLECTIONS.items():
            col = self._get_or_create_collection(col_name)
            self._collections[cat] = col

            existing = col.count()
            if existing > 0 and not force_reseed:
                logger.info(f"[{cat}] Collection already has {existing} rules — skipping seed.")
                continue

            rules = self._load_seed_rules(cat)
            if not rules:
                logger.warning(f"[{cat}] No seed rules found.")
                continue

            if force_reseed and existing > 0:
                col.delete(where={"source": {"$ne": "__none__"}})  # clear all

            self._upsert_rules(cat, rules)
            logger.info(f"[{cat}] Seeded {len(rules)} rules into '{col_name}'")

    def _upsert_rules(self, category: str, rules: list[dict]):
        """Upsert a list of rule dicts into the category collection."""
        col = self._collections.get(category)
        if col is None:
            raise RuntimeError(f"Collection for '{category}' not initialized. Call initialize() first.")

        ids, documents, metadatas = [], [], []
        for rule in rules:
            ids.append(rule["rule_id"])
            documents.append(self._rule_to_document(rule))
            # Store all metadata fields for retrieval
            metadatas.append({
                "rule_id":    rule.get("rule_id", ""),
                "source":     rule.get("source", ""),
                "category":   rule.get("category", ""),
                "severity":   rule.get("severity", ""),
                "title":      rule.get("title", ""),
                "benchmark":  rule.get("benchmark", ""),
                "weight":     rule.get("weight", 0),
                "tags":       ",".join(rule.get("tags", [])),
                "fix_guidance": rule.get("fix_guidance", ""),
                "check_pattern": rule.get("check_pattern", ""),
            })

        col.upsert(ids=ids, documents=documents, metadatas=metadatas)

    def upsert_external_rules(self, category: str, rules: list[dict]):
        """
        Add or update rules from external ingestion (scraper output).
        Called by the ingestion pipeline after fetching from OWASP, etc.
        """
        if category not in self._collections:
            self._get_or_create_collection(COLLECTIONS[category])
            self._collections[category] = self.client.get_collection(COLLECTIONS[category])

        self._upsert_rules(category, rules)
        logger.info(f"[{category}] Upserted {len(rules)} externally ingested rules.")

    def query_rules(
        self,
        category: str,
        query_text: str,
        n_results: int = 5,
        severity_filter: Optional[str] = None,
    ) -> list[dict]:
        """
        Semantic search for rules matching a query signal.

        Args:
            category:        One of security, design, error_handling, documentation, governance
            query_text:      Natural language description of the issue found in the spec
            n_results:       Number of top matching rules to return
            severity_filter: Optional filter e.g. "Critical" or "High"

        Returns:
            List of matched rule dicts with similarity distance included.
        """
        col = self._collections.get(category)
        if col is None:
            logger.warning(f"Collection '{category}' not found. Run initialize() first.")
            return []

        where_filter = {}
        if severity_filter:
            where_filter = {"severity": {"$eq": severity_filter}}

        results = col.query(
            query_texts=[query_text],
            n_results=min(n_results, col.count()),
            where=where_filter if where_filter else None,
        )

        matched = []
        if not results or not results["ids"]:
            return matched

        for i, rule_id in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][i]
            doc  = results["documents"][0][i]
            dist = results["distances"][0][i]

            matched.append({
                "rule_id":       rule_id,
                "title":         meta.get("title"),
                "severity":      meta.get("severity"),
                "category":      meta.get("category"),
                "source":        meta.get("source"),
                "benchmark":     meta.get("benchmark"),
                "weight":        meta.get("weight"),
                "fix_guidance":  meta.get("fix_guidance"),
                "check_pattern": meta.get("check_pattern"),
                "tags":          meta.get("tags", "").split(","),
                "similarity":    round(1 - dist, 4),   # cosine: 1=identical
                "document":      doc,
            })

        # Sort by similarity descending
        matched.sort(key=lambda x: x["similarity"], reverse=True)
        return matched

    def query_rules_batch(
        self,
        category: str,
        query_texts: list[str],
        n_results: int = 5,
        severity_filter: Optional[str] = None,
    ) -> list[list[dict]]:
        """
        Batch semantic search for multiple queries at once.
        
        Args:
            category:        One of security, design, error_handling, documentation, governance
            query_texts:     List of natural language descriptions
            n_results:       Number of top matching rules per query
            severity_filter: Optional filter e.g. "Critical" or "High"
        
        Returns:
            List of matched rule lists (one list per query_text)
        """
        col = self._collections.get(category)
        if col is None:
            logger.warning(f"Collection '{category}' not found. Run initialize() first.")
            return [[] for _ in query_texts]
        
        if not query_texts:
            return []
        
        collection_size = col.count()
        logger.debug(f"Batch querying {len(query_texts)} texts against {collection_size} rules in '{category}' collection")
        
        where_filter = {}
        if severity_filter:
            where_filter = {"severity": {"$eq": severity_filter}}
            logger.debug(f"Applying severity filter: {severity_filter}")
        
        # Batch query - ChromaDB processes all queries in one call
        results = col.query(
            query_texts=query_texts,
            n_results=min(n_results, collection_size),
            where=where_filter if where_filter else None,
        )
        
        # Process results for each query
        all_matched = []
        if not results or not results["ids"]:
            logger.debug(f"No results returned from batch query for category '{category}'")
            return [[] for _ in query_texts]
        
        total_results = 0
        for query_idx in range(len(query_texts)):
            matched = []
            if query_idx >= len(results["ids"]):
                all_matched.append(matched)
                continue
                
            for i, rule_id in enumerate(results["ids"][query_idx]):
                meta = results["metadatas"][query_idx][i]
                doc  = results["documents"][query_idx][i]
                dist = results["distances"][query_idx][i]
                
                matched.append({
                    "rule_id":       rule_id,
                    "title":         meta.get("title"),
                    "severity":      meta.get("severity"),
                    "category":      meta.get("category"),
                    "source":        meta.get("source"),
                    "benchmark":     meta.get("benchmark"),
                    "weight":        meta.get("weight"),
                    "fix_guidance":  meta.get("fix_guidance"),
                    "check_pattern": meta.get("check_pattern"),
                    "tags":          meta.get("tags", "").split(","),
                    "similarity":    round(1 - dist, 4),
                    "document":      doc,
                })
            
            # Sort by similarity descending
            matched.sort(key=lambda x: x["similarity"], reverse=True)
            all_matched.append(matched)
            total_results += len(matched)
        
        logger.debug(f"Batch query returned {total_results} total matches across {len(query_texts)} queries")
        return all_matched

    def get_collection_stats(self) -> dict:
        """Return rule counts per collection."""
        stats = {}
        for cat, col_name in COLLECTIONS.items():
            try:
                col = self.client.get_collection(col_name)
                stats[cat] = col.count()
            except Exception:
                stats[cat] = 0
        return stats

    def delete_rules_by_source(self, category: str, source: str):
        """Remove all rules from a specific source (used before re-ingestion)."""
        col = self._collections.get(category)
        if col:
            col.delete(where={"source": {"$eq": source}})
            logger.info(f"[{category}] Deleted rules from source: {source}")
