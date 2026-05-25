import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title=" Summarizer Demo", page_icon="📑", layout="wide")

def _require_keys(*pairs):
    needed = [(k, lbl, ph) for k, lbl, ph in pairs if not os.getenv(k)]
    if not needed:
        return
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔑 API Keys")
        st.caption("Used for this session only — never stored.")
        for k, lbl, ph in needed:
            val = st.text_input(lbl, type="password", placeholder=ph, key=f"_k_{k}")
            if val:
                os.environ[k] = val
    still = [lbl for k, lbl, _ in pairs if not os.getenv(k)]
    if still:
        st.info(f"👈 Enter your {' and '.join(still)} in the sidebar to run this demo.")
        st.stop()

_require_keys(("OPENAI_API_KEY", "OpenAI API Key", "sk-..."))

from utils.io import load_file, load_from_url
from summarizers import baseline, rag, map_reduce, chaining, progressive
from summarizers import extractive
from summarizers import styler
from summarizers import headlines as hl
from evaluation.storage import save_ratings_dict
from utils.chunking import token_chunks
from utils.metrics import coverage, redundancy, sentence_citations
from utils.quotes import quote_preserving

st.title(" Modular Summarizer Demo")

tab_upload, tab_url = st.tabs(["Upload TXT/PDF", "From URL (PDF or Web Page)"])

def compress_summary_to_words(text: str, target_words: int) -> str:
    try:
        return baseline.summarize(text, words=max(30, int(target_words)))
    except Exception:
        words = text.split()
        if len(words) <= target_words:
            return text
        return " ".join(words[:target_words]) + "..."

def run_pipeline(text: str, enforce_length: bool, target_words: int, key_prefix: str):
    if not text or not text.strip():
        st.warning("No text found to summarize.")
        return

    st.subheader("Preview")
    st.write((text[:1200] + "...") if len(text) > 1200 else text)

    query = st.text_input(
        "Optional: Enter a question for focused summary (blank = summarize full doc)",
        key=f"query_{key_prefix}"
    )

    st.markdown("### Run Options")
    mode = st.radio(
        "Choose selection mode",
        ["All", "Single", "Multi-select"],
        horizontal=True,
        index=0,
        key=f"mode_{key_prefix}",
    )

    METHODS = {
        "Extractive (TextRank)": lambda: extractive.summarize(text, max_sents=7),
        "Baseline": lambda: baseline.summarize(text, words=(target_words if enforce_length else 250)),
        "RAG":      lambda: rag.summarize(text, query=query.strip() or None),
        "Map-Reduce": lambda: map_reduce.summarize(text),
        "Chaining": lambda: chaining.summarize(text),
        "Progressive": lambda: progressive.summarize(text),
    }

    if mode == "All":
        selected = list(METHODS.keys())
    elif mode == "Single":
        selected = [st.selectbox("Pick one method", list(METHODS.keys()), key=f"single_sel_{key_prefix}")]
    else:
        selected = st.multiselect(
            "Pick one or more methods",
            list(METHODS.keys()),
            default=["Extractive (TextRank)", "Baseline"],
            key=f"multi_sel_{key_prefix}",
        )

    show_citations = st.checkbox(
        "Show citations & quality metrics (coverage / redundancy)",
        value=True,
        key=f"show_citations_{key_prefix}",
    )

    # --- Summary Types controls ---
    st.markdown("### Summary Types")
    query_focus = st.checkbox("Query-Focused mode (prioritize answering the question)", value=False, key=f"qfocus_{key_prefix}")
    multi_gran = st.checkbox("Multi-Granularity (50 / 150 / 300 words)", value=False, key=f"gran_{key_prefix}")
    styles = st.multiselect(
        "Styles Library",
        ["Executive brief", "Meeting minutes", "Legal (Obligations/Risks/Next steps)", "Research abstract", "PR/FAQ", "SWOT"],
        default=[],
        key=f"styles_{key_prefix}",
    )
    want_headlines = st.checkbox("Headline + Blurbs (Title, TL;DR, LinkedIn, X)", value=False, key=f"headlines_{key_prefix}")
    want_keypoints = st.checkbox("Key Points Extractor (bullets, actions, deadlines, owners)", value=False, key=f"keypoints_{key_prefix}")
    want_quotes = st.checkbox("Quote-Preserving Mode (verbatim sentences with citations)", value=False, key=f"quotes_{key_prefix}")

    run_key = f"results_{key_prefix}"
    if st.button("Run Summary", type="primary", key=f"runbtn_{key_prefix}"):
        results = {}
        with st.spinner("Running selected summarizers..."):
            for name in selected:
                try:
                    out = METHODS[name]()
                    if enforce_length and name != "Baseline" and isinstance(out, str):
                        out = compress_summary_to_words(out, target_words)
                    results[name] = out
                except Exception as e:
                    results[name] = f"❗ Error while running {name}: {e}"

        # Store results + text snapshot in session_state so UI changes don't wipe them
        st.session_state[run_key] = {
            "results": results,
            "selected": selected,
            "text": text,
        }
        st.success("Done.")

    # If we have stored results, show them
    data = st.session_state.get(run_key)
    if data and isinstance(data, dict) and "results" in data:
        results = data["results"]
        # Precompute chunks for citations/metrics once (based on current text)
        chunks = token_chunks(text, words_per_chunk=400, overlap=120) if show_citations else []

        for name in results.keys():
            st.markdown(f"### {name}")
            out = results[name]
            st.write(out)
            # Optional: Query-focused refinement
            if query_focus and isinstance(out, str) and (query or "").strip():
                try:
                    refined = styler.focus_summary(out, query.strip())
                    st.markdown("**Query-Focused:**")
                    st.write(refined)
                except Exception as e:
                    st.info(f"Focus transform unavailable: {e}")

            # Optional: Multi-Granularity views
            if multi_gran and isinstance(out, str):
                cols = st.columns(3)
                targets = [50, 150, 300]
                for c, tw in zip(cols, targets):
                    with c:
                        try:
                            if name == "Baseline":
                                mg = baseline.summarize(out, words=tw) if len(out.split())>tw else out
                            else:
                                mg = baseline.summarize(out, words=tw)
                            st.caption(f"{tw}-word version")
                            st.write(mg)
                        except Exception as e:
                            st.info(f"Granularity transform failed: {e}")

            if show_citations and isinstance(out, str) and chunks:
                try:
                    cov = coverage(out, chunks)
                    red = redundancy(out)
                    cits = sentence_citations(out, chunks)

                    c1, c2, c3 = st.columns([1,1,2])
                    with c1:
                        st.metric("Coverage (↑)", f"{cov:.2f}")
                    with c2:
                        st.metric("Redundancy (↓)", f"{red:.2f}")
                    with c3:
                        st.caption("Coverage=avg best sentence→chunk match; Redundancy=avg sentence↔sentence similarity")

                    with st.expander("Show sentence-level citations"):
                        for i, (sent, idx, score) in enumerate(cits, 1):
                            st.markdown(f"**{i}.** {sent}  \\n↳ source chunk **#{idx}** (score {score:.2f})")
                        st.markdown("---")
                        st.caption("Click below to preview chunks.")
                        for j, ch in enumerate(chunks):
                            with st.expander(f"Chunk #{j}"):
                                st.write(ch)
                except Exception as e:
                    st.info(f"Metrics/citations unavailable: {e}")

        # --- Styles Library applied to a base summary ---
        # Choose a base: Baseline if available, else first generated
        base_summary = None
        for candidate in ["Baseline"] + list(results.keys()):
            if candidate in results and isinstance(results[candidate], str) and results[candidate]:
                base_summary = results[candidate]
                break
        if styles and base_summary:
            st.markdown("## 🎨 Styled Versions")
            for s in styles:
                try:
                    styled = styler.style_summary(base_summary, s)
                    st.markdown(f"### {s}")
                    st.write(styled)
                except Exception as e:
                    st.info(f"Style '{s}' failed: {e}")

        # --- Headline + Blurbs ---
        if want_headlines:
            try:
                meta = hl.generate(text)
                print(meta)
                print(type(meta))
                st.markdown("## 🏷️ Headline & Blurbs")
                st.markdown(f"**Title:** {meta.get('title','')}")
                st.markdown(f"**TL;DR:** {meta.get('tldr','')}")
            except Exception as e:
                st.info(f"Headline/Blurbs failed: {e}")

        # --- Key Points Extractor ---
        if want_keypoints:
            try:
                from summarizers import keypoints as kp
                data = kp.extract(text)
                st.markdown("## ✅ Key Points")
                for i, kp in enumerate(data.get("key_points", [])[:10], 1):
                    st.markdown(f"**{i}.** {kp}")
                acts = data.get("actions", [])
                if acts:
                    st.markdown("### Action Items")
                    import pandas as pd
                    df = pd.DataFrame(acts, columns=["action","owner","deadline","priority"])
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.info(f"Key Points extraction failed: {e}")

        # --- Quote-Preserving Mode ---
        if want_quotes:
            try:
                cites = quote_preserving(text, query=(query.strip() if query_focus and (query or '').strip() else None), target_sents=8)
                st.markdown("## ✒️ Quote-Preserving Summary")
                for i, (sent, idx, score) in enumerate(cites, 1):
                    st.markdown(f"**{i}.** {sent}  \n↳ source chunk **#{idx}** (score {score:.2f})")
            except Exception as e:
                st.info(f"Quote-preserving mode failed: {e}")

        st.subheader("📝 Rate the outputs (1–5)")
        rating_inputs = {}
        for name in results.keys():
            rating_inputs[name] = st.slider(name, 1, 5, 3, key=f"rating_{key_prefix}_{name}")

        if st.button("Submit Ratings", key=f"ratebtn_{key_prefix}"):
            try:
                save_ratings_dict(rating_inputs, out_file="ratings.csv")
                st.success("Ratings saved ✅")
                st.caption("Saved to ratings.csv in the app working directory.")
            except Exception as e:
                st.error(f"Failed to save ratings: {e}")
    else:
        st.info("Configure options and click **Run Summary** to generate outputs.")

with tab_upload:
    uploaded = st.file_uploader("Upload TXT/PDF", type=["txt", "pdf"], key="uploader_upload")
    if uploaded:
        text = load_file(uploaded)
        run_pipeline(text, enforce_length=False, target_words=250, key_prefix="upload")
    else:
        st.info("Upload a .txt or .pdf to begin.")



with tab_url:
    url = st.text_input("Paste a public URL (PDF or HTML)", key="url_input")
    colA, colB = st.columns([1,1])
    with colA:
        st.session_state.setdefault("url_enforce", True)
        enforce = st.checkbox("Enforce max summary length", value=st.session_state["url_enforce"], key="url_enforce")
    with colB:
        st.session_state.setdefault("url_target", 200)
        target_words = st.slider("Target words", min_value=50, max_value=400, value=st.session_state["url_target"], step=25, key="url_target")

    cols = st.columns([1,1,1])
    with cols[0]:
        if st.button("Fetch URL", type="primary", key="fetch_url_btn"):
            try:
                with st.spinner("Downloading and extracting text..."):
                    text, meta = load_from_url(url)
                st.session_state["url_text"] = text
                st.session_state["url_meta"] = meta
                st.success("Fetched successfully.")
            except Exception as e:
                st.error(f"Failed to load from URL: {e}")
                st.caption("Tip: Ensure the link is public and points to a PDF or HTML page.")
    with cols[1]:
        if st.button("Clear URL content", key="clear_url_btn"):
            for k in ["url_text", "url_meta", "results_url"]:
                st.session_state.pop(k, None)
            st.success("Cleared URL content.")
    with cols[2]:
        pass

    # If we have URL text in state, show preview + pipeline
    if "url_text" in st.session_state:
        meta = st.session_state.get("url_meta", {})
        with st.expander("Downloaded details", expanded=True):
            t = meta.get("type", "?")
            size_b = meta.get("size_bytes", 0)
            size_kb = f"{size_b/1024:.1f} KB" if size_b else "?"
            st.write(f"**Type:** {t}  \\n**Size:** {size_kb}")
            if t == "pdf":
                st.write(f"**Pages:** {meta.get('pages', '?')}")
            if t == "html":
                st.write(f"**Title:** {meta.get('title', '')}")
            st.caption(f"Content-Type header: {meta.get('content_type','?')}")

        run_pipeline(st.session_state["url_text"], enforce_length=enforce, target_words=target_words, key_prefix="url")
    else:
        st.info("Paste a URL and click **Fetch URL** to begin.")
