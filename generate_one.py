"""
This module provides functionality to generate questions from text chunks using a language model.
It includes functions to generate questions for individual chunks, 
save the generated questions to JSON and text files,
and handle malformed JSON data.
Functions:
- generate_question(chunk): Generates a question from a given text chunk.
- save_to_json(data, file_name): Saves data to a JSON file.
- generate_questions_for_all_chunks(data): Generates questions for all 
text chunks in the provided data.
- fix_malformed_json(file_path): Fixes malformed JSON data from the specified file path.
- parse_question(response_text): Parses the response text to extract question data.
Constants:
- FILE_PATH: The path to the JSON file containing the data to be processed.

"""
import json
import random
import os
from datetime import datetime

from llm_api import model
from tools import fix_malformed_json, parse_question
from prompt import PROMPT

def generate_question(chunk):
    """
    Generates a multiple-choice question from a given text chunk.

    Args:
        chunk (dict): A dictionary containing information about the text chunk.

    Returns:
        dict: A dictionary containing the generated question data.
    """
    context = chunk['content']
    text = context.get('text', 'N/A')
    summary = context.get('summary', 'N/A')
    main_topic = context.get('main_topic', 'N/A')
    subtopics = context.get('subtopics', 'N/A')

    index = chunk['chunk_index']

    response = model.generate_content(PROMPT.format(text=text,
                                                    summary=summary,
                                                    main_topic=main_topic,
                                                    subtopics=", ".join(subtopics)))
    response_text = response.text

    try:
        question_data = parse_question(response_text)
    except ValueError as e:
        question_data = {'error': str(e)}
    question_data['index'] = index

    return question_data

def save_to_json(data, file_name):
    """
    Saves data to a JSON file.

    Args:
        data (dict): The data to be saved.
        file_name (str): The name of the JSON file to save the data to.
    """
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_to_txt(all_questions, file):
    """
    Saves the generated questions to a text file in the format that the model returns.

    Args:
        all_questions (list): A list of dictionaries containing the generated question data.
        txt_file (file): The text file to write the questions to.
    """
    for question in all_questions:
        if 'error' in question:
            file.write(f"Error: {question['error']}\n\n")
            continue
        # Create a list of answers
        answers = [
            question['distractor1'],
            question['distractor2'],
            question['distractor3'],
            question['correct_answer']
            ]
        # Shuffle the answers
        random.shuffle(answers)
        # Write the question and answers to the file
        txt_file.write(f"Question: {question['question']}\n")
        txt_file.write(f"A: {answers[0]}\n")
        txt_file.write(f"B: {answers[1]}\n")
        txt_file.write(f"C: {answers[2]}\n")
        txt_file.write(f"D: {answers[3]}\n")
        # Find the new label for the correct answer
        correct_label = 'ABCD'[answers.index(question['correct_answer'])]
        file.write(f"Correct Answer: {correct_label}\n\n")


# Function to generate questions for all chunks
def generate_questions_for_all_chunks(data):
    """
    Generates questions for all text chunks in the provided data.

    Args:
        data (list): A list of dictionaries containing information about text chunks.

    Returns:
        list: A list of dictionaries containing the generated question data for each chunk.
    """
    all_questions = []
    for chunk in data:
        if chunk['type'] == 'chunk':
            question_data = generate_question(chunk)
            all_questions.append(question_data)
    return all_questions


# Load the data from a JSON file
FILE_PATH = "data/economics.json"
loaded_data = fix_malformed_json(FILE_PATH)

# Generate questions for all chunks
questions = generate_questions_for_all_chunks(loaded_data)

# Generate file names based on the file path and timestamp
base_name = os.path.basename(FILE_PATH).split('.')[0]
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
JSON_FILE_NAME = os.path.join('generated_questions',
                              f"{base_name}_questions_{timestamp}.json")
TXT_FILE_NAME = os.path.join('generated_questions',
                             f"{base_name}_questions_{timestamp}.txt")

# Save all questions to a JSON file
with open(JSON_FILE_NAME, 'w', encoding='utf-8') as json_file:
    json.dump(questions, json_file, ensure_ascii=False, indent=4)

# Print all questions to a text file in the format that the model returns
with open(TXT_FILE_NAME, 'w', encoding='utf-8') as txt_file:
    save_to_txt(questions, txt_file)

# Print the path of the generated files
print(f"Questions saved to {JSON_FILE_NAME} and {TXT_FILE_NAME}")
