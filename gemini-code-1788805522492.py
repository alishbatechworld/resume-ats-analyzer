import os
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# Page configuration
st.set_page_config(
    page_title="AI Resume ATS Analyzer",
    page_icon="📄",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; color: #1E3A8A; font-weight: 700; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.2rem; color: #4B5563; margin-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">AI Resume ATS Analyzer & Optimizer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Upload your resume, match it with a job description, and get an instant ATS score using Gemini Flash.</p>', unsafe_allow_html=True)

# Sidebar for API Key and Job Description
with st.sidebar:
    st.header("Configuration")
    
    api_key_env = os.environ.get("GEMINI_API_KEY", "")
    api_key = st.text_input("Gemini API Key", value=api_key_env, type="password")
    
    st.markdown("---")
    st.header("Target Job Description")
    job_description = st.text_area(
        "Paste the Job Description here:",
        height=250,
        placeholder="Paste requirements, responsibilities, and skills needed..."
    )
    
    st.markdown("---")
    st.markdown("Powered by **Google Gemini Flash** & **Streamlit**")

# Main interface for resume upload
uploaded_file = st.file_uploader("Upload your Resume (PDF format)", type=["pdf"])

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

if uploaded_file is not None and job_description:
    if not api_key:
        st.warning("Please enter your Gemini API Key in the sidebar to proceed.")
    else:
        if st.button("Analyze Resume", type="primary"):
            with st.spinner("Extracting text and evaluating with Gemini Flash..."):
                try:
                    resume_text = extract_text_from_pdf(uploaded_file)
                    
                    if not resume_text.strip():
                        st.error("Could not extract text from the PDF. Please ensure it contains selectable text.")
                    else:
                        # Initialize Gemini Client using the official google-genai SDK
                        client = genai.Client(api_key=api_key)
                        
                        prompt = f"""
                        You are an expert ATS (Applicant Tracking System) tracker and Senior Technical Recruiter.
                        Evaluate the following resume against the provided job description.
                        
                        Job Description:
                        {job_description}
                        
                        Resume Text:
                        {resume_text}
                        
                        Provide your analysis strictly structured under these clear sections:
                        1. **ATS Score**: Give an overall matching score out of 100 as an integer (e.g., 85/100) and a brief justification.
                        2. **Strengths**: Bullet points highlighting what matches well.
                        3. **Missing Keywords/Skills**: Important terms or technical skills present in the job description but absent from the resume.
                        4. **Improvement Recommendations**: Actionable advice to rewrite bullet points, format changes, or structural tweaks to improve ATS compatibility.
                        """
                        
                        # Call Gemini Flash model
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt
                        )
                        
                        analysis_result = response.text
                        
                        # Display Results
                        st.markdown("---")
                        st.subheader("Analysis Results")
                        st.markdown(analysis_result)
                        
                except Exception as e:
                    st.error(f"An error occurred during analysis: {e}")
elif uploaded_file is not None and not job_description:
    st.info("Please provide a target job description in the sidebar to run the ATS evaluation.")
elif uploaded_file is None and job_description:
    st.info("Please upload a PDF resume file to start the analysis.")
else:
    st.info("Upload a PDF resume and paste a job description in the sidebar to get started.")
