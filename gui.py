from flask import Flask, render_template_string, request, jsonify
import json
from google import genai
from google.genai import types

app = Flask(__name__)

def create_image_prompt(description: str, style: str = "photorealistic") -> str:
    return f"A high-quality {style} image of {description}, highly detailed, 8k resolution, professional lighting."

def publish_social_post(platform: str, text_content: str, hashtags: list[str]) -> str:
    formatted_hashtags = " ".join([f"#{tag}" for tag in hashtags])
    payload = {"status": "QUEUED_FOR_APPROVAL", "platform": platform, "content": f"{text_content}\n\n{formatted_hashtags}"}
    return json.dumps(payload)

def log_pending_task(task_name: str, priority: str = "medium") -> str:
    task = {"task": task_name, "priority": priority, "status": "pending"}
    with open("task_queue.json", "a") as f:
        f.write(json.dumps(task) + "\n")
    return f"Task '{task_name}' logged successfully with {priority} priority."

tools_list = [create_image_prompt, publish_social_post, log_pending_task]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Agent Web UI</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
        .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input, textarea, button { width: 100%; margin-top: 10px; padding: 10px; box-sizing: border-box; }
        #response { margin-top: 20px; padding: 10px; background: #eef; border-radius: 5px; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🤖 Autonomous AI Agent App</h2>
        <input type="password" id="apiKey" placeholder="Enter Gemini API Key (AIzaSy...)">
        <textarea id="userInput" rows="4" placeholder="Type your command here..."></textarea>
        <button onclick="sendPrompt()">Send Command</button>
        <div id="response"></div>
    </div>

    <script>
        async function sendPrompt() {
            const apiKey = document.getElementById('apiKey').value;
            const prompt = document.getElementById('userInput').value;
            const responseDiv = document.getElementById('response');
            
            if(!apiKey || !prompt) {
                alert('API Key aur Prompt dono bharo!');
                return;
            }

            responseDiv.innerText = "Processing...";

            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: apiKey, prompt: prompt })
            });

            const data = await res.json();
            responseDiv.innerText = data.result;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    api_key = data.get('api_key')
    prompt = data.get('prompt')

    try:
        client = genai.Client(api_key=api_key)
        chat_session = client.chats.create(
            model="gemini-3.6-flash",
            config=types.GenerateContentConfig(
                system_instruction="You are an autonomous social content manager agent.",
                tools=tools_list,
                temperature=0.3,
            )
        )
        response = chat_session.send_message(prompt)
        return jsonify({'result': response.text})
    except Exception as e:
        return jsonify({'result': f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(port=5000)