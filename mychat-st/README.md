# 🎯 KingslakeBlue AI Assistant - Enhanced UI

A modern, user-friendly AI assistant for employee skills insights with improved UI/UX design.

## ✨ Features

- **🎤 Voice Input**: Speak naturally to ask questions
- **📊 Data Analysis**: Get insights from employee skills data
- **💬 Smart Chat**: Natural conversation with AI
- **⚡ Real-time**: Instant responses and updates
- **🎨 Modern UI**: Beautiful, responsive design
- **📱 Mobile-friendly**: Works great on all devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MySQL database with employee skills data
- Environment variables configured

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt --only-binary=:all:
   ```

2. **Set up environment variables:**
   Create a `.env` file with:
   ```
   GROQ_API_KEY=your_groq_api_key
   DB_HOST=your_database_host
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_NAME=your_database_name
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the app:**
   Open your browser and go to `http://localhost:7860`

## 🎨 UI Improvements

### What's New

- **Modern Design**: Clean, professional interface with gradient backgrounds
- **Better Layout**: Organized sections with clear visual hierarchy
- **Interactive Elements**: Hover effects and smooth transitions
- **Status Indicators**: Visual feedback for AI readiness
- **Feature Cards**: Highlight key capabilities
- **Responsive Design**: Works perfectly on desktop and mobile
- **Enhanced Typography**: Better readability and visual appeal
- **Color Scheme**: Professional blue-purple gradient theme

### Key UI Components

- **Header Section**: Eye-catching title with status indicator
- **Feature Grid**: Showcase of main capabilities
- **Input Panel**: Organized voice and text input areas
- **Chat Interface**: Clean conversation display
- **Action Buttons**: Clear call-to-action buttons

## 🔧 Technical Details

- **Framework**: Gradio with custom CSS styling
- **AI Model**: Llama3-70b-8192 via Groq
- **Speech Recognition**: OpenAI Whisper
- **Database**: MySQL with PandasAI integration
- **Theme**: Soft theme with custom styling

## 📱 Usage

1. **Voice Input**: Click the microphone icon and speak your question
2. **Text Input**: Type your question in the text area
3. **Send**: Click "Send Message" or press Enter
4. **Clear**: Use "Clear Chat" to start a new conversation

## 🎯 Example Questions

- "Show me all employees with Python skills"
- "Who has the most experience in data analysis?"
- "List employees by department"
- "What skills are most common in the engineering team?"

## 🔒 Security

- Environment variables for sensitive data
- Secure database connections
- No data persistence in the UI

## 🐛 Troubleshooting

- **Audio not working**: Check microphone permissions
- **Database errors**: Verify connection settings in `.env`
- **API errors**: Ensure GROQ_API_KEY is valid
- **Port conflicts**: Change `server_port` in `app.py`

## 📄 License

This project is part of the KingslakeBlue AI Assistant suite. 