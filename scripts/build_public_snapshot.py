from pathlib import Path
import argparse

from company_news.orchestration import build_snapshot

parser = argparse.ArgumentParser()
parser.add_argument("--run-dir", type=Path, required=True)
args = parser.parse_args()
build_snapshot(args.run_dir)

