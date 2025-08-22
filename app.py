import streamlit as st
import yaml
import json
from analysis_functions import analyze_profanity_pattern, analyze_compliance_pattern, analyze_with_llm
from call_quality import calculate_call_quality_metrics, create_call_quality_visualizations

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
    st.markdown("Upload a conversation file and click 'Analyze' to evaluate for profanity, compliance, and call quality.")

    with st.sidebar:
        st.header("⚙️ Configuration")
        uploaded_file = st.file_uploader("Upload Conversation File", type=["json", "yaml", "yml"])


        # Analysis type selection
        st.markdown("### 🎯 Analysis Options")
        analysis_type = st.selectbox("Select Analysis Type", ("Profanity Detection", "Privacy and Compliance Violation"))
        st.markdown("---")
        
        with st.container():
            st.subheader("📖 Quick Start Guide")
            st.markdown("""
            1. 📁 **Upload File:** Select a `.json` or `.yaml` conversation file.
            2. 🎯**Select Analysis:** Choose the analysis type from the dropdown.
            3. 🚀**Run Analysis:** Click the "Analyze Conversation" button.
            4. 📊**Review Results:** View the comparative analysis, call quality metrics, and transcript.
            """)
        
        st.markdown("---")
        st.markdown("Made by **Ivan Dsouza**")
        st.markdown("🔗[LinkedIn](https://www.linkedin.com/in/ivan-dsouza) | 🔗[GitHub](https://github.com/ivan-3101)")


    if not uploaded_file:
        st.info("👋 **Welcome!** Please upload a conversation file using the sidebar to begin analysis.")
        
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
        return

    try:
        content = uploaded_file.getvalue().decode("utf-8")
        data = yaml.safe_load(content) if uploaded_file.name.endswith(('yaml', 'yml')) else json.loads(content)
        
        st.success(f"File **`{uploaded_file.name}`** is loaded and ready for analysis.")
        
        analyze_button = st.button("Analyze Conversation", type="secondary")

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
                st.header("🔍 Comparative Analysis")
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
                # st.balloons()
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")

if __name__ == "__main__":
    main()