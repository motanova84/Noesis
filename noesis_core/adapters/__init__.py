"""Adapters to native ecosystem services. Noesis never replaces the native services."""
from .qcal_bus import QCALBusAdapter
from .noesis88 import Noesis88Adapter

__all__ = ["QCALBusAdapter", "Noesis88Adapter"]
