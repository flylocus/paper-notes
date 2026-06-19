DATE ?= $(shell date +%Y%m%d)
MODE ?= publish

.PHONY: help phase1 deepseek-candidates deepseek-payload deepseek-review standardize preflight qa backfill backfill-evidence theme-index

help:
	@echo "paper-notes commands"
	@echo "  make phase1 DATE=YYYYMMDD"
	@echo "  make deepseek-candidates DATE=YYYYMMDD"
	@echo "  make deepseek-payload DATE=YYYYMMDD ARXIV_ID=2606.xxxxx"
	@echo "  make deepseek-review DATE=YYYYMMDD OUT_DIR=/abs/path"
	@echo "  make standardize"
	@echo "  make preflight OUT_DIR=/abs/path MODE=publish"
	@echo "  make qa OUT_DIR=/abs/path MODE=publish"
	@echo "  make backfill OUT_DIR=/abs/path"
	@echo "  make backfill-evidence DATE_FROM=YYYYMMDD DATE_TO=YYYYMMDD"
	@echo "  make theme-index MONTH=YYYYMM"

phase1:
	python3 scripts/production/daily_runner.py phase1 --date $(DATE)

deepseek-candidates:
	python3 scripts/production/deepseek_paper_notes.py enrich-candidates --date $(DATE)

deepseek-payload:
	@if [ -z "$(ARXIV_ID)" ]; then echo "ARXIV_ID is required"; exit 1; fi
	python3 scripts/production/deepseek_paper_notes.py draft-payload --date $(DATE) --arxiv-id "$(ARXIV_ID)" --metadata "fused/$(ARXIV_ID)_metadata.json" --score "fused/$(ARXIV_ID)_score.json"

deepseek-review:
	@if [ -z "$(OUT_DIR)" ]; then echo "OUT_DIR is required"; exit 1; fi
	python3 scripts/production/deepseek_paper_notes.py review-output --date $(DATE) --out-dir "$(OUT_DIR)"

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
