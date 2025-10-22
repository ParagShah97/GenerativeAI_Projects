import io
import pandas as pd
import streamlit as st

def render_files_card(files: list[dict]):
    q = st.text_input("Search files", placeholder="type to filter…")
    if q:
        ql = q.lower()
        files = [
            f for f in files
            if any(ql in (f.get(k, "") or "").lower()
                   for k in ("file_name", "file_content", "file_summary"))
        ]
    if not files:
        st.info("No files match your search.")
        return

    for i, f in enumerate(files, start=1):
        name = f.get("file_name") or f"file_{i}.txt"
        summ = f.get("file_summary") or ""
        code = f.get("file_content") or ""

        with st.expander(f"📄 {name}", expanded=False):
            t1, t2, t3 = st.tabs(["📝 Summary", "💻 Content", "⬇️ Download"])
            with t1:
                st.write(summ or "_No summary_")
            with t2:
                lang = "markdown" if name.lower().endswith(".md") else ""
                st.code(code, language=lang)
            with t3:
                st.download_button(
                    "Download file",
                    data=io.BytesIO(code.encode("utf-8")),
                    file_name=name,
                    mime="text/plain",
                    use_container_width=True,
                )

def _preview(text: str | None, n: int = 140) -> str:
    if not text:
        return ""
    text = text.replace("\n", " ")
    return text[:n] + ("…" if len(text) > n else "")

def render_files_table(files: list[dict]):
    if not files:
        st.info("No files found for this project.")
        return

    df = pd.DataFrame([
        {
            "file_name": f.get("file_name"),
            "summary_preview": _preview(f.get("file_summary")),
            "content_preview": _preview(f.get("file_content")),
            "file_summary": f.get("file_summary"),
            "file_content": f.get("file_content"),
        }
        for f in files
    ])

    st.dataframe(
        df[["file_name", "summary_preview", "content_preview"]],
        use_container_width=True,
        hide_index=True,
    )

    if len(df):
        idx = st.selectbox(
            "Open a file",
            options=list(range(len(df))),
            format_func=lambda i: df.iloc[i]["file_name"],
        )
        with st.expander(f"View: {df.iloc[idx]['file_name']}", expanded=True):
            t1, t2, t3 = st.tabs(["📝 Summary", "💻 Content", "⬇️ Download"])
            with t1:
                st.write(df.iloc[idx]["file_summary"] or "_No summary_")
            with t2:
                st.code(df.iloc[idx]["file_content"] or "", language="")
            with t3:
                st.download_button(
                    "Download file",
                    data=io.BytesIO((df.iloc[idx]["file_content"] or "").encode("utf-8")),
                    file_name=df.iloc[idx]["file_name"] or "file.txt",
                    mime="text/plain",
                    use_container_width=True,
                )