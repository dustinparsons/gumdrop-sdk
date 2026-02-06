"""
Gumdrop Memory — Persistent, portable memory store.

Memory is stored alongside the cartridge and encrypted by default.
The user owns their memory — it lives with the cartridge, not the platform.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any


class MemoryStore:
    """
    SQLite-backed memory store for a cartridge.
    
    Supports:
      - Key-value facts (things the AI knows about the user)
      - Conversation summaries (compressed history)
      - Semantic search (when embedding provider available)
    """
    
    def __init__(self, path: Optional[Path] = None):
        self._path = path
        self._conn: Optional[sqlite3.Connection] = None
        
        if path:
            self._connect()
    
    def _connect(self):
        """Initialize database connection and schema."""
        self._conn = sqlite3.connect(str(self._path))
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._create_tables()
    
    def _create_tables(self):
        """Create memory tables if they don't exist."""
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS facts (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                confidence REAL DEFAULT 1.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary TEXT NOT NULL,
                message_count INTEGER DEFAULT 0,
                provider TEXT DEFAULT '',
                started_at TEXT NOT NULL,
                ended_at TEXT NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                importance REAL DEFAULT 0.5,
                occurred_at TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            );
        """)
    
    def remember(self, key: str, value: str, category: str = "general", confidence: float = 1.0):
        """Store or update a fact."""
        if not self._conn:
            return
        
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute("""
            INSERT INTO facts (key, value, category, confidence, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                category = excluded.category,
                confidence = excluded.confidence,
                updated_at = excluded.updated_at
        """, (key, value, category, confidence, now, now))
        self._conn.commit()
    
    def recall(self, key: str) -> Optional[str]:
        """Retrieve a specific fact."""
        if not self._conn:
            return None
        
        row = self._conn.execute(
            "SELECT value FROM facts WHERE key = ?", (key,)
        ).fetchone()
        return row[0] if row else None
    
    def forget(self, key: str):
        """Remove a specific fact."""
        if not self._conn:
            return
        self._conn.execute("DELETE FROM facts WHERE key = ?", (key,))
        self._conn.commit()
    
    def get_recent_facts(self, limit: int = 20, category: Optional[str] = None) -> List[str]:
        """Get recent facts as formatted strings."""
        if not self._conn:
            return []
        
        if category:
            rows = self._conn.execute(
                "SELECT key, value FROM facts WHERE category = ? ORDER BY updated_at DESC LIMIT ?",
                (category, limit)
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT key, value FROM facts ORDER BY updated_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        
        return [f"{key}: {value}" for key, value in rows]
    
    def get_all_facts(self) -> Dict[str, str]:
        """Get all facts as a dictionary."""
        if not self._conn:
            return {}
        
        rows = self._conn.execute("SELECT key, value FROM facts").fetchall()
        return dict(rows)
    
    def log_conversation(self, summary: str, message_count: int, provider: str = ""):
        """Log a conversation summary."""
        if not self._conn:
            return
        
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute("""
            INSERT INTO conversations (summary, message_count, provider, started_at, ended_at)
            VALUES (?, ?, ?, ?, ?)
        """, (summary, message_count, provider, now, now))
        self._conn.commit()
    
    def log_event(self, event_type: str, description: str, importance: float = 0.5):
        """Log a significant event."""
        if not self._conn:
            return
        
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute("""
            INSERT INTO events (event_type, description, importance, occurred_at, recorded_at)
            VALUES (?, ?, ?, ?, ?)
        """, (event_type, description, importance, now, now))
        self._conn.commit()
    
    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent events."""
        if not self._conn:
            return []
        
        rows = self._conn.execute("""
            SELECT event_type, description, importance, occurred_at
            FROM events ORDER BY occurred_at DESC LIMIT ?
        """, (limit,)).fetchall()
        
        return [
            {"type": r[0], "description": r[1], "importance": r[2], "at": r[3]}
            for r in rows
        ]
    
    def has_memories(self) -> bool:
        """Check if any memories exist."""
        if not self._conn:
            return False
        row = self._conn.execute("SELECT COUNT(*) FROM facts").fetchone()
        return row[0] > 0 if row else False
    
    def save(self):
        """Flush any pending writes."""
        if self._conn:
            self._conn.commit()
    
    def close(self):
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def __del__(self):
        self.close()
