"""
Test script to verify logging system is working
Run this to generate sample logs
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.logging_config import (
    get_logger,
    StructuredLogger,
    PipelineLogger,
    AgentLogger,
    log_performance,
    log_execution_time
)
import time

print("=" * 70)
print("SpecSentinel Logging System Test")
print("=" * 70)
print()

# Test 1: Basic Logger
print("1. Testing basic logger...")
logger = get_logger("specsentinel.test")
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
print("   [OK] Basic logging complete")
print()

# Test 2: Structured Logger
print("2. Testing structured logger...")
struct_logger = StructuredLogger("specsentinel.test.structured")
struct_logger.info(
    "User action",
    user_id=123,
    action="upload",
    file_name="test.yaml",
    file_size=1024
)
struct_logger.warning(
    "Rate limit approaching",
    user_id=123,
    requests_count=95,
    limit=100
)
print("   [OK] Structured logging complete")
print()

# Test 3: Pipeline Logger
print("3. Testing pipeline logger...")
pipeline = PipelineLogger("specsentinel.test.pipeline")
pipeline.start_stage("ANALYZE", spec_name="test.yaml")
time.sleep(0.5)
pipeline.end_stage("ANALYZE", signals_count=42)

pipeline.start_stage("MATCH", signals_count=42)
time.sleep(0.3)
pipeline.end_stage("MATCH", findings_count=15)

pipeline.start_stage("SCORE", findings_count=15)
time.sleep(0.2)
pipeline.end_stage("SCORE", health_score=75.5, band="Good")
print("   [OK] Pipeline logging complete")
print()

# Test 4: Agent Logger
print("4. Testing agent logger...")
agent_logger = AgentLogger("TestAgent")
agent_logger.log_analysis_start("test.yaml", category="security")
time.sleep(0.4)
agent_logger.log_analysis_complete(
    findings_count=5,
    duration=0.4,
    risk_level="MEDIUM"
)
agent_logger.log_llm_call(model="gpt-4o-mini", tokens=1500, cost=0.002)
print("   [OK] Agent logging complete")
print()

# Test 5: Performance Logging
print("5. Testing performance logging...")

@log_performance()
def slow_function():
    """Simulated slow operation"""
    time.sleep(0.5)
    return "completed"

result = slow_function()
print("   [OK] Performance logging complete")
print()

# Test 6: Context Manager
print("6. Testing execution time logging...")
with log_execution_time("database query", logger):
    time.sleep(0.3)
print("   [OK] Execution time logging complete")
print()

# Test 7: Exception Logging
print("7. Testing exception logging...")
try:
    raise ValueError("This is a test exception")
except Exception as e:
    logger.exception("Caught test exception", extra={"extra_data": {"test": True}})
print("   [OK] Exception logging complete")
print()

# Summary
print("=" * 70)
print("[SUCCESS] All logging tests completed successfully!")
print("=" * 70)
print()
print("Log files created in: logs/")
print()
print("View logs with:")
print("  Get-Content logs\\specsentinel.test.log -Wait")
print()
print("Or check all log files:")
print("  Get-ChildItem logs\\*.log")
print()

# Made with Bob
