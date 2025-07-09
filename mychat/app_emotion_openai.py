import gradio as gr
import pandas as pd
from pandasai import SmartDataframe
from langchain_groq.chat_models import ChatGroq
from langchain_openai import ChatOpenAI 
import os
from transformers import pipeline
import mysql.connector

# Initialize components
llm = ChatOpenAI(
    model_name="gpt-4-turbo-preview",  # or "gpt-4" for latest stable version
    api_key=os.environ["OPENAI_API_KEY"]  # Changed environment variable
)
speech_pipe = pipeline("automatic-speech-recognition", "openai/whisper-base")
emotion_pipe = pipeline("text-classification", 
                       model="joeddav/distilbert-base-uncased-go-emotions-student")

def process_query(message, history):
    # Detect emotion before processing query
    if isinstance(message, dict):  # Audio input
        audio_path = message["mic"]
        message = speech_pipe(audio_path)["text"]
    
    # Emotion detection
    emotion_result = emotion_pipe(message)[0]
    emotion_response = f"Detected emotion: {emotion_result['label']} (confidence: {emotion_result['score']:.2f})"

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
        
        # Combine emotion detection with original response
        full_response = f"{emotion_response}\n\n{response}"
        return str(full_response)
        
    except Exception as e:
        return f"{emotion_response}\n\nError: {str(e)}"
    finally:
        mydb.close()

def handle_submit(audio, text, history):
    query = text
    if audio is not None:
        query = speech_pipe(audio)["text"]
    
    response = process_query(query, history)
    history.append((query, response))
    return "", history, history

with gr.Blocks() as demo:
    gr.Markdown("# KingslakeBlue Support AI Assistant")
    gr.Markdown("## Ask me anything about employee skills!")
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(sources="microphone", type="filepath", label="Speak your query")
            text_input = gr.Textbox(label="Or type your query")
            submit_btn = gr.Button("Submit")
            cancel_btn = gr.Button("Cancel")
        
            chat_output = gr.Chatbot(label="Conversation History")
    
    history_state = gr.State([])
    
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