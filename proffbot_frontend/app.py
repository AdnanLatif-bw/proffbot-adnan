import gradio as gr
import requests
import os

BACKEND_URL = "https://proffbot.onrender.com/chat"
logo_path = os.path.join("file", "assets", "profile_pic.jpg")

def chat_with_backend(message, history):
    formatted_history = []
    for turn in history:
        formatted_history.append({"role": "user", "content": turn[0]})
        formatted_history.append({"role": "assistant", "content": turn[1]})

    payload = {
        "message": message,
        "history": formatted_history
    }

    try:
        response = requests.post(BACKEND_URL, json=payload)
        response.raise_for_status()
        reply = response.json()["response"]
    except Exception as e:
        reply = f"Error: {e}"

    return reply

css="""
#logo-img button.svelte-1ipelgc {
    display: none !important;  /* Hide fullscreen icon */
}

#send-btn button, #clear-btn button {
    font-size: 12px !important;
    padding: 0px 0px !important;
    height: 10px !important;
    width: 25%;
    margin-bottom: 4px;
}

#clear-btn button {
    margin-top: 2px;
}
"""

with gr.Blocks(title="Proffesional Digital Twin", css=css) as demo:
    
    with gr.Row():
        with gr.Column(scale=0, min_width=100):  # Logo
            gr.Image(
                value="assets/profile_pic.jpg",
                show_label=False,
                show_download_button=False,
                show_share_button=False,
                show_fullscreen_button=False,
                height=100,
                width=100,
                container=False,
                elem_id="logo-img",
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

    chatbot = gr.Chatbot(height=500, label="Conversation")

    with gr.Row():
        msg = gr.Textbox(placeholder="Type your question here...", show_label=False, scale=5)
        with gr.Column(scale=1):
            with gr.Row():
                send_btn = gr.Button("Send", elem_id="send-btn")
            with gr.Row():
                clear_btn = gr.Button("Clear", elem_id="clear-btn")


    def user_input(user_message, chat_history):
        reply = chat_with_backend(user_message, chat_history)
        chat_history.append((user_message, reply))
        return "", chat_history

    send_btn.click(user_input, [msg, chatbot], [msg, chatbot])
    msg.submit(user_input, [msg, chatbot], [msg, chatbot])
    clear_btn.click(lambda: None, None, chatbot, queue=False)


if __name__ == "__main__":
    demo.launch()

