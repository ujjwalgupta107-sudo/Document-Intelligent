import streamlit as st
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

# 1. Page Configuration
st.set_page_config(
    page_title="DocuGlass AI", 
    page_icon="✨", 
    layout="wide"
)

# 2. Custom Glossy CSS
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Glassmorphism card for results */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 15px;
        padding: 25px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        margin-bottom: 20px;
    }
    
    /* Customizing the Button */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
        padding: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(37, 117, 252, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar for Setup (Keeping the main area clean)
with st.sidebar:
    st.header("⚙️ Configuration")
    st.info("Enter your Azure credentials below to begin.")
    endpoint = st.text_input("Azure Endpoint", placeholder="https://your-resource.cognitiveservices.azure.com/")
    key = st.text_input("API Key", type="password")
    
    st.divider()
    st.markdown("### Instructions")
    st.caption("1. Enter Azure Credentials\n2. Upload PDF or Image\n3. Click Analyze")

# 4. Main UI Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.title("✨ DocuGlass AI")
    st.markdown("#### Modern Document Extraction")
    
    uploaded_file = st.file_uploader("Drop your document here", type=["png", "jpg", "jpeg", "pdf"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Document Preview", use_container_width=True)

with col2:
    st.write("### 🔍 Analysis")
    
    analyze_btn = st.button("Start Analysis")

    if analyze_btn:
        if not endpoint or not key:
            st.warning("⚠️ Credentials missing in the sidebar!")
        elif not uploaded_file:
            st.warning("⚠️ Please upload a document first.")
        else:
            try:
                with st.status("Processing Document...", expanded=True) as status:
                    st.write("Connecting to Azure...")
                    client = DocumentIntelligenceClient(
                        endpoint=endpoint,
                        credential=AzureKeyCredential(key)
                    )
                    
                    st.write("Reading file bytes...")
                    file_bytes = uploaded_file.read()

                    st.write("Running AI Extraction...")
                    poller = client.begin_analyze_document("prebuilt-read", file_bytes)
                    result = poller.result()
                    
                    status.update(label="Analysis Complete!", state="complete", expanded=False)

                # Results Section
                st.balloons()
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.subheader("📄 Extracted Content")
                
                full_text = ""
                for page in result.pages:
                    for line in page.lines:
                        full_text += line.content + "\n"
                
                # Using a code area or text area for easy copying
                st.text_area("Resulting Text", value=full_text, height=400)
                
                # Download Button
                st.download_button(
                    label="Download as Text",
                    data=full_text,
                    file_name="extracted_text.txt",
                    mime="text/plain"
                )
                st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Analysis Failed: {e}")