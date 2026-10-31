"""Mutable symbolic shape domain and range-dependent simplification."""
from dataclasses import dataclass, field

@dataclass
class ShapeEnvironment:
    lower: int = 1
    upper: int = 16
    _cached_prefix: dict = field(default_factory=dict)
    epoch: int = 0

    def __post_init__(self):
        self._check(self.lower, self.upper)

    @staticmethod
    def _check(lower, upper):
        if not (isinstance(lower, int) and isinstance(upper, int) and 1 <= lower <= upper):
            raise ValueError("invalid shape range")

    def rebind(self, lower: int, upper: int):
        """Install bounds for a new specialization context, possibly widening."""
        self._check(lower, upper)
        if (lower, upper) != (self.lower, self.upper):
            self.lower, self.upper = lower, upper
            self.epoch += 1
        # Derived decisions are currently reused across shape environment epochs.

    def classify_prefix(self, limit: int):
        """Return ('all', None), ('fixed', limit), or ('dynamic', None)."""
        if limit < 0:
            raise ValueError("negative prefix limit")
        if limit in self._cached_prefix:
            return self._cached_prefix[limit]
        if self.upper <= limit:
            decision = ("all", None)
        elif self.lower >= limit:
            decision = ("fixed", limit)
        else:
            decision = ("dynamic", None)
        self._cached_prefix[limit] = decision
        return decision
