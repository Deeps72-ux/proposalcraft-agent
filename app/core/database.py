import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import uuid


class ProposalDatabase:
    """Thread-safe async-ready in-memory proposal storage."""

    def __init__(self):
        self._proposals: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def save_proposal(self, proposal: Dict[str, Any], proposal_id: Optional[str] = None) -> str:
        async with self._lock:
            pid = proposal_id or proposal.get("id") or str(uuid.uuid4())
            now = datetime.now(timezone.utc).isoformat()
            
            stored = dict(proposal)
            stored["id"] = pid
            stored["created_at"] = stored.get("created_at") or now
            stored["updated_at"] = now
            self._proposals[pid] = stored
            return pid

    async def get_proposal(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            return self._proposals.get(proposal_id)

    async def update_proposal_section(
        self, proposal_id: str, section_name: str, content: Any
    ) -> Optional[Dict[str, Any]]:
        async with self._lock:
            proposal = self._proposals.get(proposal_id)
            if not proposal:
                return None
            
            if "sections" not in proposal:
                proposal["sections"] = {}
            
            proposal["sections"][section_name] = content
            proposal["updated_at"] = datetime.now(timezone.utc).isoformat()
            return proposal

    async def list_proposals(self, limit: int = 50) -> List[Dict[str, Any]]:
        async with self._lock:
            proposals = list(self._proposals.values())
            proposals.sort(key=lambda p: p.get("created_at", ""), reverse=True)
            return proposals[:limit]

    async def delete_proposal(self, proposal_id: str) -> bool:
        async with self._lock:
            if proposal_id in self._proposals:
                del self._proposals[proposal_id]
                return True
            return False


db = ProposalDatabase()
