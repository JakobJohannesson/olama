import streamlit as st
import ollama
import subprocess

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
def stream_response(model, messages, placeholder, full_response, update_frequency=5):
    """
    Streams the response from the model and displays it in the Streamlit placeholder.
    Parameters:
        model (str): The model to use for generating the response.
        messages (list): The messages to send to the model.
        placeholder (st.empty): The Streamlit placeholder to display the response.
        full_response (str): The accumulated full response so far.
        update_frequency (int): Number of chunks after which to update the display.
    Returns:
        str: The updated full response.
    """
    try:
        stream = ollama.chat(model=model, messages=messages, stream=True)
        partial_response = []
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

    return full_response

# Function to create a new file with the given content
def create_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)

# Function to execute a Python file and return its output
def execute_python_file(filename):
    try:
        result = subprocess.run(['python', filename], capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return "", str(e)

# Streamlit app
st.title("Code Review Loop with Supervisor")
st.write("**Left**: CodeLlama's Response (Python Script)\n\n**Right**: Supervisor's Feedback (llama3)")

col1, col2 = st.columns(2)

# Initialize the messages
coder_initial_message = [
    {"role": "system", "content": "You are a Python developer."},
    {"role": "user", "content": "Write a Python script that prints 'Hello, World!'."}
]

# Function to handle the review loop
def handle_review_loop(coder_message, supervisor_message, coder_placeholder, supervisor_placeholder, update_frequency=5):
    coder_full_response = ""
    supervisor_full_response = ""
    iteration = 0

    while True:
        iteration += 1
        st.write(f"### Iteration {iteration}")

        # CodeLlama writes Python script
        coder_full_response = stream_response('codellama', coder_message, coder_placeholder, "", update_frequency)
        create_file('hello_world.py', coder_full_response)

        # Execute the Python script and check the output
        stdout, stderr = execute_python_file('hello_world.py')
        st.write(f"**Output of the script:**\n{stdout}")
        if stderr:
            st.write(f"**Error:**\n{stderr}")

        # Supervisor reviews the code and provides feedback
        supervisor_message = [
            {"role": "system", "content": "You are a code reviewer."},
            {"role": "user", "content": f"Please review the following Python script and provide feedback. The script should print 'Hello, World!' as its output: {coder_full_response}"}
        ]
        supervisor_full_response = stream_response('llama3', supervisor_message, supervisor_placeholder, "", update_frequency)

        # Check if supervisor says the assignment is complete
        if any(phrase in supervisor_full_response.lower() for phrase in ["assignment is completed", "no issues found", "perfect", "a+", "assignment is complete"]):
            st.write("### The assignment is completed.")
            break

        # CodeLlama adjusts the code based on supervisor's feedback
        coder_message = [
            {"role": "system", "content": "You are a Python developer."},
            {"role": "user", "content": f"Adjust the following Python script based on the feedback: {supervisor_full_response}. Ensure it prints 'Hello, World!'."}
        ]

# Placeholders for responses
coder_placeholder = col1.empty()
supervisor_placeholder = col2.empty()

# Start the review loop
handle_review_loop(coder_initial_message, [], coder_placeholder, supervisor_placeholder, update_frequency=3)