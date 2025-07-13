import requests
import uuid
import os

import subprocess
import sys
import importlib

# Force upgrade gradio before import
subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "gradio==4.44.1"])

# Reload modules after install
import importlib
importlib.reload(sys.modules.get("gradio", importlib.import_module("gradio")))

import gradio as gr
print(f"✅ Gradio version at runtime: {gr.__version__}")

BACKEND_URL = "https://proffbot.onrender.com/chat"
SESSION_ID = str(uuid.uuid4())

image_data = ""
image_path = "assets/profile_pic_base64.txt"

if os.path.exists(image_path):
    with open(image_path, "r") as f:
        image_data = f.read().strip()
else:
    print("⚠️ Warning: profile_pic_base64.txt not found.")


def chat_with_backend(message, history):
    formatted_history = []
    for turn in history:
        if turn[0] is not None and turn[1] is not None:
            formatted_history.append({"role": "user", "content": turn[0]})
            formatted_history.append({"role": "assistant", "content": turn[1]})

    payload = {
        "message": message,
        "history": formatted_history,
        "session_id": SESSION_ID, 
        "clear": False
    }

    try:
        response = requests.post(BACKEND_URL, json=payload)
        data = response.json()
        reply = data.get("response", ["Sorry, something went wrong."])
        reply = [r for r in reply if isinstance(r, str)]
    
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            print(f"❌ Backend error: {e.response.status_code} - {e.response.text}")
        reply = f"Error: {e}"


    return reply


css = """ * Hide fullscreen icon * #logo-img button.svelte-1ipelgc { display: none !important;}

/* Send button container and style */
                #custom-send-btn > .prose button {
                    background-color: #1E90FF !important;
                    color: white !important;
                    font-size: 16px !important;
                    font-weight: bold !important;
                    height: 52px !important;
                    width: 100% !important;
                    border: none !important;
                    border-radius: 6px !important;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
                    padding: 12px 16px !important;
                    cursor: pointer !important;
                }

#custom-send-btn > .prose button:hover {
    background-color: #1C86EE !important;
}

/* Clear button style */
    #clear-btn > .prose button {
        margin-top: 10px !important;
        font-size: 14px !important;
        padding: 12px !important;
        font-weight: bold !important;
        width: 100% !important;
        background-color: #444 !important;
        color: white !important;
        border-radius: 6px !important;
    }
    """



with gr.Blocks(css=css) as demo:
    
    with gr.Row():
        with gr.Column(scale=0, min_width=100):
            gr.HTML(
                f"""
                <div id='logo-img'>
                    <img src="data:image/png;base64,{image_data}"
                        style="max-width:80px; max-height:80%; object-fit:contain; border-radius:8px;" />
                </div>
                """
            )
        with gr.Column(scale=1):
            gr.HTML("""
                <div style="display: flex; align-items: center;">
                    <div style="margin-left: 10px;">
                        <h3 style="margin: 0;">I am the proffesional Digital Twin of Adnan Latif</h3>
                        <p style="margin: 4px 0;"> Curious about my professional story? <br>
                        I've navigated seismic data, neural networks, and corporate strategy — sometimes all in the same week. <br>
                        Ask me about my life through Geoscience, AI, and Leadership.....Or just say hi and see where we end up.</p>
                    </div>
                </div>
            """)

    chatbot = gr.Chatbot(height=400, label="Conversation with Adnan")

    with gr.Row():
        msg = gr.Textbox(placeholder="Type your question here...", show_label=False, scale=5)
        send_btn = gr.Button("Send", elem_id="custom-send-btn", scale=1)

    with gr.Row():
        clear_btn = gr.Button("🧹 Clear Chat", elem_id="clear-btn", scale=1)

    def user_input(user_message, chat_history):
        reply = chat_with_backend(user_message, chat_history)

        if isinstance(reply, str):
            chat_history.append((user_message, reply))

        elif isinstance(reply, list):
            if reply:
                chat_history.append((user_message, reply[0]))
                for extra in reply[1:]:
                    chat_history.append((None, extra))
            else:
                chat_history.append((user_message, "Sorry, no response."))
        else:
            chat_history.append((user_message, str(reply)))
        return "", chat_history


    send_btn.click(user_input, [msg, chatbot], [msg, chatbot])
    msg.submit(user_input, [msg, chatbot], [msg, chatbot])

    def clear_chat():
        try:
            payload = {
                "message": "clear_request", 
                "history": [],
                "session_id": SESSION_ID,
                "clear": True
            }
            requests.post(BACKEND_URL, json=payload)
            print("🧹 Chat and session state cleared.")
        except Exception as e:
            print("Clear error:", e)
        return []


    clear_btn.click(clear_chat, None, chatbot, queue=False)




if __name__ == "__main__":
    demo.launch()

