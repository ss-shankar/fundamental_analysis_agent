"""In-memory cache for JSON data used by the fundamental analysis agent."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from threading import RLock
from typing import Any


class Memory:
	"""Thread-safe JSON cache with a configurable time-to-live."""

	def __init__(self, expiry_hours: float = 5.0) -> None:
		if expiry_hours <= 0:
			raise ValueError("expiry_hours must be greater than zero")
		self._ttl = timedelta(hours=expiry_hours)
		self._items: dict[str, tuple[datetime, Any]] = {}
		self._lock = RLock()

	@staticmethod
	def _ensure_json(data: Any) -> None:
		try:
			json.dumps(data)
		except (TypeError, ValueError) as exc:
			raise TypeError("data must be JSON-serializable") from exc

	def set(self, key: str, data: Any) -> None:
		"""Store JSON-compatible data until its TTL expires."""
		self._ensure_json(data)
		expires_at = datetime.now(timezone.utc) + self._ttl
		with self._lock:
			self._items[key] = (expires_at, deepcopy(data))

	def get(self, key: str) -> Any | None:
		"""Return data if present and unexpired; otherwise return ``None``."""
		with self._lock:
			item = self._items.get(key)
			if item is None:
				return None
			expires_at, data = item
			if datetime.now(timezone.utc) >= expires_at:
				del self._items[key]
				return None
			return deepcopy(data)

	def delete(self, key: str) -> None:
		with self._lock:
			self._items.pop(key, None)

	def clear(self) -> None:
		with self._lock:
			self._items.clear()

	def get_balance_sheet(self, identifier: str) -> Any | None:
		return self.get(f"balance_sheet:{identifier}")

	def search_recent_news(self, identifier: str) -> Any | None:
		return self.get(f"recent_news:{identifier}")

	def compute_key_ratios(self, identifier: str) -> Any | None:
		return self.get(f"key_ratios:{identifier}")

	def store_balance_sheet(self, identifier: str, data: Any) -> None:
		self.set(f"balance_sheet:{identifier}", data)

	def store_recent_news(self, identifier: str, data: Any) -> None:
		self.set(f"recent_news:{identifier}", data)

	def store_key_ratios(self, identifier: str, data: Any) -> None:
		self.set(f"key_ratios:{identifier}", data)
