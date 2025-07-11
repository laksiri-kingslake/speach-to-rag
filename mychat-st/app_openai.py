import gradio as gr
import pandas as pd
from pandasai import SmartDataframe
# from langchain_groq.chat_models import ChatGroq  # Commented out Groq
from langchain_openai import ChatOpenAI  # Added OpenAI
import os
from transformers import pipeline
import mysql.connector
from dotenv import load_dotenv
import time
import mimetypes
import uuid

# Load environment variables
load_dotenv()

# Initialize components
# llm = ChatGroq(model_name="llama3-70b-8192", api_key=os.environ["GROQ_API_KEY"])  # Commented out Groq
llm = ChatOpenAI(model_name="gpt-3.5-turbo", api_key=os.environ["OPENAI_API_KEY"])  # Use OpenAI
speech_pipe = pipeline("automatic-speech-recognition", "openai/whisper-base")

def is_image_file(filepath):
    if not isinstance(filepath, str):
        return False
    mime, _ = mimetypes.guess_type(filepath)
    return mime is not None and mime.startswith("image/")

def process_query(message, history):
    """Process user query and return response (text or image)"""
    if isinstance(message, dict):  # Audio input
        audio_path = message["mic"]
        message = speech_pipe(audio_path)["text"]
    
    mydb = mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )
    
    try:
        df = pd.read_sql("SELECT * FROM employee_skill_view", mydb)
        # Configure PandasAI with better settings to avoid concatenation errors
        config = {
            "llm": llm,
            "verbose": False,
            "enforce_privacy": False,
            "max_retries": 3,
            "enable_logging": False
        }
        smart_df = SmartDataframe(df, config=config)

        # Generate a unique filename for the chart
        chart_dir = os.path.join(os.getcwd(), "exports", "charts")
        os.makedirs(chart_dir, exist_ok=True)
        unique_chart_path = os.path.join(chart_dir, f"chart_{uuid.uuid4().hex}.png")
        os.environ["PANDASAI_CHART_PATH"] = unique_chart_path  # PandasAI uses this if set

        # First, let's check the data quality
        total_employees = len(df)
        employees_with_skill_rate = len(df.dropna(subset=['skill_rate']))
        null_skill_rates = df['skill_rate'].isnull().sum()

        response = smart_df.chat(message)

        # Handle chart/image file responses
        if is_image_file(response):
            if os.path.exists(response):
                diagnostic_info = f"\n\n📊 **Data Summary:**\n- Total employees: {total_employees}\n- Employees with skill rates: {employees_with_skill_rate}\n- Employees with NULL skill rates: {null_skill_rates}"
                return {"type": "image", "path": response, "diagnostic": diagnostic_info}
            else:
                # Try again with a new filename
                unique_chart_path = os.path.join(chart_dir, f"chart_{uuid.uuid4().hex}.png")
                os.environ["PANDASAI_CHART_PATH"] = unique_chart_path
                response = smart_df.chat(message)
                if os.path.exists(response):
                    diagnostic_info = f"\n\n📊 **Data Summary:**\n- Total employees: {total_employees}\n- Employees with skill rates: {employees_with_skill_rate}\n- Employees with NULL skill rates: {null_skill_rates}"
                    return {"type": "image", "path": response, "diagnostic": diagnostic_info}
                else:
                    return {"type": "text", "content": "Chart could not be generated. Please try again."}
        # Handle different response types
        if isinstance(response, pd.DataFrame):
            if response.empty:
                return {"type": "text", "content": "No data found matching your query."}
            return {"type": "text", "content": response.to_markdown()}
        elif isinstance(response, pd.Series):
            return {"type": "text", "content": response.to_string()}
        elif isinstance(response, str):
            return {"type": "text", "content": response}
        else:
            return {"type": "text", "content": str(response)}

    except Exception as pandasai_error:
        error_msg = str(pandasai_error)
        if "concatenate" in error_msg.lower() or "series" in error_msg.lower():
            return {"type": "text", "content": f"I understand you're asking about employee skills. Let me help you with that. Could you please rephrase your question to be more specific? For example:\n\n- 'Show me all employees with Python skills'\n- 'List employees by department'\n- 'Count employees by skill level'\n\nError details: {error_msg}"}
        else:
            return {"type": "text", "content": f"Error processing your query: {error_msg}"}
    finally:
        mydb.close()

def handle_submit(audio, text, history):
    """Handle form submission with audio or text input, supporting images in chat."""
    query = text.strip()
    if audio is not None:
        query = speech_pipe(audio)["text"]
    
    if not query:
        return "", history, history
    
    response = process_query(query, history)
    # Append as (user input, bot response) tuple
    if isinstance(response, dict) and response.get("type") == "image":
        # For chart responses, add diagnostic info if available
        diagnostic = response.get("diagnostic", "")
        if diagnostic:
            # Add diagnostic info as a separate message
            history.append((query, (None, response["path"])))  # (user, (None, image_path))
            history.append(("", diagnostic))  # Add diagnostic info
        else:
            history.append((query, (None, response["path"])))
        return "", history, history
    elif isinstance(response, dict) and response.get("type") == "text":
        history.append((query, response["content"]))
        return "", history, history
    else:
        history.append((query, str(response)))
        return "", history, history

def clear_chat(history):
    """Clear the chat history"""
    return []

def get_data_info():
    """Get information about the data to help with debugging"""
    mydb = mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )
    
    try:
        df = pd.read_sql("SELECT * FROM employee_skill_view", mydb)
        
        info = f"""
📊 **Database Information:**
- Total employees: {len(df)}
- Employees with skill rates: {len(df.dropna(subset=['skill_rate']))}
- Employees with NULL skill rates: {df['skill_rate'].isnull().sum()}
- Unique skill rates: {df['skill_rate'].nunique()}
- Skill rate range: {df['skill_rate'].min()} to {df['skill_rate'].max()}

🔍 **Sample skill rates:**
{df['skill_rate'].value_counts().head(10).to_string()}

💡 **Suggested queries:**
- "Show all employees with their skill rates"
- "List employees with NULL skill rates"
- "Show skill rate distribution"
- "Count employees by skill rate range"
        """
        return info
        
    except Exception as e:
        return f"Error getting data info: {str(e)}"
    finally:
        mydb.close()

# Custom CSS for better styling
custom_css = """
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.main-header {
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 0.5rem;
    border-radius: 15px;
    margin-bottom: 0.5rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.main-header h1 {
    margin: 0;
    font-size: 2.0rem;
    font-weight: 700;
}

.main-header p {
    margin: 0.5rem 0 0 0;
    font-size: 1.1rem;
    opacity: 0.9;
}

.input-section {
    background: white;
    padding: 1rem;
    border-radius: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}

.chat-container {
    background: white;
    border-radius: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    overflow: hidden;
}

.submit-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.submit-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
}

.clear-btn {
    background: #f8f9fa !important;
    color: #6c757d !important;
    border: 1px solid #dee2e6 !important;
    padding: 8px 16px !important;
    border-radius: 20px !important;
    font-weight: 500 !important;
}

.clear-btn:hover {
    background: #e9ecef !important;
    color: #495057 !important;
}

.audio-input {
    border: 2px dashed #dee2e6 !important;
    border-radius: 15px !important;
    padding: 1rem !important;
    transition: all 0.3s ease !important;
    min-height: 200px;
}

.audio-input:hover {
    border-color: #667eea !important;
    background: #f8f9ff !important;
}

.text-input {
    border: 2px solid #e9ecef !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
    min-height: 200px;
}

.text-input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}

.chatbot {
    border: none !important;
    border-radius: 15px !important;
    overflow: hidden !important;
}

.status-indicator {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #28a745;
    margin-right: 8px;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 0rem 0;
}

.feature-card {
    background: #f8f9ff;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    border: 1px solid #e9ecef;
}

.feature-card h4 {
    margin: 0 0 0.5rem 0;
    color: #667eea;
}

.feature-card p {
    margin: 0;
    font-size: 0.9rem;
    color: #6c757d;
}
"""

# Create the Gradio interface
with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
    
    # Header section
    with gr.Row():
        gr.HTML("""
        <div class="main-header">
            <h1>KingslakeBlue Assistant</h1>
        </div>
        """)
    
    # Feature highlights
    # with gr.Row():
    #     gr.HTML("""
    #     <div class="feature-grid">
    #         <div class="feature-card">
    #             <h4>🎤 Voice Input</h4>
    #         </div>
    #         <div class="feature-card">
    #             <h4>📊 Data Analysis</h4>
    #         </div>
    #         <div class="feature-card">
    #             <h4>💬 Smart Chat</h4>
    #         </div>
    #         <div class="feature-card">
    #             <h4>⚡ Real-time</h4>
    #         </div>
    #     </div>
    #     """)
    
    # Main content area
    with gr.Row():
        with gr.Group(elem_classes="chat-container"):
            gr.Markdown("### 💬 **Conversation History**")
            chat_output = gr.Chatbot(
                label="",
                height=360,
                elem_classes="chatbot"
            )
    
    with gr.Row():
        with gr.Group(elem_classes="input-section"):
            gr.Markdown("### ✍️ **Ask your question**")
            with gr.Row():
                with gr.Column(scale=1):
                    mic_input = gr.Audio(
                        sources="microphone",
                        type="filepath",
                        label=None,
                        elem_id="mic-btn",
                        elem_classes="audio-input",
                        show_label=False
                    )
                with gr.Column(scale=3):
                    text_input = gr.Textbox(
                        label="Type or speak your question here",
                        placeholder="Ask me anything about employee skills...",
                        lines=3,
                        elem_classes="text-input",
                        show_label=False,
                        scale=8
                    )
                with gr.Column(scale=1):
                    with gr.Row():
                        submit_btn = gr.Button(
                            "Send Message",
                            variant="primary",
                            elem_classes="submit-btn"
                        )
                    with gr.Row():
                        clear_btn = gr.Button(
                            "Clear Chat",
                            elem_classes="clear-btn"
                        )
        
    # State to maintain conversation history
    history_state = gr.State([])

    # When audio is recorded, transcribe and insert into textbox
    def transcribe_audio(audio, text):
        if audio is not None:
            transcribed = speech_pipe(audio)["text"]
            return transcribed
        return text

    mic_input.change(
        transcribe_audio,
        inputs=[mic_input, text_input],
        outputs=[text_input]
    )

    # Event handlers
    submit_btn.click(
        handle_submit,
        inputs=[mic_input, text_input, history_state],
        outputs=[text_input, chat_output, history_state]
    )
    
    text_input.submit(
        handle_submit,
        inputs=[mic_input, text_input, history_state],
        outputs=[text_input, chat_output, history_state]
    )
    
    clear_btn.click(
        clear_chat,
        inputs=[history_state],
        outputs=[history_state]
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    ) 