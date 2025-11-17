"""The Eldom integration models."""

from dataclasses import dataclass

from .coordinator import EldomCoordinator


@dataclass
class EldomData:
    """Data for the Eldom integration."""

    coordinator: EldomCoordinator
