import gradio as gr
import pandas as pd
from pandasai import SmartDataframe
from langchain_groq.chat_models import ChatGroq
import os
from transformers import pipeline
import mysql.connector
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Initialize components
llm = ChatGroq(model_name="llama3-70b-8192", api_key=os.environ["GROQ_API_KEY"])
speech_pipe = pipeline("automatic-speech-recognition", "openai/whisper-base")

def process_query(message, history):
    """Process user query and return response"""
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
        smart_df = SmartDataframe(df, config={"llm": llm})
        response = smart_df.chat(message)
        
        # Convert DataFrame responses to markdown tables
        if isinstance(response, pd.DataFrame):
            response = response.to_markdown()
            
        return str(response)
        
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        mydb.close()

def handle_submit(audio, text, history):
    """Handle form submission with audio or text input"""
    query = text.strip()
    if audio is not None:
        query = speech_pipe(audio)["text"]
    
    if not query:
        return "", history, history
    
    # Add loading state
    response = process_query(query, history)
    history.append((query, response))
    return "", history, history

def clear_chat(history):
    """Clear the chat history"""
    return []

# Custom CSS for better styling
custom_css = """
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.main-header {
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.main-header h1 {
    margin: 0;
    font-size: 2.5rem;
    font-weight: 700;
}

.main-header p {
    margin: 0.5rem 0 0 0;
    font-size: 1.1rem;
    opacity: 0.9;
}

.input-section {
    background: white;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 2rem;
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
    margin: 1rem 0;
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
            <h1>🎯 KingslakeBlue AI Assistant</h1>
            <!--<p>Your intelligent companion for employee skills insights</p>
            <div style="margin-top: 1rem;">
                <span class="status-indicator"></span>
                <span style="font-size: 0.9rem; opacity: 0.8;">AI Ready</span>
            </div>-->
        </div>
        """)
    
    # Feature highlights
    with gr.Row():
        gr.HTML("""
        <div class="feature-grid">
            <div class="feature-card">
                <h4>🎤 Voice Input</h4>
                <!--<p>Speak naturally to ask questions</p>-->
            </div>
            <div class="feature-card">
                <h4>📊 Data Analysis</h4>
                <!--<p>Get insights from employee skills data</p>-->
            </div>
            <div class="feature-card">
                <h4>💬 Smart Chat</h4>
                <!--<p>Natural conversation with AI</p>-->
            </div>
            <div class="feature-card">
                <h4>⚡ Real-time</h4>
                <!--<p>Instant responses and updates</p>-->
            </div>
        </div>
        """)
    
    # Main content area
    with gr.Row():
        with gr.Column(scale=1):
            # Input section
            with gr.Group(elem_classes="input-section"):
                gr.Markdown("### 🎤 **Voice Input**")
                audio_input = gr.Audio(
                    sources="microphone", 
                    type="filepath", 
                    label="Click to record your question",
                    elem_classes="audio-input"
                )
                
                gr.Markdown("### ✍️ **Text Input**")
                text_input = gr.Textbox(
                    label="Or type your question here",
                    placeholder="Ask me anything about employee skills...",
                    lines=3,
                    elem_classes="text-input"
                )
                
                with gr.Row():
                    submit_btn = gr.Button(
                        "🚀 Send Message", 
                        variant="primary",
                        elem_classes="submit-btn"
                    )
                    clear_btn = gr.Button(
                        "🗑️ Clear Chat",
                        elem_classes="clear-btn"
                    )
        
        with gr.Column(scale=2):
            # Chat section
            with gr.Group(elem_classes="chat-container"):
                gr.Markdown("### 💬 **Conversation**")
                chat_output = gr.Chatbot(
                    label="",
                    height=500,
                    elem_classes="chatbot"
                )
    
    # State to maintain conversation history
    history_state = gr.State([])
    
    # Event handlers
    submit_btn.click(
        handle_submit,
        inputs=[audio_input, text_input, history_state],
        outputs=[text_input, chat_output, history_state]
    )
    
    text_input.submit(
        handle_submit,
        inputs=[audio_input, text_input, history_state],
        outputs=[text_input, chat_output, history_state]
    )
    
    clear_btn.click(
        clear_chat,
        inputs=[history_state],
        outputs=[history_state]
    )
    
    # Audio input event
    audio_input.change(
        handle_submit,
        inputs=[audio_input, text_input, history_state],
        outputs=[text_input, chat_output, history_state]
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    ) 