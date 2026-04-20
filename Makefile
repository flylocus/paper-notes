DATE ?= $(shell date +%Y%m%d)
MODE ?= publish

.PHONY: help phase1 standardize preflight backfill

help:
	@echo "paper-notes commands"
	@echo "  make phase1 DATE=YYYYMMDD"
	@echo "  make standardize"
	@echo "  make preflight OUT_DIR=/abs/path MODE=publish"
	@echo "  make backfill OUT_DIR=/abs/path"

phase1:
	python3 scripts/production/daily_runner.py phase1 --date $(DATE)

standardize:
	python3 scripts/maintenance/batch_standardize_outputs.py

preflight:
	@if [ -z "$(OUT_DIR)" ]; then echo "OUT_DIR is required"; exit 1; fi
	python3 scripts/production/preflight_check.py --out-dir "$(OUT_DIR)" --mode $(MODE)

backfill:
	@if [ -z "$(OUT_DIR)" ]; then echo "OUT_DIR is required"; exit 1; fi
	python3 scripts/maintenance/backfill_output_dir.py --out-dir "$(OUT_DIR)" --run-preflight
