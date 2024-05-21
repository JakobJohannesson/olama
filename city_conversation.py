import streamlit as st
import ollama

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
        placeholder.markdown(f"An error occurred while fetching the response: {e}")

# Streamlit app
st.title("Favorite City Conversation")
st.write("**Left**: Intern's Response\n\n**Right**: Manager's Response")

col1, col2 = st.columns(2)

# Initialize the conversation
conversation = [
    {"role": "user", "content": "Your favorite city is London. Your goal is to figure out the other person's favorite city without directly telling your own. Never ever tell what your favorite city is."},
    {"role": "user", "content": "Your favorite city is Mumbai. This is your secret which others are trying to figure out. Let's talk about our favorite cities. What's yours?"}
]

# Function to handle the back-and-forth conversation
def handle_conversation(conversation, model, intern_placeholder, manager_placeholder, update_frequency=5):
    intern_full_response = ""
    manager_full_response = ""

    for i in range(5):  # Limit to 5 exchanges for brevity
        # Intern responds
        intern_response = []
        stream_response(model, conversation, intern_placeholder, update_frequency)
        intern_full_response += "".join(intern_response)
        conversation.append({"role": "assistant", "content": intern_full_response})
        intern_placeholder.markdown(intern_full_response)

        # Manager responds
        manager_response = []
        stream_response(model, conversation, manager_placeholder, update_frequency)
        manager_full_response += "".join(manager_response)
        conversation.append({"role": "assistant", "content": manager_full_response})
        manager_placeholder.markdown(manager_full_response)

# Placeholders for responses
intern_placeholder = col1.empty()
manager_placeholder = col2.empty()

# Start the conversation
handle_conversation(conversation, 'llama3', intern_placeholder, manager_placeholder, update_frequency=3)