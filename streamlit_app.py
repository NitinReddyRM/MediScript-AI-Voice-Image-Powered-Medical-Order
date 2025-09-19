import streamlit as st
from audio_recorder_streamlit import audio_recorder
import pandas as pd
import fitz
import json
import time
from gtts import gTTS
import io
import base64



from src.orchestration import orchetraction


orchetra=orchetraction()

class Sessionkeys:
    patient_details_json="Details"
    Edit_Prescription="Edit Prescription "
    file_name="Name"
    Audio_button=True
    


st.set_page_config(layout='wide',page_title="MediScript AI")

# --- Prescription Edit Dialog ---
@st.dialog("✏️ Edit Prescription")
def edit_prescription():
    st.session_state[Sessionkeys.Edit_Prescription]=False
    st.markdown(
        """
        <style>
        .stDialog > div > div {
            width: 80vw !important;
            max-width: 1200px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Load medicines into DataFrame
    df = pd.DataFrame(st.session_state[Sessionkeys.patient_details_json]["medicine"]).rename(columns={
        "name": "Drug Name",
        "dosage": "Dosage",
        "quantity": "Quantity",
        "timing": "Timing"
    })

    st.write("💊 Update medicine quantities (only Quantity is editable):")
    edited_df = st.data_editor(
        df,
        column_config={
            "Quantity": st.column_config.NumberColumn("Quantity", min_value=1, step=1)
        },
        disabled=["Drug Name", "Dosage", "Timing"],  # lock other columns
        use_container_width=True,
        height=300,
        hide_index=True 
    )

    if st.button("💾 Save Details", type="primary", use_container_width=True):
        # Update JSON in session state
        
        st.session_state[Sessionkeys.patient_details_json]["medicine"] = edited_df.rename(columns={
    "Drug Name": "name",
    "Dosage": "dosage",
    "Quantity": "quantity",
    "Timing": "timing"
}).to_dict(orient="records")
        st.success("✅ Prescription updated successfully!")
        st.rerun()

        
def play_audio():
    text_lines = []
    for k, v in st.session_state[Sessionkeys.patient_details_json].items():
        if isinstance(v, list):  # If the value is a list
            text_lines.append(f"{k}:")
            for item in v:
                text_lines.append(f" - {item}")
        else:
            text_lines.append(f"{k}: {v}")

    text_to_read = "\n".join(text_lines)
    tts = gTTS(text_to_read, lang="en")
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)

    # Play audio directly in Streamlit
    # Encode as base64 for inline autoplay
    b64 = base64.b64encode(audio_bytes.read()).decode()
    # Autoplay audio
    st.components.v1.html(
f"""
<audio autoplay>
<source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
</audio>
""",
height=0,
)

def display_details():
    
    if "name" in st.session_state[Sessionkeys.patient_details_json] :
        
        st.title("🏥 MediScript AI - Digital Prescription")
        # Show details in markdown "popup" style
        
        with st.expander("📋 View Prescription Details", expanded=True):
            st.markdown(f"### 🧑 Patient: {st.session_state[Sessionkeys.patient_details_json]['name']} (Age: {st.session_state[Sessionkeys.patient_details_json]['age']})")
            st.markdown("#### 💊 Medicines:")
            if len(st.session_state[Sessionkeys.patient_details_json]["medicine"])>1:
                for med in st.session_state[Sessionkeys.patient_details_json]["medicine"]:
                    st.markdown(f"- **{med['name']}** → Dosage: {med['dosage']} | Quantity: {med['quantity']} | Timing: {med['timing']}")

                col1,space, col2, space2,col3 = st.columns([1,0.5, 1,0.2, 1])  # center button in middle column
                with col1:
                    if st.button("✏️ Edit Prescription", use_container_width=True):
                        st.session_state[Sessionkeys.Edit_Prescription] = True
                with col2:
                    if st.button("🔊 Play", use_container_width=True, help="Read the Medicines"):
                        with space2:
                            with st.spinner(""):
                                play_audio()
                        

                            



            else:
                st.warning("No Medicine details found or transcription failed.")

            # Edit Mode
            

                    
    else:
        st.warning("No patient details found or transcription failed.")

# def patient_details():
    

st.markdown("""
    <style>
    .custom-title {
        font-size: 40px;
        text-align: left;
        width: 80%;
        padding: 5px;
        border-radius: 80px;
    }
    </style>
    <div class="custom-title">🧬 MediScript AI: Voice & Image Powered Medical Order Automation  🤖</div>
""", unsafe_allow_html=True)
st.sidebar.title("Select the Resource")
st.markdown("""
<div style='font-size:18px;'>
  <strong>MediScript AI</strong> is an AI-powered tool that transforms doctor prescriptions from 
  <strong>images or voice</strong> into structured, machine-readable medical orders. Using 
  <strong>OCR, speech-to-text (Whisper), and LLMs like GPT-4</strong> Whisper</strong> extracts patient and 
  medicine details accurately. It outputs clean <strong>JSON, PDF, or text formats</strong> ready 
  for pharmacy use or digital records.
</div>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            width: 300px !important; 
        }

        /* Adjust main content to accommodate new sidebar size */
        section[data-testid="stSidebar"] + div {
            margin-left: 30px;  /* Slightly more than sidebar width */
        }
    </style>
""", unsafe_allow_html=True)


choice=["Select input",'Image',"PDF","Voice"]
selected_option =st.sidebar.selectbox("Choose input type",choice)

if selected_option =="Image":

    st.markdown("### 📸 Drag & Drop Prescription Image Here")
    uploaded_file = st.file_uploader(
    label="Upload Image",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=False,
    help="Upload the doctor's handwritten prescription image"
)
    if uploaded_file is not None:
        st.success(f"✅ File `{uploaded_file.name}` uploaded successfully!")
        
elif selected_option =="PDF":
    st.markdown("### 📄 Drag & Drop Prescription PDF Here")
    PDF_File = st.file_uploader(
    label="Upload PDF",
    type=["pdf"],
    accept_multiple_files=False,
    help="Upload the patient's prescription PDF. Only new uploads trigger parsing."
)
    if PDF_File is not None:

        st.success(f"✅ File `{PDF_File.name}` uploaded successfully!")
        if Sessionkeys.patient_details_json not in st.session_state or st.session_state.get(Sessionkeys.file_name) != PDF_File.file_id:
            with st.spinner("🔍 Extracting text from PDF..."):
                try:
                    # Open the PDF with fitz
                    pdf_document = fitz.open(stream=PDF_File.read(), filetype="pdf")
                    text = " ".join([page.get_text() for page in pdf_document])
                    
                    
                    st.session_state[Sessionkeys.file_name]=PDF_File.file_id
                    new_data = json.loads(orchetra.PDF_data_extraction(text))
                    st.session_state[Sessionkeys.patient_details_json] = new_data
        
                    
                except Exception as e:
                    st.error(f"Failed to parse PDF: {e}")
                    st.session_state[Sessionkeys.patient_details_json] = {}
                    st.write("⏳ Refreshing in 10 seconds...")
                    time.sleep(10)
                    st.rerun()
                    
        st.success(f"✅ PDF '{PDF_File.name}' parsed successfully!")
        display_details()
elif selected_option =="Voice":
    
    st.markdown("### 🩺 Upload Doctor's Prescription (Voice Recording)")
    sub_choice = st.radio(
        "Choose input mode",
        ["None", "🎙️ Upload Voice Note", "🔴 Live Streaming"],
        horizontal=True
    )
    if sub_choice=="🎙️ Upload Voice Note":
        uploaded_audio = st.file_uploader(
            "📂 Upload Prescription Voice File",
            type=["mp3", "wav", "m4a"],
            help="Upload the doctor's voice prescription (MP3/WAV/M4A)"
        )
        
        if uploaded_audio is not None:
            st.success(f"✅ File `{uploaded_audio.name}` uploaded successfully!")
            
            if Sessionkeys.patient_details_json not in st.session_state or st.session_state.get(Sessionkeys.file_name) != uploaded_audio.file_id:
                # st.audio(uploaded_audio, format='audio/wav')
                with st.spinner("📝 Transcribing doctor's prescription... Please wait ⏳"):
                    try:
                        st.session_state[Sessionkeys.file_name]=uploaded_audio.file_id
                        new_data = json.loads(orchetra.speech_to_text(uploaded_audio))
                        st.session_state[Sessionkeys.patient_details_json] = new_data
                        
                    except json.JSONDecodeError:
                        st.error("Failed to parse transcription into Text. Please check audio or format.")
                        st.session_state[Sessionkeys.patient_details_json] = {}
                        st.write("⏳ Refreshing in 10 seconds...")
                        time.sleep(10)
                        st.rerun()
            st.success(f"✅ Prescription from '{uploaded_audio.name}' processed successfully!")
            display_details()
            
            
            # You can also save or process the audio here
    elif sub_choice=="🔴 Streaming":
        print("Streaming")
    else:
        st.info("Select the source type")

    
else:
    st.info("Select the input type")

if st.session_state.get(Sessionkeys.Edit_Prescription, False):
    edit_prescription()






