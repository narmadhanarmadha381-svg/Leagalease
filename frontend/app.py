from __future__ import annotations

import html
import os
import re
from datetime import date
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(
    ROOT_DIR / ".env"
)


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


st.set_page_config(

    page_title="LegalEase",

    page_icon="⚖️",

    layout="wide",

    initial_sidebar_state="expanded"
)


# -----------------------------
# CUSTOM CSS
# -----------------------------

st.markdown(
    """
    <style>

    .legal-preview {

        background: #111827;

        color: #f9fafb;

        padding: 2rem;

        border-radius: 16px;

        min-height: 400px;

        max-height: 650px;

        overflow-y: auto;

        line-height: 1.65;

        border: 1px solid #374151;

    }

    .legal-preview h3 {

        color: white;

        margin-top: 1.2rem;

        margin-bottom: .5rem;

    }

    .legal-preview p {

        margin: .35rem 0;

    }

    .legal-brand {

        text-align: center;

        letter-spacing: .18em;

        font-weight: 700;

        margin-bottom: 1.5rem;

    }

    .notice {

        padding: .8rem 1rem;

        border-radius: 10px;

        background: rgba(127,127,127,.12);

        border: 1px solid rgba(127,127,127,.25);

        margin: 1rem 0;

    }

    </style>
    """,

    unsafe_allow_html=True
)


# -----------------------------
# HTML PREVIEW
# -----------------------------

def html_preview(text: str) -> str:

    parts = []

    for raw_line in text.splitlines():

        line = raw_line.strip()

        if not line:

            parts.append(
                "<div style='height:8px'></div>"
            )

        elif re.match(
            r"^\d+[\.\)]\s+",
            line
        ) or line.isupper():

            parts.append(
                f"<h3>{html.escape(line)}</h3>"
            )

        elif line.startswith("- "):

            parts.append(
                f"<li>{html.escape(line[2:])}</li>"
            )

        else:

            parts.append(
                f"<p>{html.escape(line)}</p>"
            )

    return (
        "<div class='legal-preview'>"
        "<div class='legal-brand'>LEGALEASE</div>"
        + "".join(parts)
        + "</div>"
    )


# -----------------------------
# DOCUMENT EXPORTS
# -----------------------------

def create_docx(
    content: str,
    document_type: str
) -> bytes:

    from backend.formatters.document_formatter import (
        format_docx
    )

    return format_docx(
        content,
        document_type
    )


def create_pdf(
    content: str,
    document_type: str
) -> bytes:

    from backend.formatters.document_formatter import (
        format_pdf
    )

    return format_pdf(
        content,
        document_type
    )


# -----------------------------
# HEADER
# -----------------------------

st.title("⚖️ LegalEase")

st.caption(
    "AI-powered legal document drafting"
)


st.markdown(
    """
    <div class="notice">

    <b>Important:</b>

    AI-generated drafts are not legal advice.
    Review important documents with a qualified
    legal professional before signing or relying
    on them.

    </div>
    """,

    unsafe_allow_html=True
)


# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:

    st.header(
        "Document Settings"
    )

    document_type = st.selectbox(

        "Document Type",

        [
            "Employment Contract",

            "Non-Disclosure Agreement (NDA)",

            "Lease Agreement",

            "Service Agreement",

            "Freelance Work Contract",

            "Employment Offer Letter",

            "General Agreement",

            "Custom"
        ]
    )

    if document_type == "Custom":

        document_type = st.text_input(
            "Enter document type"
        )

    language = st.selectbox(

        "Output Language",

        [
            "English",
            "Tamil",
            "Hindi",
            "Malayalam",
            "Telugu",
            "Kannada"
        ]
    )

    jurisdiction = st.text_input(

        "Jurisdiction (optional)",

        placeholder="Example: Tamil Nadu, India"
    )

    title = st.text_input(

        "Document Title (optional)",

        placeholder="Example: Freelance Services Agreement"
    )

    st.divider()

    st.caption(
        f"Backend: {BACKEND_URL}"
    )


# -----------------------------
# SESSION STATE
# -----------------------------

if "document" not in st.session_state:

    st.session_state.document = ""


if "model" not in st.session_state:

    st.session_state.model = ""


# -----------------------------
# MAIN COLUMNS
# -----------------------------

left, right = st.columns(
    [1, 1]
)


# -----------------------------
# INPUT FORM
# -----------------------------

with left:

    st.subheader(
        "Document Information"
    )

    parties = st.text_area(

        "Parties Involved",

        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),

        height=120
    )

    terms = st.text_area(

        "Terms & Conditions",

        placeholder=(
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Work must be completed by deadline; "
            "Either party may terminate with 15 days notice"
        ),

        height=180,

        help=(
            "Separate each term with a semicolon (;)."
        )
    )

    effective_date = st.date_input(

        "Effective Date",

        value=date.today()
    )

    generate = st.button(

        "✨ Generate Document",

        type="primary",

        use_container_width=True
    )


# -----------------------------
# GENERATE
# -----------------------------

if generate:

    if not parties.strip():

        st.error(
            "Please enter the parties."
        )

    elif not terms.strip():

        st.error(
            "Please enter the terms."
        )

    elif not document_type.strip():

        st.error(
            "Please provide a document type."
        )

    else:

        payload = {

            "document_type":
                document_type.strip(),

            "parties":
                parties.strip(),

            "terms":
                terms.strip(),

            "effective_date":
                effective_date.isoformat(),

            "title":
                title.strip(),

            "jurisdiction":
                jurisdiction.strip(),

            "language":
                language
        }

        with st.spinner(
            "Generating legal draft..."
        ):

            try:

                response = requests.post(

                    f"{BACKEND_URL}/generate",

                    json=payload,

                    timeout=120
                )

                if response.ok:

                    data = response.json()

                    st.session_state.document = (
                        data["content"]
                    )

                    st.session_state.model = (
                        data.get(
                            "model",
                            ""
                        )
                    )

                    st.success(
                        "Document generated successfully."
                    )

                else:

                    try:

                        detail = response.json().get(
                            "detail",
                            response.text
                        )

                    except Exception:

                        detail = response.text

                    st.error(
                        f"Backend error: {detail}"
                    )

            except requests.RequestException as exc:

                st.error(
                    "Could not connect to FastAPI. "
                    "Make sure the backend is running.\n\n"
                    f"Details: {exc}"
                )


# -----------------------------
# PREVIEW / EDIT / DOWNLOAD
# -----------------------------

with right:

    st.subheader(
        "Document Preview"
    )

    if st.session_state.document:

        st.markdown(

            html_preview(
                st.session_state.document
            ),

            unsafe_allow_html=True
        )

        st.divider()

        st.subheader(
            "Edit Document"
        )

        edited_document = st.text_area(

            "Edit the generated document",

            value=st.session_state.document,

            height=420,

            label_visibility="collapsed"
        )

        st.session_state.document = (
            edited_document
        )

        # Generate files
        txt_data = (
            edited_document.encode("utf-8")
        )

        docx_data = create_docx(

            edited_document,

            document_type
        )

        pdf_data = create_pdf(

            edited_document,

            document_type
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.download_button(

                "⬇️ TXT",

                data=txt_data,

                file_name=(
                    "legalease_document.txt"
                ),

                mime="text/plain",

                use_container_width=True
            )

        with col2:

            st.download_button(

                "⬇️ DOCX",

                data=docx_data,

                file_name=(
                    "legalease_document.docx"
                ),

                mime=(
                    "application/"
                    "vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),

                use_container_width=True
            )

        with col3:

            st.download_button(

                "⬇️ PDF",

                data=pdf_data,

                file_name=(
                    "legalease_document.pdf"
                ),

                mime="application/pdf",

                use_container_width=True
            )

        if st.session_state.model:

            st.caption(
                f"AI model: {st.session_state.model}"
            )

    else:

        st.info(
            "Your generated document will appear here."
        )
