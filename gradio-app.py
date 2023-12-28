import json
import gradio as gr
from llm_service import LLMService

# Initialize the LLMService object with the configuration
with open('config.json') as f:
    cfg = json.load(f)
    solver = LLMService(cfg)

# Function for generating LLM response
def generate_response(message, history):
    answer = solver.content_query(message)
    return answer

def upload_file(file,):
    try:
        # Call the method to upload custom knowledge
        # Assuming the method takes a file path as an argument
        solver.upload_file_knowledge(file)
        return "File uploaded and custom knowledge has been processed successfully!"
    except Exception as e:
        return f"An error occurred while processing the file: {e}"


demo = gr.ChatInterface(
    generate_response,
    title="Alibaba Cloud RAG - Knowledge Base System",
    description="Ask anything based on my knowledge which uploaded to the Vector DB",
    theme="soft",
    examples=["Hello, tell me about Alibaba Cloud PAI", "How can I run QWen 7B", "What can I do with EasyCV?"],
    )

with demo:
    with gr.Row():
        with gr.Column(scale=1, min_width="15%"):  # Set a minimum width for the upload button column
            file_input = gr.File(label="Upload File", type="filepath", file_types=["txt", ".md", ".csv", ".pdf", ".html"])

            # Define the event listener for the file upload.
            # When a file is uploaded, 'upload_file' function is called and the returned value is displayed.
            file_input.change(
                fn=upload_file,
                inputs=file_input,
            )


if __name__ == "__main__":
    demo.launch()
# gradio gradio-app.py