"""Test harness for refactored implementation.
Mirrors original tests for apples-to-apples comparison.
"""
from __future__ import annotations
import json, time, tracemalloc, os, statistics
from typing import Any, Dict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / 'src'))

from refactored_code import compute_statistics  # type: ignore

TEST_DATA_PATH = ROOT / 'test_data.json'
LOG_DIR = PROJECT_ROOT / 'logs'
PERF_DIR = PROJECT_ROOT / 'performance'
LOG_FILE = LOG_DIR / 'log_refactored.txt'
TIME_FILE = PERF_DIR / 'time_refactored.txt'

for d in (LOG_DIR, PERF_DIR):
    d.mkdir(parents=True, exist_ok=True)


def _generate_large(gen: Dict[str, Any]):
    repeat = int(gen.get('repeat', 0))
    base = gen.get('base', {})
    data = [dict(base) for _ in range(repeat)]
    for i in range(0, repeat, max(1, repeat // 10)):
        data[i]['duration'] = (i % 5) + 1
    # Provide JSON string to leverage orjson acceleration if available
    import json as _json
    return _json.dumps(data)


def run_tests():
    raw = json.loads(TEST_DATA_PATH.read_text())
    cases = raw['cases']
    results = []
    durations = []
    tracemalloc.start()
    large_case_time = None
    for case in cases:
        cid = case['id']
        mode = case['input_mode']
        expected = case['expected']
        if mode == 'list':
            input_obj = case['input']
        elif mode == 'raw':
            input_obj = case['input']
        elif mode == 'generate':
            input_obj = _generate_large(case['generation'])
        else:
            input_obj = case['input']
        start = time.perf_counter()
        stats = compute_statistics(input_obj)
        end = time.perf_counter()
        elapsed = end - start
        durations.append(elapsed)
        if cid == 'large':
            large_case_time = elapsed
        comparisons = {}
        pass_case = True
        for k, v in expected.items():
            if k not in stats:
                pass_case = False
                comparisons[k] = (v, None)
            else:
                actual = stats[k]
                comparisons[k] = (v, actual)
                if isinstance(v, float) and isinstance(actual, float):
                    if abs(v - actual) > 1e-6:
                        pass_case = False
                else:
                    if v != actual:
                        pass_case = False
        results.append({
            'id': cid,
            'pass': pass_case,
            'elapsed': elapsed,
            'comparisons': comparisons,
            'stats': stats,
        })
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    passes = sum(1 for r in results if r['pass'])
    total = len(results)
    accuracy = passes / total if total else 0
    edge_cases = [r for r in results if r['id'] in {'nested','negative','invalid','large'}]
    edge_passes = sum(1 for r in edge_cases if r['pass'])
    edge_accuracy = edge_passes / len(edge_cases) if edge_cases else 0

    summary = {
        'accuracy': accuracy,
        'total_cases': total,
        'passes': passes,
        'edge_accuracy': edge_accuracy,
        'edge_passes': edge_passes,
        'peak_memory_bytes': peak,
        'avg_elapsed': statistics.mean(durations),
        'p95_elapsed': statistics.quantiles(durations, n=20)[-1] if len(durations) > 1 else durations[0],
        'large_case_time': large_case_time,
        'results': results,
    }

    LOG_FILE.write_text(json.dumps(summary, indent=2))
    TIME_FILE.write_text(json.dumps({
        'avg_elapsed': summary['avg_elapsed'],
        'large_case_time': summary['large_case_time'],
        'peak_memory_bytes': summary['peak_memory_bytes'],
        'accuracy': summary['accuracy'],
        'edge_accuracy': summary['edge_accuracy']
    }, indent=2))
    return summary


if __name__ == '__main__':
    s = run_tests()
    print(json.dumps({'accuracy': s['accuracy'], 'edge_accuracy': s['edge_accuracy']}, indent=2))
