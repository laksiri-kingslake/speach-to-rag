import os
import gradio as gr
import openai
from dotenv import load_dotenv
import mysql.connector
import pandas as pd
from transformers import pipeline

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Initialize OpenAI client
client = None
if OPENAI_API_KEY:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
else:
    print("Warning: OPENAI_API_KEY not found. NL-to-SQL functionality will be disabled.")

# Initialize Speech-to-Text pipeline
try:
    transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")
except Exception as e:
    print(f"Error initializing speech-to-text pipeline: {e}")
    transcriber = None

# --- Database Schema ---
# This schema definition helps the LLM generate accurate SQL queries.
# It's designed to be extensible for future views like 'line_efficiency_view'.
DATABASE_SCHEMA = """
-- The database contains information about production line balancing.
-- We have the following views available:
-- 1. employee_skill_view: Contains details about employee skills.

-- Columns in employee_skill_view:
-- employee_id (INT): The unique identifier for an employee.
-- employee_name (VARCHAR): The name of the employee.
-- skill_id (INT): The unique identifier for a skill.
-- skill_name (VARCHAR): The name of the skill (e.g., 'Sewing', 'Cutting').
-- skill_rate (INT): A rating of the employee's proficiency in that skill.

-- Example queries:
-- "List top 10 employees by their skill rate. show employee name, skill name and skill rate"
-- "show top 10 employees by their skill rate in a bar chart"
"""

# --- Core Functions ---

def get_db_connection():
    """Establishes a connection to the MariaDB database."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def generate_sql_from_text(user_query):
    """Uses OpenAI GPT-3.5 to convert a natural language query into a SQL query."""
    if not client:
        return None, "OpenAI API key is not configured."

    prompt = f"""
    Given the following database schema:
    {DATABASE_SCHEMA}

    Convert the following user's question into a valid SQL query for MariaDB.
    Only return the SQL query and nothing else.

    User Question: "{user_query}"
    SQL Query:
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that converts natural language questions into SQL queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        sql_query = response.choices[0].message.content.strip()
        return sql_query, None
    except Exception as e:
        return None, f"Error generating SQL: {e}"

def execute_sql_query(sql_query):
    """Executes a SQL query and returns the result as a pandas DataFrame."""
    conn = get_db_connection()
    if conn is None:
        return None, "Failed to connect to the database."
    
    try:
        df = pd.read_sql(sql_query, conn)
        return df, None
    except Exception as e:
        return None, f"Error executing query: {e}"
    finally:
        if conn.is_connected():
            conn.close()

def transcribe_audio(audio_input):
    """Transcribes audio input to text using the speech-to-text pipeline."""
    if transcriber is None or audio_input is None:
        return ""
    try:
        text = transcriber(audio_input)["text"]
        return text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return ""

def handle_chat_submission(user_message, history):
    """Main function to handle user queries, generate SQL, execute it, and return results."""
    history.append([user_message, None])
    
    # 1. Generate SQL from the user's text query
    sql_query, error = generate_sql_from_text(user_message)
    if error:
        history[-1][1] = f"Error: {error}"
        return history, gr.update(visible=False), gr.update(visible=False)

    # 2. Execute the SQL query
    result_df, error = execute_sql_query(sql_query)
    if error:
        history[-1][1] = f"Error: {error}"
        return history, gr.update(visible=False), gr.update(visible=False)

    # 3. Determine the output format (table, chart, or text)
    if "chart" in user_message.lower() and result_df is not None and not result_df.empty:
        # Generate a bar chart
        try:
            # Heuristic to find good columns for a bar chart
            x_col = result_df.columns[1]  # Often a name or category
            y_col = result_df.columns[-1]  # Often a numeric value
            history[-1][1] = "Here is the chart you requested:"
            # Return a new BarPlot object to update the UI
            return history, gr.update(visible=False), gr.BarPlot(
                value=result_df,
                x=x_col,
                y=y_col,
                title=f"Chart for: {user_message}",
                visible=True
            )
        except Exception as e:
            history[-1][1] = f"Could not generate a chart. Displaying data as a table instead. Error: {e}"
            return history, gr.update(value=result_df, visible=True), gr.update(visible=False)

    elif result_df is not None and not result_df.empty:
        # Display results in a table
        history[-1][1] = "Here is the data you requested:"
        return history, gr.update(value=result_df, visible=True), gr.update(visible=False)
    
    else:
        # Handle cases with no data or other issues
        history[-1][1] = "I couldn't retrieve any data for that query. Please try rephrasing your question."
        return history, gr.update(visible=False), gr.update(visible=False)


def clear_inputs():
    """Clears all input and output fields."""
    return "", None, [], gr.update(visible=False), gr.update(visible=False)

# --- Gradio UI ---

with gr.Blocks(theme=gr.themes.Soft(), title="KingslakeBlue Assistant") as app:
    gr.Markdown("# KingslakeBlue Assistant")

    with gr.Row():
        chatbot = gr.Chatbot(label="Chat History", height=400)

    with gr.Row():
        with gr.Column(scale=2):
            data_output = gr.DataFrame(label="Query Results", visible=False)
            plot_output = gr.BarPlot(label="Chart Results", visible=False)
        with gr.Column(scale=1):
            pass # Spacer

    with gr.Row():
        with gr.Column(scale=3):
            text_input = gr.Textbox(label="Enter your question here")
        with gr.Column(scale=1):
            audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Or record your voice")
    
    with gr.Row():
        send_button = gr.Button("Send", variant="primary")
        clear_button = gr.Button("Clear")

    # --- Event Listeners ---

    # When audio is recorded, transcribe it and put the text in the textbox
    audio_input.change(
        fn=transcribe_audio,
        inputs=audio_input,
        outputs=text_input
    )

    # When the send button is clicked or enter is pressed in the textbox
    send_button.click(
        fn=handle_chat_submission,
        inputs=[text_input, chatbot],
        outputs=[chatbot, data_output, plot_output]
    )
    text_input.submit(
        fn=handle_chat_submission,
        inputs=[text_input, chatbot],
        outputs=[chatbot, data_output, plot_output]
    )

    # When the clear button is clicked
    clear_button.click(
        fn=clear_inputs,
        inputs=[],
        outputs=[text_input, audio_input, chatbot, data_output, plot_output]
    )

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
