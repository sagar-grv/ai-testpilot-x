"""Page 08 — Knowledge Base: browse, search, and ingest into ChromaDB."""

import streamlit as st
import tempfile
from pathlib import Path

st.set_page_config(
    page_title="Knowledge Base | AI TestPilot X", page_icon="📚", layout="wide"
)

# ── Inject shared CSS + sidebar ───────────────────────────────────────────────
from pages._css import inject_css, sidebar_branding

inject_css()
sidebar_branding()


st.markdown(
    """
<h1 class="tp-page-title">📚 Knowledge Base</h1>
<p class="tp-page-subtitle">Search, browse, and ingest documents into the ChromaDB RAG vector store.</p>
""",
    unsafe_allow_html=True,
)
st.divider()

try:
    from core.rag_engine import rag_engine

    rag_available = True
except Exception as e:
    st.warning(f"RAG engine unavailable: {e}")
    rag_available = False

if not rag_available:
    st.stop()

# Stats
st.markdown(
    '<div class="tp-section-title">Index Statistics</div>', unsafe_allow_html=True
)
col1, col2, col3, col4 = st.columns(4)
try:
    col1.metric("🧪 Test Cases", rag_engine.count("testcases"))
    col2.metric("🐛 Bugs", rag_engine.count("bugs"))
    col3.metric("📋 Requirements", rag_engine.count("requirements"))
    col4.metric("📊 Reports", rag_engine.count("reports"))
except Exception as e:
    st.warning(f"Could not load stats: {e}")
    col3.metric("Requirements", rag_engine.count("requirements"))
    col4.metric("Reports", rag_engine.count("reports"))
except Exception as e:
    st.warning(f"Could not load stats: {e}")

st.divider()

# ── Search ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tp-section-title">Semantic Search</div>', unsafe_allow_html=True
)

sc1, sc2 = st.columns([3, 1])
with sc1:
    query = st.text_input(
        "Search query",
        placeholder="e.g. login authentication failure, checkout bug",
        label_visibility="collapsed",
    )
with sc2:
    collection = st.selectbox(
        "Collection",
        ["testcases", "bugs", "requirements", "reports"],
        label_visibility="collapsed",
    )

if query:
    with st.spinner("Searching ChromaDB..."):
        results = rag_engine.query(collection, query, n=10)
    if results:
        st.markdown(
            f"""
        <div style="font-size:13px; color:#64748B; margin-bottom:10px;">
            Found <strong style="color:#6C63FF;">{len(results)}</strong> results in
            <code style="background:#1E2337; padding:1px 6px; border-radius:4px;">{collection}</code>
        </div>""",
            unsafe_allow_html=True,
        )
        for r in results:
            sim = max(0.0, 1.0 - float(r.get("distance", 0.5)))
            sim_color = (
                "#22c55e" if sim > 0.7 else "#f59e0b" if sim > 0.4 else "#64748B"
            )
            with st.expander(f"{r.get('id', 'unknown')} · {sim:.0%} match"):
                st.markdown(
                    f"""
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
                    <div style="flex:1; height:4px; background:#1E2337; border-radius:2px;">
                        <div style="width:{sim*100:.0f}%; height:100%;
                                    background:{sim_color}; border-radius:2px;"></div>
                    </div>
                    <span style="color:{sim_color}; font-size:11px; font-weight:700;">
                        {sim:.0%}</span>
                </div>""",
                    unsafe_allow_html=True,
                )
                st.write(r.get("text", "")[:300])
                if r.get("metadata"):
                    st.json(r["metadata"])
    else:
        st.info(
            "No results found. Try a different query or ingest some documents first."
        )

st.divider()

# ── Ingestion ─────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tp-section-title">Ingest Documents</div>', unsafe_allow_html=True
)

uploaded_files = st.file_uploader(
    "Upload documents",
    type=["txt", "pdf", "docx", "md"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)
i1, i2 = st.columns([2, 1])
with i1:
    target_collection = st.selectbox(
        "Target Collection",
        ["requirements", "testcases", "bugs", "reports"],
        key="ingest_col",
    )
with i2:
    st.markdown("<br>", unsafe_allow_html=True)
    ingest_btn = st.button(
        "⬆ Ingest",
        type="primary",
        disabled=not uploaded_files,
        use_container_width=True,
    )

if ingest_btn and uploaded_files:
    prog = st.progress(0, text="Ingesting documents...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            for f in uploaded_files:
                Path(tmpdir, f.name).write_bytes(f.read())
            count = rag_engine.ingest_knowledge_dir(target_collection, tmpdir)
        prog.empty()
        st.success(f"✅ Ingested {count} chunks into '{target_collection}'")
        st.rerun()
    except Exception as e:
        prog.empty()
        st.error(f"Ingestion failed: {e}")

st.divider()

# Browse recent items
st.subheader("Browse Recent Items")
browse_collection = st.selectbox(
    "Browse Collection",
    ["testcases", "bugs", "requirements", "reports"],
    key="browse_col",
)
if st.button("Browse"):
    items = rag_engine.query(browse_collection, "test", n=20)
    if items:
        for item in items:
            with st.expander(item.get("id", "unknown")):
                st.write(item.get("text", "")[:200])
    else:
        st.info(f"No items in '{browse_collection}' yet.")
