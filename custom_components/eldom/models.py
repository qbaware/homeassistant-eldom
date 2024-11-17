"""The Eldom integration models."""

from dataclasses import dataclass

from eldom.client import Client as EldomClient

from .coordinator import EldomCoordinator


@dataclass
class EldomData:
    """Data for the Eldom integration."""

    api: EldomClient
    coordinator: EldomCoordinator
