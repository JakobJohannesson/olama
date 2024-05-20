# Import required libraries
import streamlit as st
from autogen import AssistantAgent

# Configuration list for llama3 model
config_list = [
    {
        "model": "llama3",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
    }
]

# Initialize the intern (Assistant Agent)
intern = AssistantAgent("intern", llm_config={"config_list": config_list})

# Initialize the manager (Warren Buffett)
manager = AssistantAgent("WarrenBuffett", llm_config={"config_list": config_list})


# Define the messages for generating an equity research paper
intern_message = """
Please write a draft of an equity research paper that includes the following:
1. Background on the operations of the business.
2. A table with the stock price information for the company, including:
   - Date
   - Opening Price
   - Closing Price
   - High
   - Low
   - Volume
3. Provide a detailed analysis of the stock performance and future outlook.

Company: Apple Inc
"""


import streamlit as st
import ollama
import time

# Function to generate response from stream
def generate_response(stream):
    """
    Extracts the content from the stream of responses.
    Parameters:
        stream: The stream of responses from the model.
    Yields:
        str: The content of each chunk.
    """
    for chunk in stream:
        if 'message' in chunk and 'content' in chunk['message']:
            yield chunk['message']['content']

# Function to concatenate and display partial responses
def concatenate_partial_response(partial_response, full_response, placeholder):
    """
    Concatenates the partial response into a single string and updates the placeholder.
    Parameters:
        partial_response (list): The chunks of the response.
        full_response (str): The accumulated full response so far.
        placeholder (st.empty): The Streamlit placeholder to update the display.
    Returns:
        str: The concatenated response.
    """
    str_response = "".join(partial_response)
    full_response += str_response
    placeholder.markdown(full_response)
    return full_response

# Function to stream response and display in Streamlit
def stream_response(model, messages, placeholder):
    """
    Streams the response from the model and displays it in the Streamlit placeholder.
    Parameters:
        model (str): The model to use for generating the response.
        messages (list): The messages to send to the model.
        placeholder (st.empty): The Streamlit placeholder to display the response.
    """
    try:
        stream = ollama.chat(model=model, messages=messages, stream=True)
        partial_response = []
        full_response = ""
        gen_stream = generate_response(stream)
        
        for chunk_content in gen_stream:
            partial_response.append(chunk_content)
            if '\n' in chunk_content:
                full_response = concatenate_partial_response(partial_response, full_response, placeholder)
                partial_response = []

        if partial_response:
            full_response = concatenate_partial_response(partial_response, full_response, placeholder)
    
    except Exception as e:
        placeholder.error(f"An error occurred while fetching the response: {e}")

# Streamlit app
st.title("Equity Research Paper Collaboration")
st.write("**Left**: Intern's Response (Draft)\n\n**Right**: Manager's Feedback (Warren Buffett)")

col1, col2 = st.columns(2)

# Define the messages for generating an equity research paper
intern_message = {
    'role': 'user',
    'content': """
    Please write a draft of an equity research paper that includes the following:
    1. Background on the operations of the business.
    2. A table with the stock price information for the company, including:
       - Date
       - Opening Price
       - Closing Price
       - High
       - Low
       - Volume
    3. Provide a detailed analysis of the stock performance and future outlook.

    Company: Apple Inc
    """
}

manager_message = {
    'role': 'user',
    'content': """
    Provide feedback on the draft equity research paper written by the intern. Make sure to use a fundamental research approach and give detailed input on areas that need improvement or further analysis.
    """
}

# Stream the intern's response
with col1:
    st.subheader("Intern's Response")
    intern_placeholder = st.empty()
    stream_response(model='llama3', messages=[intern_message], placeholder=intern_placeholder)

# Stream the manager's feedback
with col2:
    st.subheader("Manager's Feedback")
    manager_placeholder = st.empty()
    stream_response(model='llama3', messages=[manager_message], placeholder=manager_placeholder)