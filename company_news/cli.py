from __future__ import annotations

import argparse
from pathlib import Path

from .orchestration import build_snapshot, evaluate_run, run_benchmark
from .providers import all_adapters
from .verification import verify_run


def _endpoints(value: str | None) -> list[str] | None:
    return [item.strip() for item in value.split(",") if item.strip()] if value else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="company-news", description="OpenBenchmarks Company News runner")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("list-providers", help="List endpoint names, surfaces and documentation")
    run = commands.add_parser("run", help="Run fresh vendor calls and evaluation")
    run.add_argument("--dataset", type=Path, required=True)
    run.add_argument("--output", type=Path)
    run.add_argument("--endpoints", help="Comma-separated endpoint names; default is the published roster")
    run.add_argument("--limit", type=int, default=0)
    run.add_argument("--search-only", action="store_true")
    run.add_argument("--resume", action="store_true")

    evaluate = commands.add_parser("evaluate", help="Evaluate search-only cells without vendor calls")
    evaluate.add_argument("--run-dir", type=Path, required=True)
    evaluate.add_argument("--workers", type=int, default=4)
    snapshot = commands.add_parser("build-snapshot", help="Rebuild run.json and its manifest")
    snapshot.add_argument("--run-dir", type=Path, required=True)
    verify = commands.add_parser("verify", help="Verify counts, hashes and credential redaction")
    verify.add_argument("--run-dir", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == "list-providers":
        for adapter in all_adapters().values():
            print(f"{adapter.name}\t{adapter.surface}\t{adapter.docs_url}")
    elif args.command == "run":
        output = run_benchmark(args.dataset, args.output, endpoints=_endpoints(args.endpoints),
                               limit=args.limit, search_only=args.search_only, resume=args.resume)
        print(output)
    elif args.command == "evaluate":
        evaluate_run(args.run_dir, workers=args.workers)
    elif args.command == "build-snapshot":
        build_snapshot(args.run_dir)
    elif args.command == "verify":
        print(verify_run(args.run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
