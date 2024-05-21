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
def stream_response(model, messages, placeholder, update_frequency=5):
    """
    Streams the response from the model and displays it in the Streamlit placeholder.
    Parameters:
        model (str): The model to use for generating the response.
        messages (list): The messages to send to the model.
        placeholder (st.empty): The Streamlit placeholder to display the response.
        update_frequency (int): Number of chunks after which to update the display.
    """
    try:
        stream = ollama.chat(model=model, messages=messages, stream=True)
        partial_response = []
        full_response = ""
        gen_stream = generate_response(stream)
        
        chunk_count = 0
        for chunk_content in gen_stream:
            partial_response.append(chunk_content)
            chunk_count += 1
            
            # Update more frequently by checking chunk count
            if chunk_count >= update_frequency:
                full_response = concatenate_partial_response(partial_response, full_response, placeholder)
                partial_response = []
                chunk_count = 0

        if partial_response:
            full_response = concatenate_partial_response(partial_response, full_response, placeholder)
    
    except Exception as e:
        placeholder.error(f"An error occurred while fetching the response: {e}")

# Streamlit app
st.title("Equity Research Paper Collaboration")
st.write("**Left**: Intern's Response (Draft)\n\n**Right**: Manager's Feedback (Warren Buffett)")

col1, col2 = st.columns(2)

# Define the segments of the equity research paper
segments = [
    {
        'role': 'user',
        'content': """
        Please write the introduction and background of the Apple's operations. write at most 1 sentences.
        """
    },
    {
        'role': 'user',
        'content': """
        Provide a detailed analysis of the Apple's financial performance. write at most 1 sentences.
        """
    },
    {
        'role': 'user',
        'content': """
        Discuss the competitive landscape and the Apple's market position. write at most 1 sentences.
        """
    },
    {
        'role': 'user',
        'content': """
        Analyze the Apple's stock price performance and provide a future outlook. write at most 1 sentences.
        """
    }
]

# Stream responses back and forth for each segment
for segment in segments:
    # Stream the intern's response
    with col1:
        st.subheader("Intern's Response")
        intern_placeholder = st.empty()
        stream_response(model='codellama', messages=[segment], placeholder=intern_placeholder, update_frequency=3)

    # Stream the manager's feedback
    with col2:
        st.subheader("Manager's Feedback")
        manager_placeholder = st.empty()
        manager_feedback_message = {
            'role': 'user',
            'content': f"Provide feedback on the following segment: {segment['content']}"
        }
        stream_response(model='llama3', messages=[manager_feedback_message], placeholder=manager_placeholder, update_frequency=3)