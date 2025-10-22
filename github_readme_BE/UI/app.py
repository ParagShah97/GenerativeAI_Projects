# streamlit_app.py
import os
import io
import requests
import streamlit as st
from typing import Optional, List, Dict
from helper import render_files_card, render_files_table

# -----------------------------
# Config
# -----------------------------
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")  # your FastAPI root

TIMEOUT = 120  # seconds

# -----------------------------
# Small HTTP helpers
# -----------------------------
def _url(path: str) -> str:
    return f"{API_BASE.rstrip('/')}/{path.lstrip('/')}"

def post_json(path: str, payload: dict) -> requests.Response:
    return requests.post(_url(path), json=payload, timeout=TIMEOUT)

def get_json(path: str) -> requests.Response:
    return requests.get(_url(path), timeout=TIMEOUT)

# -----------------------------
# API wrappers (adjust if your BE differs)
# -----------------------------
def api_create_project(project_name: str, git_url: Optional[str]) -> dict:
    payload = {"project_name": project_name, "git_url": git_url}
    res = post_json("/repo", payload)
    res.raise_for_status()
    return res.json()

def api_list_projects() -> List[Dict]:
    res = get_json("/projects")
    res.raise_for_status()
    return res.json()

def api_get_project_files(project_id: str) -> List[Dict]:
    res = get_json(f"/projects/{project_id}/files")
    res.raise_for_status()
    return res.json()

def api_generate_readme(project_id: str) -> Dict:
    res = get_json(f"/projects/{project_id}/readme")
    res.raise_for_status()
    return res.json()

# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="Repo Summarizer", page_icon="📚", layout="wide")
st.title("Repo Summarizer UI")

with st.sidebar:
    st.caption("Backend")
    st.code(API_BASE+"/docs")

# --- Create project form ---
st.subheader("1) Add a project")
with st.form("create_project_form", clear_on_submit=False):
    project_name = st.text_input("Project Name", placeholder="e.g., ProjectName")
    git_url = st.text_input("Git URL", placeholder="https://github.com/you/your-repo")
    submitted = st.form_submit_button("Create / Register Project")

if submitted:
    if not project_name.strip():
        st.error("Project name is required.")
    else:
        try:
            created = api_create_project(project_name.strip(), git_url.strip() or None)
            print(created)
            st.success(f"Project created: {created.get('project_name', project_name)}")
            st.session_state["_projects_cache"] = None  # invalidate cache
        except requests.HTTPError as e:
            msg = e.response.text if e.response is not None else str(e)
            st.error(f"Failed to create project: {msg}")
        except Exception as e:
            st.error(f"Error: {e}")

# --- Load project list ---
st.subheader("2) Projects")
colA, colB = st.columns([1, 5])
with colA:
    refresh = st.button("🔄 Refresh list", use_container_width=True)

if "_projects_cache" not in st.session_state or refresh:
    st.session_state["_projects_cache"] = None

if st.session_state["_projects_cache"] is None:
    try:
        st.session_state["_projects_cache"] = api_list_projects()
    except Exception as e:
        st.error(f"Failed to load projects: {e}")
        st.stop()

projects = st.session_state["_projects_cache"] or []

if not projects:
    st.info("No projects yet. Add one above.")
    st.stop()

# Map names to ids (fallbacks if fields differ)
def _proj_label(p: Dict) -> str:
    name = p.get("project_name") or p.get("name") or "<unnamed>"
    pid = p.get("project_id") or p.get("id") or ""
    return f"{name} ({pid})" if pid else name

labels = [_proj_label(p) for p in projects]
index_default = 0
selected_label = st.selectbox("Select a project", labels, index=index_default)

# Resolve selection to project dict
selected_project: Dict = projects[labels.index(selected_label)]
project_id = str(selected_project.get("project_id") or selected_project.get("id"))
project_name_sel = selected_project.get("project_name") or selected_project.get("name")

st.write(f"**Selected:** {project_name_sel}")
st.caption(f"Project ID: `{project_id}`")

# --- Fetch files for the selected project ---
st.subheader("3) Files & Summaries")
files_placeholder = st.empty()

try:
    files = api_get_project_files(project_id)
    if not isinstance(files, list):
        raise ValueError("Unexpected response shape for files")
    # if files:
    #     # Show as a simple table
    #     st.dataframe(
    #         [{"file_name": f.get("file_name"), "file_content" : f.get("file_content"), "summary": f.get("file_summary")} for f in files],
    #         use_container_width=True,
    #     )
    # else:
    #     st.info("No files found for this project.")
    
    if not files:
        st.info("No files found for this project.")
    else:
        view = st.radio("View", options=["Cards", "Table"], horizontal=True)
        if view == "Cards":
            render_files_card(files)
        else:
            render_files_table(files)
    
except Exception as e:
    files_placeholder.error(f"Failed to load files: {e}")

# --- Generate README ---
st.subheader("4) Generate README")
gen_col1, gen_col2 = st.columns([1, 3])
with gen_col1:
    gen_btn = st.button("📝 Generate README", use_container_width=True)

readme_text_key = f"_readme_{project_id}"
if gen_btn:
    try:
        result = api_generate_readme(project_id)
        # print("README result:", result)
        # Accept either {readme_text: "..."} or {readme: "..."}; adapt if different
        readme_text = result or ""
        if not readme_text:
            st.warning("Backend returned empty README.")
        st.session_state[readme_text_key] = readme_text
        st.success("README generated.")
    except requests.HTTPError as e:
        st.error(f"Failed to generate README: {e.response.text if e.response is not None else e}")
    except Exception as e:
        st.error(f"Error: {e}")

readme_text = st.session_state.get(readme_text_key, "")
if readme_text:
    st.markdown("#### Preview")
    with st.expander("Show README.md preview", expanded=True):
        st.code(readme_text, language="markdown")

    # Download button
    buf = io.BytesIO(readme_text.encode("utf-8"))
    st.download_button(
        label="⬇️ Download README.md",
        data=buf,
        file_name=f"{project_name_sel or 'README'}.md",
        mime="text/markdown",
        use_container_width=True,
    )

# Footer
st.caption("Tip: set API_BASE env var to point at your FastAPI (e.g., http://localhost:8000)")