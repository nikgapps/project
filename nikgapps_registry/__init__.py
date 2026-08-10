"""Publish legacy NikGapps package trees to the GitLab Generic Registry."""

from .service import RegistryService, SyncRequest

__all__ = ["RegistryService", "SyncRequest"]
