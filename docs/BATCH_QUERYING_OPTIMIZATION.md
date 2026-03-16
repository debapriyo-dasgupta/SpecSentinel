# Batch Querying Optimization

## Overview

The Match pipeline has been optimized with batch querying by category, resulting in **3-6x performance improvement** for typical API specifications.

## Implementation

### Changes Made

1. **ChromaDB Client** (`src/vectordb/store/chroma_client.py`)
   - Added `query_rules_batch()` method for batch vector queries
   - Processes multiple query texts in a single ChromaDB call
   - Returns results grouped by query

2. **Rule Matcher** (`src/engine/rule_matcher.py`)
   - Modified `match_signals()` to group signals by category
   - Batch queries all signals in each category together
   - Maintains backward compatibility with `match_signals_sequential()`

### How It Works

```python
# Before (Sequential)
for signal in signals:
    results = store.query_rules(category, query_text, n_results)
    # Process results...

# After (Batch)
signals_by_category = group_by_category(signals)
for category, category_signals in signals_by_category.items():
    batch_results = store.query_rules_batch(
        category=category,
        query_texts=[s.description for s in category_signals],
        n_results=n_results
    )
    # Process all results at once...
```

## Performance Results

### Test Results (from `test_batch_querying_large.py`)

| Signals | Batch Time | Sequential Time | Speedup | Improvement |
|---------|-----------|-----------------|---------|-------------|
| 10      | 0.873s    | 2.988s          | 3.42x   | 70.8%       |
| 25      | 2.176s    | 7.428s          | 3.41x   | 70.7%       |
| 50      | 2.312s    | 13.932s         | 6.03x   | 83.4%       |

### Key Findings

- **Small datasets (<10 signals)**: Minimal overhead, still faster
- **Medium datasets (10-25 signals)**: 3-4x performance improvement
- **Large datasets (50+ signals)**: 6x+ performance improvement
- **Scalability**: Performance improvement increases with dataset size

## Usage

The batch querying is now the default behavior in `RuleMatcher.match_signals()`:

```python
from src.engine.rule_matcher import RuleMatcher
from src.vectordb.store.chroma_client import SpecSentinelVectorStore

store = SpecSentinelVectorStore()
store.initialize()

matcher = RuleMatcher(store, n_results_per_signal=3)
findings = matcher.match_signals(signals)  # Uses batch querying automatically
```

### Fallback to Sequential

If needed, the sequential method is still available:

```python
findings = matcher.match_signals_sequential(signals)  # Legacy method
```

## Benefits

1. **Faster Analysis**: 3-6x reduction in Match stage duration
2. **Better Scalability**: Performance improves with larger specs
3. **Reduced API Calls**: Fewer round trips to ChromaDB
4. **Lower Latency**: Batch processing reduces overhead
5. **Same Results**: Produces identical findings as sequential method

## Technical Details

### Grouping Strategy

Signals are grouped by category before querying:
- `security` signals → Query security collection once
- `design` signals → Query design collection once
- `error_handling` signals → Query error_handling collection once
- `documentation` signals → Query documentation collection once
- `governance` signals → Query governance collection once

### ChromaDB Batch Query

ChromaDB's native batch query support:
```python
results = collection.query(
    query_texts=["query1", "query2", "query3"],  # Multiple queries
    n_results=3
)
# Returns results for all queries in one call
```

### Memory Efficiency

- Processes one category at a time
- Doesn't load all results into memory at once
- Suitable for large specifications (100+ signals)

## Testing

Run the performance tests:

```bash
# Basic test (5 signals)
python test_batch_querying.py

# Large dataset test (10, 25, 50 signals)
python test_batch_querying_large.py
```

## Future Optimizations

Potential further improvements:

1. **Parallel Category Processing**: Process multiple categories concurrently
2. **Query Caching**: Cache results for identical queries
3. **Adaptive Batching**: Adjust batch size based on signal count
4. **Async/Await**: Convert to async for better concurrency

## Monitoring

Track Match stage performance in logs:

```
INFO: Matched 46/50 signals to rules (threshold=0.35) using batch queries
```

The "using batch queries" message confirms the optimization is active.

## Backward Compatibility

- Existing code continues to work without changes
- API remains the same
- Results are identical to sequential method
- No breaking changes

## Conclusion

Batch querying by category provides significant performance improvements for the Match pipeline with no downsides. The optimization is transparent to users and maintains full backward compatibility.