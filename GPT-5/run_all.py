"""Master orchestrator to execute both project test suites and build compare_report.md.
Designed to be cross-platform (Windows PowerShell friendly).
"""
from __future__ import annotations
import subprocess, sys, json, time
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
REPORT_FILE = ROOT / 'compare_report.md'
TEST_DATA_PATH = ROOT / 'test_data.json'

PROJECTS = [
    {
        'name': 'ProjectA',
        'req': 'requirements.txt',
        'setup': 'setup.sh',
        'test_script': 'tests/test_original.py',
        'perf_file': 'performance/time_original.txt',
        'log_file': 'logs/log_original.txt',
    },
    {
        'name': 'ProjectB',
        'req': 'requirements_optimized.txt',
        'setup': 'setup_optimized.sh',
        'test_script': 'tests/test_refactored.py',
        'perf_file': 'performance/time_refactored.txt',
        'log_file': 'logs/log_refactored.txt',
    },
]


def _run(cmd: list[str], cwd: Path):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def ensure_venv(project: dict):
    proj_dir = ROOT / project['name']
    venv_dir = proj_dir / '.venv'
    if not venv_dir.exists():
        print(f"[set up] {project['name']}")
        _run([sys.executable, '-m', 'venv', str(venv_dir)], proj_dir)
        pip = venv_dir / ('Scripts' if sys.platform == 'win32' else 'bin') / 'pip'
        req_file = proj_dir / project['req']
        if req_file.exists():
            # Network may be restricted; attempt upgrades but continue on failure
            try:
                _run([str(pip), 'install', '--upgrade', 'pip'], proj_dir)
            except Exception as e:
                print(f"[warn] pip upgrade failed: {e}")
            try:
                _run([str(pip), 'install', '-r', str(req_file)], proj_dir)
            except Exception as e:
                print(f"[warn] dependency install failed: {e}")
    else:
        print(f"[reuse venv] {project['name']}")


def run_tests(project: dict):
    proj_dir = ROOT / project['name']
    ensure_venv(project)
    py = (proj_dir / '.venv' / ('Scripts' if sys.platform == 'win32' else 'bin') / 'python')
    start = time.perf_counter()
    res = _run([str(py), project['test_script']], proj_dir)
    elapsed = time.perf_counter() - start
    print(f"[tests done] {project['name']} elapsed={elapsed:.3f}s")
    return res


def load_perf(project: dict):
    f = ROOT / project['name'] / project['perf_file']
    if f.exists():
        return json.loads(f.read_text())
    return {}


def load_log(project: dict):
    f = ROOT / project['name'] / project['log_file']
    if f.exists():
        return json.loads(f.read_text())
    return {}


def build_report(perf_a: dict, perf_b: dict, log_a: dict, log_b: dict):
    def fmt_pct(x):
        return f"{x*100:.1f}%" if isinstance(x, (int,float)) else "n/a"
    lines = [
        "# Refactor Comparison Report",
        "", 
        "## Summary",
        "This report compares pre-refactor (ProjectA) and post-refactor (ProjectB) implementations.",
        "", "## Metrics Table", "", "| Metric | ProjectA | ProjectB | Improvement |", "|--------|----------|----------|------------|"
    ]
    def improvement(metric: str, a, b):
        if not (isinstance(a,(int,float)) and isinstance(b,(int,float)) and a!=0):
            return "n/a"
        # For accuracy metrics higher is better
        if "Accuracy" in metric:
            return f"{((b - a)/a)*100:.1f}%"  # positive means improvement
        # For time/memory lower is better
        if any(k in metric for k in ["Elapsed","Time","Memory"]):
            return f"{((a - b)/a)*100:.1f}%"  # positive means reduction
        return f"{((b - a)/a)*100:.1f}%"

    rows = [
        ("Accuracy", fmt_pct(log_a.get('accuracy')), fmt_pct(log_b.get('accuracy')), improvement("Accuracy", log_a.get('accuracy'), log_b.get('accuracy'))),
        ("Edge Accuracy", fmt_pct(log_a.get('edge_accuracy')), fmt_pct(log_b.get('edge_accuracy')), improvement("Edge Accuracy", log_a.get('edge_accuracy'), log_b.get('edge_accuracy'))),
        ("Avg Elapsed (s)", f"{perf_a.get('avg_elapsed', 'n/a')}", f"{perf_b.get('avg_elapsed', 'n/a')}", improvement("Avg Elapsed (s)", perf_a.get('avg_elapsed'), perf_b.get('avg_elapsed'))),
        ("Large Case Time (s)", f"{perf_a.get('large_case_time','n/a')}", f"{perf_b.get('large_case_time','n/a')}", improvement("Large Case Time (s)", perf_a.get('large_case_time'), perf_b.get('large_case_time'))),
        ("Peak Memory (bytes)", f"{perf_a.get('peak_memory_bytes','n/a')}", f"{perf_b.get('peak_memory_bytes','n/a')}", improvement("Peak Memory (bytes)", perf_a.get('peak_memory_bytes'), perf_b.get('peak_memory_bytes'))),
    ]
    for r in rows:
        lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |")

    lines += ["", "## Key Refactor Changes", "- Removed duplicated category counting loops", "- Single-pass aggregation reduces time complexity of core metrics", "- Excluded negative durations from totals to ensure correctness", "- Iterative stack traversal avoids deep recursion and excessive list concatenations", "- Introduced dataclass for clarity and type hints for maintainability", "- Optional fast JSON parsing with orjson (used when available).", "", "## Edge Case Handling", "- Negative durations counted but excluded from averages and totals", "- Invalid input (non-list) reported without crashing", "- Deeply nested subtasks counted accurately with depth tracking", "", "## Potential Pitfalls", "- Extremely large nested structures may still increase memory usage due to Task object creation", "- orjson is optional; absence slightly reduces parsing performance", "- Validation cost grows linearly; can be skipped with validate=False for trusted data", "", "## Recommendations", "- Consider streaming for very large inputs", "- Add type-enforced schema validation if data sources are unreliable", "- Extend metrics to include median duration and category duration distributions", ""]
    REPORT_FILE.write_text("\n".join(lines))


def main():
    perf_data = {}
    log_data = {}
    for p in PROJECTS:
        run_tests(p)
        perf_data[p['name']] = load_perf(p)
        log_data[p['name']] = load_log(p)
    build_report(perf_data['ProjectA'], perf_data['ProjectB'], log_data['ProjectA'], log_data['ProjectB'])
    print(f"Report written: {REPORT_FILE}")

if __name__ == '__main__':
    main()
