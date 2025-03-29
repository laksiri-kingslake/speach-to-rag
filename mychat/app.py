import gradio as gr
import pandas as pd
from pandasai import SmartDataframe
from langchain_groq.chat_models import ChatGroq
import os
from transformers import pipeline
import mysql.connector

# Initialize components
llm = ChatGroq(model_name="llama3-70b-8192", api_key=os.environ["GROQ_API_KEY"])
speech_pipe = pipeline("automatic-speech-recognition", "openai/whisper-base")

def process_query(message, history):
    if isinstance(message, dict):  # Audio input
        audio_path = message["mic"]
        message = speech_pipe(audio_path)["text"]
    
    mydb = mysql.connector.connect(
        host="trial.kingslakeblue.link",
        user="fxuser",
        password="FxUser123#@!",
        database="line_balancing"
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
    query = text
    if audio is not None:
        query = speech_pipe(audio)["text"]
    
    response = process_query(query, history)
    # Append as (user input, bot response) tuple
    history.append((query, response))
    return "", history, history

with gr.Blocks() as demo:
    gr.Markdown("# KingslakeBlue AI Assistant")
    gr.Markdown("## Ask me anything about employee skills!")
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(sources="microphone", type="filepath", label="Speak your query")
            text_input = gr.Textbox(label="Or type your query")
            submit_btn = gr.Button("Submit")
            cancel_btn = gr.Button("Cancel")
        
        chat_output = gr.Chatbot(label="Conversation History")
    
    # State to maintain conversation history
    history_state = gr.State([])
    
    def handle_submit(audio, text, history):
        query = text
        if audio is not None:
            query = speech_pipe(audio)["text"]
        
        response = process_query(query, history)
        history.append((query, response))
        return "", history, history
    
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

demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False
)