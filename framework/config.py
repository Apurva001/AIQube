from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any
import yaml


@dataclass
class Thresholds:
	allowed_failures: int = 0
	# Reserved for future enhancements
	allowed_new_failures: int = 0


@dataclass
class SuiteConfig:
	name: str
	description: str = ""
	# File globs to include, relative to repo root
	includes: List[str] = field(default_factory=lambda: ["tests/**/*.py"])
	pytest_args: List[str] = field(default_factory=list)
	thresholds: Thresholds = field(default_factory=Thresholds)


def _expand_env_vars(data: Any) -> Any:
	if isinstance(data, dict):
		return {k: _expand_env_vars(v) for k, v in data.items()}
	if isinstance(data, list):
		return [_expand_env_vars(v) for v in data]
	if isinstance(data, str):
		return os.path.expandvars(data)
	return data


def load_suite_config(path: str) -> SuiteConfig:
	with open(path, "r", encoding="utf-8") as f:
		raw = yaml.safe_load(f) or {}
		raw = _expand_env_vars(raw)

	name = raw.get("name")
	if not name:
		# Derive from filename without extension
		name = os.path.splitext(os.path.basename(path))[0]

	thresholds_raw = raw.get("thresholds", {})
	thresholds = Thresholds(
		allowed_failures=int(thresholds_raw.get("allowed_failures", 0)),
		allowed_new_failures=int(thresholds_raw.get("allowed_new_failures", 0)),
	)

	config = SuiteConfig(
		name=name,
		description=raw.get("description", ""),
		includes=list(raw.get("includes", ["tests/**/*.py"])),
		pytest_args=list(raw.get("pytest_args", [])),
		thresholds=thresholds,
	)
	return config


def save_baseline(baseline_path: str, metrics: Dict[str, Any]) -> None:
	os.makedirs(os.path.dirname(baseline_path), exist_ok=True)
	with open(baseline_path, "w", encoding="utf-8") as f:
		json.dump(metrics, f, indent=2, sort_keys=True)


def load_baseline(baseline_path: str) -> Dict[str, Any]:
	if not os.path.exists(baseline_path):
		return {}
	with open(baseline_path, "r", encoding="utf-8") as f:
		return json.load(f)

