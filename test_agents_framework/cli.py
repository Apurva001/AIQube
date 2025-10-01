import typer
from rich.console import Console
from .core.comms import MessageBus, Blackboard
from .core.learning import LearningStore
from .core.risk import DeltaAnalyzer, RiskEngine
from .core.base import Tooling
from .core.types import ExecutionRequest, TestTarget
from .core.orchestrator import Orchestrator
from .agents.specialized import RegressionAgent, SanityAgent, RiskDetectorAgent, APIValidatorAgent

app = typer.Typer(help="Test Agents Framework CLI")
console = Console()


@app.command()
def version():
	"""Print version info."""
	console.print("Test Agents Framework v0.1.0")


@app.command()
def run(
	base_ref: str = typer.Option("HEAD~1", help="Base git ref for delta"),
	head_ref: str = typer.Option("HEAD", help="Head git ref for delta"),
	repo: str = typer.Option(".", help="Path to git repository"),
	db: str = typer.Option(".taf/learning.db", help="SQLite DB path"),
	api: bool = typer.Option(False, help="Include API tests"),
):
	"""Run orchestrated tests with local decision-making and learning."""
	bus = MessageBus()
	board = Blackboard()
	store = LearningStore(db)
	tooling = Tooling()
	# Delta and risk
	analyzer = DeltaAnalyzer(repo)
	delta = analyzer.compute_delta(base_ref, head_ref)
	hotspots = store.get_failure_hotspots(delta.modules_touched)
	risk_engine = RiskEngine()
	risk = risk_engine.assess(delta, hotspots)
	# Build targets (placeholder selection)
	targets = [
		TestTarget(path="tests/unit", kind="unit"),
		TestTarget(path="tests/integration", kind="integration"),
	]
	if api:
		targets.append(TestTarget(path="tests/api", kind="api"))
	request = ExecutionRequest(agent="orchestrator", targets=targets, delta=delta, risk=risk)
	# Orchestrator and agents
	orch = Orchestrator(bus, board, store, risk_engine)
	reg = RegressionAgent(tooling)
	san = SanityAgent(tooling)
	rdet = RiskDetectorAgent(tooling)
	api_agent = APIValidatorAgent(tooling)
	orch.register(reg)
	orch.register(san)
	orch.register(rdet)
	orch.register(api_agent)
	results = orch.execute(request)
	summary = {
		"total": len(results),
		"passed": sum(1 for r in results if r.success),
		"failed": sum(1 for r in results if not r.success),
	}
	console.print(summary)


if __name__ == "__main__":
	app()
