"""import openai

def main():
    openai.api_key = 'secret key'

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Updated model name
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "show me the compliance status of each mandatory courses with each person"}
        ],
        max_tokens=150
    )

    print(response.choices[0].message['content'])

if __name__ == "__main__":
    main()
"""

import os
import openai
from dotenv import load_dotenv
from prompt_generator import read_multiple_csv_data, generate_prompt_from_chunk
from retriever import retrieve_relevant_data

# Load environment variables from .env file
load_dotenv()
openai.api_key = "secret key"
def get_openai_chat_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",  # You can change the model if needed
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
    )
    return response['choices'][0]['message']['content'].strip()


def process_large_data(df, chunk_size=100):
    num_chunks = (len(df) + chunk_size - 1) // chunk_size
    data_chunks = []
    
    for i in range(num_chunks):
        chunk = df[i * chunk_size: (i + 1) * chunk_size]
        data_chunks.append(chunk)
        
    #print(data_chunks)
    return data_chunks

def main():
    # Directory containing CSV files
    csv_directory = 'Sample_Data/'
    
    # Read data from multiple CSV files
    df = read_multiple_csv_data(csv_directory)
    
    # Process the large data into chunks
    data_chunks = process_large_data(df)

    print("Enter 'exit' to end the chat.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        
        # Choose a data chunk to include in the prompt
        chunk_index = 0  # You can choose the chunk dynamically if needed
        chunk = data_chunks[chunk_index]
        
        # Generate the prompt from user input and data chunk
        prompt = generate_prompt_from_chunk(chunk, user_input)
        
        #relevant_data = retrieve_relevant_data(user_input, df)
        #context = "\n\n".join(relevant_data)
        #prompt = f"{context}\n\nUser Query: {user_input}"
        
        # Get response from OpenAI
        result = get_openai_chat_response(prompt)
        #print(prompt)
        print(f"OpenAI: {result}")

if __name__ == "__main__":
    main()


