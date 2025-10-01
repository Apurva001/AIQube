from __future__ import annotations
import threading
import time
from typing import Callable, Dict, List, Optional, Set
from .types import AgentMessage


class MessageBus:
	"""In-memory pub/sub bus with basic deduplication by correlation_id."""

	def __init__(self) -> None:
		self._subscribers: List[Callable[[AgentMessage], None]] = []
		self._lock = threading.Lock()
		self._seen: Set[str] = set()

	def subscribe(self, handler: Callable[[AgentMessage], None]) -> None:
		with self._lock:
			self._subscribers.append(handler)

	def publish(self, message: AgentMessage) -> None:
		if message.correlation_id:
			with self._lock:
				if message.correlation_id in self._seen:
					return
				self._seen.add(message.correlation_id)
		for handler in list(self._subscribers):
			handler(message)


class Blackboard:
	"""Thread-safe shared context for agents to post/find information."""

	def __init__(self) -> None:
		self._store: Dict[str, object] = {}
		self._lock = threading.Lock()

	def set(self, key: str, value: object) -> None:
		with self._lock:
			self._store[key] = value

	def get(self, key: str, default: Optional[object] = None) -> object:
		with self._lock:
			return self._store.get(key, default)

	def ensure_list(self, key: str) -> List[object]:
		with self._lock:
			lst = self._store.get(key)
			if not isinstance(lst, list):
				lst = []
				self._store[key] = lst
			return lst

	def append(self, key: str, value: object) -> None:
		with self._lock:
			lst = self._store.get(key)
			if not isinstance(lst, list):
				lst = []
				self._store[key] = lst
			lst.append(value)

