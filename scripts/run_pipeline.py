import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_step(script_name):
    script = ROOT / "scripts" / script_name
    print(f"\n==> Running {script_name}")
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)


def main():
    steps = [
        "paper_scanner.py",
        "crossref_scanner.py",
        "paper_normalizer.py",
        "paper_screener.py",
        "tag_assigner.py",
        "daily_digest.py",
        "query_quality_report.py",
    ]
    for step in steps:
        run_step(step)
    print("\nPipeline completed.")


if __name__ == "__main__":
    main()
