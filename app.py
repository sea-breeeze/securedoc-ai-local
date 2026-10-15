import hashlib
import streamlit as st

from local_agent import ask_agent
from vector_search import load_document

st.set_page_config(
    page_title="SecureDoc AI",
    page_icon="🔒",
    layout="centered"
)

# Remember information between Streamlit reruns
if "loaded_pdf_hash" not in st.session_state:
    st.session_state.loaded_pdf_hash = None

if "document_index" not in st.session_state:
    st.session_state.document_index = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None


# Sidebar
with st.sidebar:
    st.title("🔒 SecureDoc AI")
    st.caption("Local PDF Research Assistant")

    st.divider()

    st.subheader("Your Document")

    uploaded_pdf = st.file_uploader(
        "Upload a PDF",
        type=["pdf"]
    )

    if uploaded_pdf is not None:
        pdf_bytes = uploaded_pdf.getvalue()

        if len(pdf_bytes) > 10 * 1024 * 1024:
            st.error("PDF must be smaller than 10 MB.")
            st.session_state.loaded_pdf_hash = None

        else:
            pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()

            if st.session_state.loaded_pdf_hash != pdf_hash:
                st.session_state.loaded_pdf_hash = None
                st.session_state.document_index = None
                st.session_state.messages = []

                with st.spinner("Loading model and processing PDF..."):
                    try:
                        st.session_state.document_index = load_document(pdf_bytes)

                        st.session_state.loaded_pdf_hash = pdf_hash
                        st.session_state.pdf_name = uploaded_pdf.name

                    except Exception:
                        st.error("Unable to process PDF.")

            if st.session_state.loaded_pdf_hash == pdf_hash:
                st.success("Document ready")
                st.write(f"**File:** {st.session_state.pdf_name}")

    else:
        st.session_state.loaded_pdf_hash = None
        st.info("Upload a PDF to get started.")

    st.divider()

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("Powered by Ollama + EmbeddingGemma")


# Main chat interface
st.title("SecureDoc AI")
st.caption("Ask questions about your PDF using local AI.")

if not st.session_state.messages:
    st.info("Upload a PDF from the sidebar, then ask a question.")

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
question = st.chat_input(
    "Ask a question about your document...",
    max_chars=500,
    disabled=st.session_state.document_index is None
)

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching document..."):
            try:
                answer = ask_agent(
                question,
                st.session_state.document_index
            )
            except Exception:
                answer = "Sorry, I couldn't process that question."

        st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })