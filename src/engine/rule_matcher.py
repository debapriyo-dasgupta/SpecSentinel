"""
specsentinel/engine/rule_matcher.py

Bridges the signal extractor and vector DB.
For each signal from an OpenAPI spec, queries the vector store
and returns matched rules with similarity scores.
"""

from dataclasses import dataclass, field
from typing import Optional

from src.engine.signal_extractor import Signal
from src.vectordb.store.chroma_client import SpecSentinelVectorStore
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# Minimum similarity threshold — below this, matches are ignored
SIMILARITY_THRESHOLD = 0.35


@dataclass
class RuleMatch:
    """A rule matched to a signal, with full context for reporting."""
    signal:      Signal
    rule_id:     str
    title:       str
    severity:    str
    category:    str
    source:      str
    benchmark:   str
    fix_guidance: str
    check_pattern: str
    tags:        list[str]
    similarity:  float
    weight:      int = 15


@dataclass
class FindingGroup:
    """All rule matches for a single signal, de-duped and ranked."""
    signal:       Signal
    matches:      list[RuleMatch] = field(default_factory=list)

    @property
    def top_match(self) -> Optional[RuleMatch]:
        return self.matches[0] if self.matches else None

    @property
    def highest_severity(self) -> str:
        order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
        if not self.matches:
            return "Low"
        return max(self.matches, key=lambda m: order.get(m.severity, 0)).severity


class RuleMatcher:
    """
    Queries the vector DB for rules matching each signal extracted from an API spec.

    Usage:
        matcher = RuleMatcher(store)
        findings = matcher.match_signals(signals)
    """

    def __init__(
        self,
        store: SpecSentinelVectorStore,
        n_results_per_signal: int = 3,
        similarity_threshold: float = SIMILARITY_THRESHOLD,
    ):
        self.store     = store
        self.n_results = n_results_per_signal
        self.threshold = similarity_threshold

    def match_signal(self, signal: Signal) -> FindingGroup:
        """Query vector DB for a single signal and return matched rules."""
        results = self.store.query_rules(
            category=signal.category,
            query_text=signal.description,
            n_results=self.n_results,
        )

        matches = []
        for r in results:
            if r["similarity"] < self.threshold:
                continue
            matches.append(RuleMatch(
                signal=signal,
                rule_id=r["rule_id"],
                title=r["title"] or "",
                severity=r["severity"] or "Medium",
                category=r["category"] or signal.category,
                source=r["source"] or "",
                benchmark=r["benchmark"] or "",
                fix_guidance=r["fix_guidance"] or "",
                check_pattern=r["check_pattern"] or "",
                tags=r["tags"] or [],
                similarity=r["similarity"],
                weight=int(r.get("weight") or 15),
            ))

        return FindingGroup(signal=signal, matches=matches)

    def match_signals(self, signals: list[Signal]) -> list[FindingGroup]:
        """Match all signals using batch querying for better performance."""
        if not signals:
            return []
        
        logger.info(f"Starting batch matching for {len(signals)} signals")
        
        # Group signals by category for batch processing
        signals_by_category = {}
        for signal in signals:
            if signal.category not in signals_by_category:
                signals_by_category[signal.category] = []
            signals_by_category[signal.category].append(signal)
        
        logger.info(f"Grouped signals into {len(signals_by_category)} categories: {list(signals_by_category.keys())}")
        
        findings = []
        total_matches = 0
        
        # Process each category in batch
        for category, category_signals in signals_by_category.items():
            logger.info(f"[{category}] Batch querying {len(category_signals)} signals...")
            
            # Prepare batch query
            query_texts = [signal.description for signal in category_signals]
            
            # Execute batch query
            import time
            batch_start = time.time()
            batch_results = self.store.query_rules_batch(
                category=category,
                query_texts=query_texts,
                n_results=self.n_results,
            )
            batch_duration = time.time() - batch_start
            
            logger.info(f"[{category}] Batch query completed in {batch_duration:.3f}s")
            
            # Process results for each signal
            category_matches = 0
            for signal, results in zip(category_signals, batch_results):
                matches = []
                for r in results:
                    if r["similarity"] < self.threshold:
                        continue
                    matches.append(RuleMatch(
                        signal=signal,
                        rule_id=r["rule_id"],
                        title=r["title"] or "",
                        severity=r["severity"] or "Medium",
                        category=r["category"] or signal.category,
                        source=r["source"] or "",
                        benchmark=r["benchmark"] or "",
                        fix_guidance=r["fix_guidance"] or "",
                        check_pattern=r["check_pattern"] or "",
                        tags=r["tags"] or [],
                        similarity=r["similarity"],
                        weight=int(r.get("weight") or 15),
                    ))
                
                if matches:
                    group = FindingGroup(signal=signal, matches=matches)
                    findings.append(group)
                    category_matches += len(matches)
                    top = group.top_match
                    if top:
                        logger.debug(
                            f"Signal {signal.signal_id}: {len(group.matches)} matches, "
                            f"top={top.rule_id} ({top.similarity:.2f} similarity)"
                        )
                else:
                    logger.debug(f"Signal {signal.signal_id}: no matches above threshold")
            
            total_matches += category_matches
            logger.info(f"[{category}] Found {category_matches} total matches for {len(category_signals)} signals")

        logger.info(
            f"Batch matching complete: {len(findings)}/{len(signals)} signals matched, "
            f"{total_matches} total rule matches (threshold={self.threshold})"
        )
        return findings
    
    def match_signals_sequential(self, signals: list[Signal]) -> list[FindingGroup]:
        """Legacy sequential matching (kept for comparison/fallback)."""
        findings = []
        for signal in signals:
            group = self.match_signal(signal)
            if group.matches:
                findings.append(group)
                top = group.top_match
                if top:
                    logger.debug(
                        f"Signal {signal.signal_id}: {len(group.matches)} matches, "
                        f"top={top.rule_id} ({top.similarity:.2f} similarity)"
                    )
            else:
                logger.debug(f"Signal {signal.signal_id}: no matches above threshold")

        logger.info(
            f"Matched {len(findings)}/{len(signals)} signals to rules "
            f"(threshold={self.threshold})"
        )
        return findings
