from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from fastapi import APIRouter

from app.schemas.commerce import RagQuery

router = APIRouter(prefix="/rag", tags=["rag"])

POLICY_DIR = Path(__file__).resolve().parents[3] / "rag-policy-assistant" / "sample_policies"


def _chunks() -> List[Dict[str, str]]:
    chunks = []
    if not POLICY_DIR.exists():
        return chunks
    for path in sorted(POLICY_DIR.glob("*.md")):
        paragraphs = [p.strip() for p in path.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for index, text in enumerate(paragraphs):
            chunks.append({"source": path.name, "chunk_id": f"{path.stem}-{index}", "text": text})
    return chunks


def _score(query: str, text: str) -> int:
    q = set(query.lower().replace("?", "").split())
    t = set(text.lower().replace("?", "").replace(",", "").split())
    return len(q & t)


@router.post("/query")
def query(request: RagQuery):
    ranked = sorted(_chunks(), key=lambda chunk: _score(request.query, chunk["text"]), reverse=True)[:3]
    supported = ranked and _score(request.query, ranked[0]["text"]) > 0
    if not supported:
        return {"answer": "I do not have enough policy context.", "citations": [], "retrieved_chunks": ranked}
    answer = ranked[0]["text"].split("\n")[-1]
    return {"answer": answer, "citations": [{"source": c["source"], "chunk_id": c["chunk_id"]} for c in ranked if _score(request.query, c["text"]) > 0], "retrieved_chunks": ranked}
