import gradio as gr
import json
from google import genai
from google.genai import types

# -------------------------------------------------------------------
# 1. DEFINE TOOL FUNCTIONS
# -------------------------------------------------------------------

def create_image_prompt(description: str, style: str = "photorealistic") -> str:
    """Generates an expanded prompt optimized for AI image generators."""
    return f"A high-quality {style} image of {description}, highly detailed, 8k resolution, professional lighting."

def publish_social_post(platform: str, text_content: str, hashtags: list[str]) -> str:
    """Simulates publishing a post to social media channels like Instagram, Telegram, or YouTube."""
    formatted_hashtags = " ".join([f"#{tag}" for tag in hashtags])
    payload = {
        "status": "QUEUED_FOR_APPROVAL",
        "platform": platform,
        "content": f"{text_content}\n\n{formatted_hashtags}"
    }
    return json.dumps(payload)

def log_pending_task(task_name: str, priority: str = "medium") -> str:
    """Saves a task to the agent's internal queue file."""
    task = {"task": task_name, "priority": priority, "status": "pending"}
    with open("task_queue.json", "a") as f:
        f.write(json.dumps(task) + "\n")
    return f"Task '{task_name}' logged successfully with {priority} priority."

tools_list = [create_image_prompt, publish_social_post, log_pending_task]

# -------------------------------------------------------------------
# 2. AGENT RESPONSE LOGIC
# -------------------------------------------------------------------

def respond(message, history, api_key):
    if not api_key:
        return "⚠️ Please enter your Gemini API Key in the box above!"
    
    try:
        client = genai.Client(api_key=api_key)
        chat = client.chats.create(
            model="gemini-3.6-flash",
            config=types.GenerateContentConfig(
                system_instruction="You are an autonomous social content manager agent. Use your tools to fulfill user requests.",
                tools=tools_list,
                temperature=0.3,
            )
        )
        response = chat.send_message(message)
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"

# -------------------------------------------------------------------
# 3. GRADIO WEB UI
# -------------------------------------------------------------------

with gr.Blocks(title="AI Agent App") as demo:
    gr.Markdown("# 🤖 Autonomous AI Content Agent")
    api_key_input = gr.Textbox(
        label="Gemini API Key", 
        type="password", 
        placeholder="Enter your API key starting with AIza..."
    )
    gr.ChatInterface(fn=respond, additional_inputs=[api_key_input])

if __name__ == "__main__":
    demo.launch()