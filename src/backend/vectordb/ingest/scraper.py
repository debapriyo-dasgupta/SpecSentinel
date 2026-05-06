"""
specsentinel/vectordb/ingest/scraper.py

Fetches rule content from external sources: OWASP, OpenAPI docs, RFC pages.
Converts raw HTML/text into structured rule dicts ready for vector store ingestion.
"""

import hashlib
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ── Source registry ───────────────────────────────────────────────────────────

@dataclass
class RuleSource:
    name:       str
    url:        str
    category:   str          # maps to VectorStore collection
    benchmark:  str
    severity_default: str = "Medium"
    weight_default:   int  = 15
    selector:   str = "article"   # CSS selector for main content


RULE_SOURCES = [
    RuleSource(
        name="OWASP API Security Top 10 2023",
        url="https://owasp.org/API-Security/editions/2023/en/0x11-t10/",
        category="security",
        benchmark="OWASP",
        severity_default="High",
        weight_default=35,
        selector="article",
    ),
    RuleSource(
        name="OWASP API Security - Broken Object Authorization",
        url="https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/",
        category="security",
        benchmark="OWASP",
        severity_default="Critical",
        weight_default=35,
        selector="article",
    ),
    RuleSource(
        name="OWASP API Security - Broken Authentication",
        url="https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/",
        category="security",
        benchmark="OWASP",
        severity_default="Critical",
        weight_default=35,
        selector="article",
    ),
    RuleSource(
        name="OpenAPI 3.x Specification Best Practices",
        url="https://learn.openapis.org/best-practices.html",
        category="design",
        benchmark="OpenAPI Best Practices",
        severity_default="Medium",
        weight_default=20,
        selector="main",
    ),
    RuleSource(
        name="RFC 7807 Problem Details",
        url="https://datatracker.ietf.org/doc/html/rfc7807",
        category="error_handling",
        benchmark="RFC 7807",
        severity_default="High",
        weight_default=15,
        selector="section",
    ),
]


# ── Text chunker ──────────────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """
    Split long text into overlapping chunks for embedding.
    Tries to split on sentence boundaries.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, current, current_len = [], [], 0

    for sentence in sentences:
        slen = len(sentence)
        if current_len + slen > chunk_size and current:
            chunks.append(" ".join(current))
            # Keep last N chars as overlap
            overlap_words = " ".join(current).split()
            overlap_text  = " ".join(overlap_words[-overlap // 10:])
            current = [overlap_text, sentence]
            current_len = len(overlap_text) + slen
        else:
            current.append(sentence)
            current_len += slen

    if current:
        chunks.append(" ".join(current))

    return [c.strip() for c in chunks if len(c.strip()) > 50]


# ── HTML fetcher ──────────────────────────────────────────────────────────────

def fetch_page_text(url: str, selector: str = "article", timeout: int = 15) -> Optional[str]:
    """
    Fetch a web page and extract main content text.
    Returns cleaned text or None on failure.
    """
    headers = {
        "User-Agent": "SpecSentinel-RuleIngestion/1.0 (API Governance Bot)",
        "Accept": "text/html,application/xhtml+xml",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Try the target selector first, fall back to body
        content = soup.select_one(selector) or soup.find("body")
        if not content:
            return None

        # Remove navigation, scripts, styles
        for tag in content.select("nav, script, style, footer, header, .sidebar"):
            tag.decompose()

        text = content.get_text(separator=" ", strip=True)
        text = re.sub(r"\s{2,}", " ", text)   # collapse whitespace
        return text.strip()

    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None


# ── Rule extraction from chunks ───────────────────────────────────────────────

def extract_rules_from_chunks(
    chunks: list[str],
    source: RuleSource,
    page_title: str = "",
) -> list[dict]:
    """
    Convert text chunks into structured rule dicts for vector store ingestion.
    Each chunk becomes one rule entry with auto-generated ID.
    """
    rules = []
    now = datetime.utcnow().isoformat()

    for i, chunk in enumerate(chunks):
        # Generate stable rule ID from source + chunk hash
        chunk_hash = hashlib.md5(chunk.encode()).hexdigest()[:8]
        rule_id = f"EXT-{source.category.upper()[:3]}-{chunk_hash}"

        # Infer severity hints from text
        severity = source.severity_default
        text_lower = chunk.lower()
        if any(w in text_lower for w in ["critical", "must not", "never", "forbidden", "injection"]):
            severity = "Critical"
        elif any(w in text_lower for w in ["should not", "high risk", "vulnerability", "attack"]):
            severity = "High"
        elif any(w in text_lower for w in ["recommended", "consider", "may", "optional"]):
            severity = "Low"

        # Extract likely tags from keywords in chunk
        tags = _extract_tags(chunk)

        rule = {
            "rule_id":       rule_id,
            "source":        source.name,
            "category":      _category_to_class(source.category),
            "severity":      severity,
            "title":         _infer_title(chunk, page_title, i),
            "description":   chunk[:600],
            "check_pattern": _infer_check_pattern(chunk),
            "fix_guidance":  _infer_fix_guidance(chunk),
            "benchmark":     source.benchmark,
            "weight":        source.weight_default,
            "tags":          tags,
            "ingested_at":   now,
            "source_url":    source.url,
        }
        rules.append(rule)

    return rules


def _category_to_class(category: str) -> str:
    return {
        "security":       "Security",
        "design":         "Design",
        "error_handling": "ErrorHandling",
        "documentation":  "Documentation",
        "governance":     "Governance",
    }.get(category, category.title())


def _infer_title(chunk: str, page_title: str, index: int) -> str:
    """Extract a short title from the first sentence or use page title."""
    first_sentence = re.split(r"[.!?]", chunk)[0].strip()
    if len(first_sentence) < 10 or len(first_sentence) > 120:
        return f"{page_title} — Rule {index + 1}" if page_title else f"Rule {index + 1}"
    return first_sentence[:120]


def _infer_check_pattern(chunk: str) -> str:
    """Extract check pattern hints from text."""
    patterns = re.findall(
        r"(missing\s+\w+[\w\s]{5,40}|no\s+\w+[\w\s]{5,40}|lack[s]?\s+\w+[\w\s]{5,40}|"
        r"without\s+\w+[\w\s]{5,40}|absent\s+\w+[\w\s]{5,40})",
        chunk.lower()
    )
    if patterns:
        return "; ".join(patterns[:3])
    return "See description for check criteria"


def _infer_fix_guidance(chunk: str) -> str:
    """Extract fix guidance hints from text."""
    fixes = re.findall(
        r"(should\s+[\w\s]{10,80}|must\s+[\w\s]{10,80}|implement\s+[\w\s]{10,80}|"
        r"add\s+[\w\s]{10,80}|use\s+[\w\s]{10,80}|define\s+[\w\s]{10,80})",
        chunk.lower()
    )
    if fixes:
        return "; ".join(fixes[:3]).capitalize()
    return "Refer to source documentation for remediation guidance."


def _extract_tags(text: str) -> list[str]:
    """Extract meaningful keyword tags from text."""
    keyword_map = {
        "authentication": "authentication",
        "authorization": "authorization",
        "oauth": "oauth2",
        "jwt": "jwt",
        "api key": "api-key",
        "rate limit": "rate-limiting",
        "pagination": "pagination",
        "versioning": "versioning",
        "deprecat": "deprecation",
        "error": "error-handling",
        "schema": "schema",
        "inject": "injection",
        "cors": "cors",
        "https": "https",
        "token": "token",
        "scope": "scopes",
        "403": "403",
        "401": "401",
        "429": "429",
        "swagger": "openapi",
        "openapi": "openapi",
    }
    text_lower = text.lower()
    return list({v for k, v in keyword_map.items() if k in text_lower})


# ── Main ingestion function ───────────────────────────────────────────────────

def ingest_from_source(source: RuleSource, chunk_size: int = 800) -> list[dict]:
    """
    Full pipeline: fetch → chunk → extract rules for one RuleSource.
    Returns list of rule dicts ready for vector store upsert.
    """
    logger.info(f"Fetching: {source.url}")
    text = fetch_page_text(source.url, selector=source.selector)

    if not text:
        logger.warning(f"No content fetched from {source.url} — skipping.")
        return []

    chunks = chunk_text(text, chunk_size=chunk_size)
    logger.info(f"  → {len(chunks)} chunks from {source.name}")

    rules = extract_rules_from_chunks(chunks, source, page_title=source.name)
    logger.info(f"  → {len(rules)} rules extracted")
    return rules


def ingest_all_sources(
    sources: Optional[list[RuleSource]] = None,
    delay_seconds: float = 2.0,
) -> dict[str, list[dict]]:
    """
    Ingest rules from all configured sources.
    Returns dict: category → list of rule dicts.

    Args:
        sources:       List of RuleSource objects (defaults to RULE_SOURCES)
        delay_seconds: Polite delay between requests
    """
    sources = sources or RULE_SOURCES
    results: dict[str, list[dict]] = {}

    for source in sources:
        rules = ingest_from_source(source)
        if rules:
            cat = source.category
            results.setdefault(cat, []).extend(rules)
        time.sleep(delay_seconds)   # be polite to external servers

    total = sum(len(v) for v in results.values())
    logger.info(f"Ingestion complete: {total} rules across {len(results)} categories")
    return results
