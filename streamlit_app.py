import streamlit as st
from audio_recorder_streamlit import audio_recorder
import pandas as pd
import json



from src.orchestration import orchetraction


orchetra=orchetraction()

class Sessionkeys:
    patient_details_json="Details"
    Edit_Prescription="Edit Prescription "
    file_name="Name"
    


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
    st.title("Upload the Image")
    uploaded_file = st.file_uploader("Upload the Image File", type=["png", "jpeg", "jpg"])
    if uploaded_file is not None:
        print(uploaded_file)
        st.text_area(uploaded_file.name,uploaded_file.file_id)
elif selected_option =="PDF":
    st.sidebar.text_area("pdf")
elif selected_option =="Voice":

    sub_choice=st.radio("Select the file type",["None","🎙️Recorder Voice","🔴 Streaming"])
    if sub_choice=="🎙️Recorder Voice":
        uploaded_audio = st.file_uploader("🎙️ Upload a Voice File", type=["mp3", "wav", "m4a"])
        
        if uploaded_audio is not None:
            
            if Sessionkeys.patient_details_json not in st.session_state or st.session_state.get(Sessionkeys.file_name) != uploaded_audio.file_id:
                # st.audio(uploaded_audio, format='audio/wav')
                with st.spinner("Transcribing audio... Please wait ⏳"):
                    try:
                        st.session_state[Sessionkeys.file_name]=uploaded_audio.file_id
                        new_data = json.loads(orchetra.speech_to_text(uploaded_audio))
                        st.session_state[Sessionkeys.patient_details_json] = new_data
                        
                    except json.JSONDecodeError:
                        st.error("Failed to parse transcription into Text. Please check audio or format.")
                        st.session_state[Sessionkeys.patient_details_json] = {}
                        st.rerun()
            st.title("🏥 MediScript AI - Digital Prescription")
            if "name" in st.session_state[Sessionkeys.patient_details_json] :
                # Show details in markdown "popup" style
                
                with st.expander("📋 View Prescription Details", expanded=True):
                    st.markdown(f"### 🧑 Patient: {st.session_state[Sessionkeys.patient_details_json]['name']} (Age: {st.session_state[Sessionkeys.patient_details_json]['age']})")
                    st.markdown("#### 💊 Medicines:")
                    if len(st.session_state[Sessionkeys.patient_details_json]["medicine"])>1:
                        for med in st.session_state[Sessionkeys.patient_details_json]["medicine"]:
                            st.markdown(f"- **{med['name']}** → Dosage: {med['dosage']} | Quantity: {med['quantity']} | Timing: {med['timing']}")

                        col1, col2, col3 = st.columns([1, 2, 1])  # center button in middle column
                        with col1:
                            if st.button("✏️ Edit Prescription", use_container_width=True):
                                st.session_state[Sessionkeys.Edit_Prescription] = True


                    else:
                        st.warning("No Medicine details found or transcription failed.")

                    # Edit Mode
                    

                            
            else:
                st.warning("No patient details found or transcription failed.")
            
            
            # You can also save or process the audio here
    elif sub_choice=="🔴 Streaming":
        print("Streaming")
    else:
        st.info("Select the source type")

    
else:
    st.info("Select the input type")

if st.session_state.get(Sessionkeys.Edit_Prescription, False):
    edit_prescription()






