"""ChromaDB-backed RAG engine."""

from __future__ import annotations
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from config import settings
from monitoring.logger import get_logger

log = get_logger(__name__)
_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
_COLLECTIONS = ["testcases", "bugs", "requirements", "reports"]


class RAGEngine:
    def __init__(self, path: str | None = "auto"):
        if path is None:
            self._client = chromadb.EphemeralClient()
        else:
            chroma_path = settings.CHROMA_PATH if path == "auto" else path
            self._client = chromadb.PersistentClient(path=chroma_path)
        self._ef = SentenceTransformerEmbeddingFunction(model_name=_EMBEDDING_MODEL)
        for name in _COLLECTIONS:
            self._client.get_or_create_collection(
                name=name, embedding_function=self._ef
            )
        log.info(f"RAGEngine initialized | collections={_COLLECTIONS}")

    def list_collections(self) -> list[str]:
        return [c.name for c in self._client.list_collections()]

    def upsert(
        self, collection: str, doc_id: str, text: str, metadata: dict | None = None
    ) -> None:
        col = self._client.get_collection(collection, embedding_function=self._ef)
        col.upsert(documents=[text], ids=[doc_id], metadatas=[metadata or {}])
        log.debug(f"RAG upsert | collection={collection} | id={doc_id}")

    def query(
        self, collection: str, query_text: str, n: int | None = None
    ) -> list[dict]:
        n = n or settings.RAG_TOP_K
        try:
            col = self._client.get_collection(collection, embedding_function=self._ef)
            results = col.query(query_texts=[query_text], n_results=n)
            out = []
            for i, doc_id in enumerate(results["ids"][0]):
                out.append(
                    {
                        "id": doc_id,
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                    }
                )
            return out
        except Exception as e:
            log.warning(f"RAG query failed | collection={collection} | {e}")
            return []

    def delete(self, collection: str, doc_id: str) -> None:
        col = self._client.get_collection(collection, embedding_function=self._ef)
        col.delete(ids=[doc_id])

    def count(self, collection: str) -> int:
        try:
            col = self._client.get_collection(collection, embedding_function=self._ef)
            return col.count()
        except Exception:
            return 0

    def ingest_knowledge_dir(self, collection: str, dir_path) -> int:
        from pathlib import Path

        dir_path = Path(dir_path)
        count = 0
        for fpath in dir_path.rglob("*"):
            if fpath.suffix not in {".txt", ".pdf", ".docx", ".md"}:
                continue
            text = self._read_file(fpath)
            if not text:
                continue
            chunks = self._chunk_text(text, chunk_size=512, overlap=50)
            for i, chunk in enumerate(chunks):
                doc_id = f"{fpath.stem}-chunk-{i}"
                self.upsert(
                    collection, doc_id, chunk, {"source": str(fpath), "chunk": i}
                )
                count += 1
        return count

    def _read_file(self, path) -> str:
        from pathlib import Path

        path = Path(path)
        if path.suffix in (".txt", ".md"):
            return path.read_text(encoding="utf-8", errors="ignore")
        elif path.suffix == ".pdf":
            try:
                from pypdf import PdfReader

                reader = PdfReader(str(path))
                return " ".join(p.extract_text() or "" for p in reader.pages)
            except Exception:
                return ""
        elif path.suffix == ".docx":
            try:
                from docx import Document

                doc = Document(str(path))
                return " ".join(p.text for p in doc.paragraphs)
            except Exception:
                return ""
        return ""

    def _chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> list:
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunks.append(" ".join(words[start:end]))
            start += chunk_size - overlap
        return chunks


rag_engine = RAGEngine(path="auto")
