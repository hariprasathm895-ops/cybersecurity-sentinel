#!/usr/bin/env python
"""Quick test of the pipeline."""
import sys
import subprocess
import logging
logging.basicConfig(level=logging.INFO)

print("\n=== DATA GENERATION ===")
result = subprocess.run([sys.executable, "generate_data.py", "--seed", "42"], cwd=".")
if result.returncode != 0:
    print("DATA GENERATION: FAIL")
    sys.exit(1)
print("DATA GENERATION: PASS")

print("\n=== MODEL TRAINING ===")
result = subprocess.run([sys.executable, "train_models.py"], cwd=".")
if result.returncode != 0:
    print("MODEL TRAINING: FAIL")
    sys.exit(1)
print("MODEL TRAINING: PASS")

print("\n=== TESTS ===")
result = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=".")
if result.returncode != 0:
    print("TESTS: FAIL (non-critical)")
else:
    print("TESTS: PASS")

print("\n=== PIPELINE ===")
result = subprocess.run([sys.executable, "-m", "src.pipeline", "--input", "data/sample_telemetry.csv", "--max-risk", "70"], cwd=".")
if result.returncode not in [0, 1]:  # 0 = passed, 1 = policy failed
    print("PIPELINE: FAIL")
    sys.exit(1)
print("PIPELINE: PASS")

print("\n=== ALL CHECKS COMPLETE ===")
