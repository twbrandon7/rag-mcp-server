"""Chunk-related constants and enums."""

from enum import Enum


class ChunkStatus(str, Enum):
    """Status of chunk processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    STORED = "stored"
    FAILED = "failed"
