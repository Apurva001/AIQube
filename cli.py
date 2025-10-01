import sys
import pathlib
import typer
from rich.console import Console
from framework.runner import run_suite

console = Console()


def main(
	suite: str = typer.Option(..., "--suite", help="Path to suite YAML"),
	retries: int = typer.Option(0, "--retries", min=0, help="Number of reruns on failure"),
	workers: int = typer.Option(0, "--workers", min=0, help="Reserved for future parallelization"),
	auto_approve: bool = typer.Option(False, "--auto-approve", help="Bypass human approval gating"),
) -> None:
	"""Run tests defined by a suite YAML with monitoring and reporting."""
	suite_path = pathlib.Path(suite).resolve()
	if not suite_path.exists():
		console.print(f"[red]Suite not found:[/red] {suite_path}")
		sys.exit(2)

	result_code = run_suite(
		suite_path=suite_path,
		retries=retries,
		workers=workers,
		auto_approve=auto_approve,
	)
	sys.exit(result_code)


if __name__ == "__main__":
	typer.run(main)
