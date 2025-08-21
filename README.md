# Debt Collection Call Analyzer 📞

A comprehensive Streamlit application for analyzing debt collection conversations to detect profanity, compliance violations, and evaluate call quality metrics.

🚀 **[Live Demo](https://debt-collection-call-analyzer.streamlit.app/)**

## Features

- **Profanity Detection**: Identify inappropriate language using both pattern matching and AI-powered analysis
- **Compliance Violation Detection**: Detect when sensitive information is shared without proper identity verification
- **Call Quality Metrics**: Calculate and visualize silence percentage, overtalk percentage, and speaking time distribution
- **Comparative Analysis**: Side-by-side comparison of pattern-based and AI-powered analysis methods
- **Interactive Visualizations**: Comprehensive dashboard with timeline views and quality metrics

## Project Structure

```
debt-collection-analyzer/
├── app.py                   # Main Streamlit application
├── analysis_functions.py    # Core analysis functions (profanity, compliance)
├── call_quality.py         # Call quality metrics and visualizations
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── .streamlit/
    └── secrets.toml       # Configuration file for API keys
```

## Quick Start

🌐 **Try the live application**: [https://debt-collection-call-analyzer.streamlit.app/](https://debt-collection-call-analyzer.streamlit.app/)

For local development, follow the installation steps below.

## Local Installation & Setup
### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd debt-collection-analyzer
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.streamlit/secrets.toml` file in your project root:

```toml
GEMINI_API_KEY = "your_google_gemini_api_key_here"
```

**To get a Gemini API key:**
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Copy the key to your `secrets.toml` file

### 5. Run the Application
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## Usage

### Input File Format

The application accepts conversation files in JSON or YAML format with the following structure:

```yaml
- speaker: "agent"
  text: "Hello, this is regarding your account"
  stime: 0.0
  etime: 3.2
- speaker: "customer"
  text: "Yes, I can hear you"
  stime: 3.5
  etime: 5.1
```

**Required fields:**
- `speaker`: "agent" or "customer" (or similar identifiers)
- `text`: The spoken content
- `stime`: Start timestamp in seconds
- `etime`: End timestamp in seconds

### How to Analyze

1. **Upload File**: Use the sidebar file uploader to select your conversation file
2. **Select Analysis Type**: Choose between "Profanity Detection" or "Privacy and Compliance Violation"
3. **Click Analyze**: The system will process the conversation using both pattern matching and AI analysis
4. **Review Results**: Compare results from both approaches and examine call quality metrics

### Analysis Types

#### Profanity Detection
- **Pattern Matching**: Uses a curated list of profane words for direct keyword matching
- **AI Analysis**: Uses Google's Gemini model to detect inappropriate language, unprofessional terms, and context-dependent profanity

#### Privacy and Compliance Violation
- **Pattern Matching**: Checks if sensitive information (account balance, SSN, etc.) is shared before identity verification
- **AI Analysis**: Uses advanced reasoning to identify compliance violations based on conversation flow and context

## Call Quality Metrics

The application automatically calculates and visualizes:

- **Total Duration**: Complete call length
- **Speaking Time**: Time spent actually speaking (excluding silence)
- **Silence Percentage**: Percentage of call that was silent
- **Overtalk Percentage**: Percentage of time both parties spoke simultaneously
- **Speaker Distribution**: Breakdown of speaking time between agent and customer
- **Timeline Visualization**: Visual representation of who spoke when

## Technical Implementation

### Pattern Matching Approach
- Uses predefined keyword sets for fast, reliable detection
- Employs regex patterns for robust text processing
- Provides deterministic results with clear keyword tracking

### AI-Powered Approach
- Leverages Google's Gemini 2.0 Flash model for context-aware analysis
- Uses structured prompts to ensure consistent JSON output
- Provides nuanced understanding of language and context

### Call Quality Calculations
- **Overtalk Detection**: Uses combinatorial analysis to find overlapping speech intervals
- **Silence Calculation**: Accounts for total duration minus speaking time plus overtalk adjustments
- **Timeline Processing**: Efficiently handles large conversation datasets

## API Requirements

- **Google Gemini API**: Required for AI-powered analysis
  - Free tier available with generous limits
  - Requires API key configuration in `secrets.toml`

## Troubleshooting

### Common Issues

1. **"Gemini API key is not set" error**
   - Ensure your `.streamlit/secrets.toml` file exists and contains a valid API key
   - Verify the key format: `GEMINI_API_KEY = "your_key_here"`

2. **File upload errors**
   - Ensure your file is in JSON or YAML format
   - Check that required fields (speaker, text, stime, etime) are present
   - Verify timestamp formats are numeric

3. **Installation issues**
   - Use Python 3.8 or higher
   - Consider using a fresh virtual environment
   - On some systems, you may need to install additional dependencies for YAML support

### Performance Tips

- For large files (>1000 utterances), analysis may take 10-15 seconds
- AI analysis is slower than pattern matching but provides more accurate results
- Consider processing very large datasets in smaller batches

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is available under the MIT License. See LICENSE file for details.

## Support

For issues, questions, or feature requests, please:
1. Check the troubleshooting section above
2. Review existing issues in the repository
3. Create a new issue with detailed information about your problem

---

**Note**: This application is designed for educational and professional use in analyzing debt collection conversations for compliance and quality purposes. Ensure you have proper authorization before analyzing any conversation data.