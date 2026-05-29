"""Page 08 — Knowledge Base: browse, search, and ingest into ChromaDB."""
import streamlit as st
import tempfile
from pathlib import Path

st.set_page_config(page_title="Knowledge Base | AI TestPilot X", layout="wide")
st.title("Knowledge Base")

from core.rag_engine import rag_engine

# Stats
col1, col2, col3, col4 = st.columns(4)
try:
    col1.metric("Test Cases", rag_engine.count("testcases"))
    col2.metric("Bugs", rag_engine.count("bugs"))
    col3.metric("Requirements", rag_engine.count("requirements"))
    col4.metric("Reports", rag_engine.count("reports"))
except Exception as e:
    st.warning(f"Could not load stats: {e}")

st.divider()

# Search
st.subheader("Search Knowledge Base")
search_col1, search_col2 = st.columns([3, 1])
with search_col1:
    query = st.text_input("Search query", placeholder="e.g. login authentication failure")
with search_col2:
    collection = st.selectbox("Collection", ["testcases", "bugs", "requirements", "reports"])

if query:
    with st.spinner("Searching..."):
        results = rag_engine.query(collection, query, n=10)
    if results:
        st.markdown(f"**{len(results)} results** in `{collection}`:")
        for r in results:
            similarity = 1.0 - float(r.get("distance", 0.5))
            with st.expander(f"{r.get('id', 'unknown')} — Similarity: {similarity:.0%}"):
                st.write(r.get("text", "")[:300])
                if r.get("metadata"):
                    st.json(r["metadata"])
    else:
        st.info("No results found. Try a different query or ingest some documents first.")

st.divider()

# Ingestion
st.subheader("Ingest Documents")
uploaded_files = st.file_uploader(
    "Upload documents to knowledge base",
    type=["txt", "pdf", "docx", "md"],
    accept_multiple_files=True
)
target_collection = st.selectbox("Target Collection", ["requirements", "testcases", "bugs", "reports"], key="ingest_col")

if uploaded_files and st.button("Ingest Documents", type="primary"):
    with st.spinner(f"Ingesting {len(uploaded_files)} file(s) into '{target_collection}'..."):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                for f in uploaded_files:
                    fpath = Path(tmpdir) / f.name
                    fpath.write_bytes(f.read())
                count = rag_engine.ingest_knowledge_dir(target_collection, tmpdir)
            st.success(f"Ingested {count} chunks into '{target_collection}'")
            st.rerun()
        except Exception as e:
            st.error(f"Ingestion failed: {e}")

st.divider()

# Browse recent items
st.subheader("Browse Recent Items")
browse_collection = st.selectbox("Browse Collection", ["testcases", "bugs", "requirements", "reports"], key="browse_col")
if st.button("Browse"):
    items = rag_engine.query(browse_collection, "test", n=20)
    if items:
        for item in items:
            with st.expander(item.get("id", "unknown")):
                st.write(item.get("text", "")[:200])
    else:
        st.info(f"No items in '{browse_collection}' yet.")
