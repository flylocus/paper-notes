DATE ?= $(shell date +%Y%m%d)
MODE ?= publish

.PHONY: help phase1 standardize preflight qa backfill backfill-evidence theme-index

help:
	@echo "paper-notes commands"
	@echo "  make phase1 DATE=YYYYMMDD"
	@echo "  make standardize"
	@echo "  make preflight OUT_DIR=/abs/path MODE=publish"
	@echo "  make qa OUT_DIR=/abs/path MODE=publish"
	@echo "  make backfill OUT_DIR=/abs/path"
	@echo "  make backfill-evidence DATE_FROM=YYYYMMDD DATE_TO=YYYYMMDD"
	@echo "  make theme-index MONTH=YYYYMM"

phase1:
	python3 scripts/production/daily_runner.py phase1 --date $(DATE)

standardize:
	python3 scripts/maintenance/batch_standardize_outputs.py

preflight:
	@if [ -z "$(OUT_DIR)" ]; then echo "OUT_DIR is required"; exit 1; fi
	python3 scripts/production/preflight_check.py --out-dir "$(OUT_DIR)" --mode $(MODE)

qa:
	@if [ -z "$(OUT_DIR)" ]; then echo "OUT_DIR is required"; exit 1; fi
	python3 scripts/production/qa_check.py --out-dir "$(OUT_DIR)" --mode $(MODE)

backfill:
	@if [ -z "$(OUT_DIR)" ]; then echo "OUT_DIR is required"; exit 1; fi
	python3 scripts/maintenance/backfill_output_dir.py --out-dir "$(OUT_DIR)" --run-preflight

backfill-evidence:
	python3 scripts/maintenance/backfill_evidence_ledger.py --date-from "$(DATE_FROM)" --date-to "$(DATE_TO)" --run-qa

standardize-legacy:
	python3 scripts/maintenance/standardize_legacy_outputs.py --date-from "$(DATE_FROM)" --date-to "$(DATE_TO)" --run-qa

theme-index:
	@if [ -z "$(MONTH)" ]; then echo "MONTH is required (YYYYMM)"; exit 1; fi
	python3 scripts/maintenance/build_theme_index.py --month "$(MONTH)"
