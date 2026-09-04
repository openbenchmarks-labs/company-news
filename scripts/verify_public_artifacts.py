from pathlib import Path
import argparse

from company_news.verification import verify_run

parser = argparse.ArgumentParser()
parser.add_argument("--run-dir", type=Path, required=True)
args = parser.parse_args()
print(verify_run(args.run_dir))

