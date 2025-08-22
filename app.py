import streamlit as st
import yaml
import json
from analysis_functions import analyze_profanity_pattern, analyze_compliance_pattern, analyze_with_llm
from call_quality import calculate_call_quality_metrics, create_call_quality_visualizations

# --- Sample Data ---
SAMPLE_DATA = {
    "Good Call (No Violations)": [
        {
            "speaker": "Agent",
            "text": "Hello, this is Sarah calling from Debt Solutions. How are you today?",
            "stime": 0,
            "etime": 7
        },
        {
            "speaker": "Customer",
            "text": "Hi Sarah, I'm alright, thanks. What's this about?",
            "stime": 7.5,
            "etime": 12
        },
        {
            "speaker": "Agent",
            "text": "I'm reaching out regarding an outstanding balance on your account. Before we proceed, could you please confirm your date of birth?",
            "stime": 11,
            "etime": 24
        },
        {
            "speaker": "Customer",
            "text": "Sure, it's July 15, 1990.",
            "stime": 23,
            "etime": 26
        },
        {
            "speaker": "Agent",
            "text": "Thank you for that information. Can you also verify your current address for me?",
            "stime": 25,
            "etime": 32
        },
        {
            "speaker": "Customer",
            "text": "Yes, it's 123 Elm Street, Springfield.",
            "stime": 31,
            "etime": 34
        },
        {
            "speaker": "Agent",
            "text": "Great, I have verified your identity. You currently have a balance of $250. How would you like to proceed with the payment?",
            "stime": 33,
            "etime": 46
        },
        {
            "speaker": "Customer",
            "text": "I can pay half of it today, about $125.",
            "stime": 45,
            "etime": 50
        },
        {
            "speaker": "Agent",
            "text": "That sounds good. Would you like to make that payment by credit card or bank transfer?",
            "stime": 49,
            "etime": 58
        },
        {
            "speaker": "Customer",
            "text": "I'll use my credit card.",
            "stime": 57,
            "etime": 59
        },
        {
            "speaker": "Agent",
            "text": "Perfect. Please hold on while I process that for you.",
            "stime": 58,
            "etime": 65
        },
        {
            "speaker": "Customer",
            "text": "Sure, take your time.",
            "stime": 64,
            "etime": 68
        },
        {
            "speaker": "Agent",
            "text": "Thank you for your patience. Your payment has been processed successfully. Is there anything else I can assist you with today?",
            "stime": 67,
            "etime": 80
        },
        {
            "speaker": "Customer",
            "text": "No, that's all. Thank you!",
            "stime": 79,
            "etime": 82
        },
        {
            "speaker": "Agent",
            "text": "You're welcome! Have a great day!",
            "stime": 81,
            "etime": 85
        }
    ],
    
    "Profanity Violation": [
        {
            "speaker": "Agent",
            "text": "Hello, this is Kyle from XYZ Collections. How the hell are you?",
            "stime": 0,
            "etime": 7
        },
        {
            "speaker": "Customer",
            "text": "I'm doing well, thank you. How can I assist you today?",
            "stime": 7.5,
            "etime": 12
        },
        {
            "speaker": "Agent",
            "text": "I need to verify your identity before discussing your account. Can you please give me your date of birth?",
            "stime": 11,
            "etime": 21
        },
        {
            "speaker": "Customer",
            "text": "Sure, it's March 15, 1985.",
            "stime": 20,
            "etime": 23
        },
        {
            "speaker": "Agent",
            "text": "Alright, that checks out. Now, you owe us a shitload of money. What the hell are you planning to do about it?",
            "stime": 22,
            "etime": 34
        },
        {
            "speaker": "Customer",
            "text": "I plan to pay it off as soon as possible, but I need to discuss my options.",
            "stime": 33,
            "etime": 38
        },
        {
            "speaker": "Agent",
            "text": "Options? Don't give me that crap. You need to pay up, plain and simple!",
            "stime": 37,
            "etime": 46
        },
        {
            "speaker": "Customer",
            "text": "I understand, but I would like to know if I can set up a payment plan.",
            "stime": 45,
            "etime": 50
        },
        {
            "speaker": "Agent",
            "text": "Payment plan? Who the hell do you think you are? Just pay the damn balance!",
            "stime": 49,
            "etime": 58
        },
        {
            "speaker": "Customer",
            "text": "I really want to resolve this, but I need a reasonable solution.",
            "stime": 57,
            "etime": 62
        },
        {
            "speaker": "Agent",
            "text": "A reasonable solution is to pay what you owe! Stop wasting my time!",
            "stime": 61,
            "etime": 70
        },
        {
            "speaker": "Customer",
            "text": "I will find a way to make this work. Thank you for your time.",
            "stime": 69,
            "etime": 74
        },
        {
            "speaker": "Agent",
            "text": "Whatever, just get it done! Bye!",
            "stime": 73,
            "etime": 80
        }
    ],
    
    "Privacy Violation": [
        {
            "speaker": "Customer",
            "text": "You have reached the voicemail of John Smith. Please leave a message after the beep.",
            "stime": 0,
            "etime": 8
        },
        {
            "speaker": "Agent",
            "text": "Hello, John. This is Lisa from Greenfield Collections. I wanted to discuss your account balance.",
            "stime": 11,
            "etime": 20
        },
        {
            "speaker": "Customer",
            "text": "If you need immediate assistance, please send an email.",
            "stime": 21,
            "etime": 27
        },
        {
            "speaker": "Agent",
            "text": "You can reach me at 1-800-555-0199. It's important to address this matter as soon as possible.",
            "stime": 28,
            "etime": 39
        },
        {
            "speaker": "Customer",
            "text": "Thank you for your call. I'll return it as soon as I can.",
            "stime": 40,
            "etime": 46
        }
    ]
}

# --- Streamlit Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="Debt Collection Call Analyzer",
    page_icon="📞"
)

# --- UI Display Functions ---

def display_llm_analysis(entity, llm_result):
    """Displays the results from the LLM analysis in a clean, single column."""
    st.subheader("🧠 AI-Powered Analysis")
    
    if "error" in llm_result:
        st.error(f"LLM analysis failed: {llm_result['error']}")
        return

    if entity == "Profanity Detection":
        agent_profanity = llm_result.get('agent_profanity', False)
        customer_profanity = llm_result.get('customer_profanity', False)
        
        st.markdown("**Profanity Findings**")
        col1, col2 = st.columns(2)
        col1.metric(label="Agent", value="Detected" if agent_profanity else "None",
                  delta="High Risk" if agent_profanity else "", delta_color="inverse")
        col2.metric(label="Customer", value="Detected" if customer_profanity else "None",
                  delta="High Risk" if customer_profanity else "", delta_color="inverse")
        
        agent_examples = llm_result.get('agent_examples', [])
        customer_examples = llm_result.get('customer_examples', [])
        if agent_examples or customer_examples:
            with st.expander("Show AI Examples", expanded=False):
                if agent_examples:
                    st.markdown("**Agent Examples:**")
                    for ex in agent_examples:
                        st.warning(f"-> \"{ex}\"")
                if customer_examples:
                    st.markdown("**Customer Examples:**")
                    for ex in customer_examples:
                        st.info(f"-> \"{ex}\"")

    elif entity == "Privacy and Compliance Violation":
        violation = llm_result.get('compliance_violation', False)
        verification = llm_result.get('verification_attempted', False)
        
        st.markdown("**Compliance Findings**")
        col1, col2 = st.columns(2)
        col1.metric(label="Violation", value="Yes" if violation else "No",
                  delta="High Risk" if violation else "", delta_color="inverse")
        col2.metric(label="Verification", value="Attempted" if verification else "Not Attempted")
        
        if llm_result.get('violation_examples'):
            with st.expander("Show Violation Details", expanded=False):
                for ex in llm_result['violation_examples']:
                    st.error(f"-> \"{ex}\"")

def display_pattern_analysis(entity, pattern_result):
    """Displays the results from the pattern-based analysis in a single column."""
    st.subheader("🤖 Pattern-Based Analysis")

    if entity == "Profanity Detection":
        agent_profanity, customer_profanity, details = pattern_result
        
        st.markdown("**Profanity Findings**")
        col1, col2 = st.columns(2)
        col1.metric(label="Agent", value="Detected" if agent_profanity else "None")
        col2.metric(label="Customer", value="Detected" if customer_profanity else "None")

        if details:
            with st.expander("Show Detected Keywords", expanded=False):
                for d in details:
                    st.markdown(f"**{d['speaker']}** at *{d['timestamp']}*: \"...{d['text']}...\"")

    elif entity == "Privacy and Compliance Violation":
        violation, details = pattern_result
        
        st.markdown("**Compliance Findings**")
        st.metric(label="Violation", value="Detected" if violation else "None")

        if details:
            with st.expander("Show Violation Details", expanded=False):
                for d in details:
                    st.error(f"**Violation at {d['timestamp']}**: \"...{d['text']}...\"")
                    st.caption(f"Keywords Found: {', '.join(d['keywords_found'])}")

def render_transcript(data):
    """Renders the conversation transcript using chat elements."""
    with st.expander("Full Conversation Transcript", expanded=False):
        for item in data:
            speaker_label = "Agent" if item['speaker'].lower() == 'agent' else "Customer"
            with st.chat_message(speaker_label):
                st.markdown(f"**Time:** {item['stime']}s - {item['etime']}s")
                st.write(item['text'])

# --- Main Application Logic ---
def main():
    st.title("📞 Debt Collection Call Analyzer")

    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # File upload OR sample selection
        st.markdown("### 📁 Data Source")
        data_source = st.radio("Choose data source:", ("Upload File", "Use Sample Data"))
        
        uploaded_file = None
        selected_sample = None
        
        if data_source == "Upload File":
            uploaded_file = st.file_uploader("Upload Conversation File", type=["json", "yaml", "yml"])
        else:
            selected_sample = st.selectbox("Select Sample Conversation:", list(SAMPLE_DATA.keys()))
            st.info(f"Using sample: **{selected_sample}**")

        # Analysis type selection
        st.markdown("### 🎯 Analysis Options")
        analysis_type = st.selectbox("Select Analysis Type", ("Profanity Detection", "Privacy and Compliance Violation"))
        st.markdown("---")
        
        with st.container():
            st.subheader("📖 Quick Start Guide")
            st.markdown("""
            1. 📁 **Choose Data:** Upload a file or select a sample conversation.
            2. 🎯**Select Analysis:** Choose the analysis type from the dropdown.
            3. 🚀**Run Analysis:** Click the "Analyze Conversation" button.
            4. 📊**Review Results:** View the comparative analysis, call quality metrics, and transcript.
            """)
        
        st.markdown("---")
        st.markdown("Made by **Ivan Dsouza**")
        st.markdown("🔗[LinkedIn](https://www.linkedin.com/in/ivan-dsouza) | 🔗[GitHub](https://github.com/ivan-3101)")

    # Handle data source
    data = None
    data_source_name = ""
    
    if uploaded_file:
        try:
            content = uploaded_file.getvalue().decode("utf-8")
            data = yaml.safe_load(content) if uploaded_file.name.endswith(('yaml', 'yml')) else json.loads(content)
            data_source_name = uploaded_file.name
        except Exception as e:
            st.error(f"Error processing uploaded file: {e}")
            return
            
    elif selected_sample:
        data = SAMPLE_DATA[selected_sample]
        data_source_name = selected_sample

    if not data:
        st.info("👋 **Welcome!** Please upload a conversation file or select a sample conversation to begin analysis.")
        
        st.subheader("📄 Expected File Structure")
        st.markdown("Your JSON or YAML file should contain a list of conversation entries, like this:")
        
        sample_code = """
[
    {
        "speaker": "Agent",
        "text": "Hello, is this Sarah Johnson?",
        "stime": 0,
        "etime": 5
    },
    {
        "speaker": "Customer",
        "text": "Yes, this is Sarah. Who's calling?",
        "stime": 5.2,
        "etime": 9
    },
    {
        "speaker": "Agent",
        "text": "Hi Sarah, this is Mark from XYZ Collections...",
        "stime": 8,
        "etime": 14
    }
]
        """
        st.code(sample_code, language='json')
        
        # Show sample data preview
        st.subheader("🔍 Sample Data Preview")
        for sample_name, sample_data in SAMPLE_DATA.items():
            with st.expander(f"Preview: {sample_name}"):
                st.write(f"**Total utterances:** {len(sample_data)}")
                st.write(f"**Duration:** {sample_data[-1]['etime']}s")
                st.json(sample_data[:2])  # Show first 2 entries
        return

    st.success(f"Data **`{data_source_name}`** is loaded and ready for analysis.")
    
    analyze_button = st.button("Analyze Conversation", type="primary")

    if analyze_button:
        with st.spinner('Performing analysis... please wait.'):
            # --- Perform all analyses first ---
            try:
                GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
            except (FileNotFoundError, KeyError):
                GEMINI_API_KEY = ""
            
            llm_result = analyze_with_llm(data, analysis_type, GEMINI_API_KEY)
            if analysis_type == "Profanity Detection":
                pattern_result = analyze_profanity_pattern(data)
            else:
                pattern_result = analyze_compliance_pattern(data)

            # --- Display Comparative Analysis Section ---
            st.header("📊 Comparative Analysis")
            col1, col2 = st.columns(2, gap="medium")
            
            with col1:
                with st.container(border=True):
                    display_llm_analysis(analysis_type, llm_result)
            with col2:
                with st.container(border=True):
                    display_pattern_analysis(analysis_type, pattern_result)
            
            st.markdown("---")

            # --- Call Quality Metrics Section ---
            with st.container(border=True):
                st.subheader("📈 Call Quality Overview")
                call_metrics = calculate_call_quality_metrics(data)
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                m_col1.metric("Total Duration", f"{call_metrics['total_duration']}s")
                m_col2.metric("Silence %", f"{call_metrics['silence_percentage']:.2f}%")
                m_col3.metric("Overtalk %", f"{call_metrics['overtalk_percentage']:.2f}%")
                
                agent_time = sum((i['end'] - i['start']) for i in call_metrics.get('speaking_intervals', []) if i['speaker'].lower() == 'agent')
                customer_time = sum((i['end'] - i['start']) for i in call_metrics.get('speaking_intervals', []) if i['speaker'].lower() != 'agent')
                m_col4.metric("Agent vs Customer Talk Time", f"{agent_time:.1f}s / {customer_time:.1f}s")
                
                fig = create_call_quality_visualizations(call_metrics)
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            render_transcript(data)
            st.balloons()

if __name__ == "__main__":
    main()