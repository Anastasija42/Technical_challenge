"""
tools.py
This module contains utility functions for handling JSON data and parsing multiple-choice questions.
Functions:
    fix_malformed_json(file_path):
        Fixes a malformed JSON file containing multiple root objects and loads it into a 
        Python list of dictionaries.
    parse_question(text):
        Parses a multiple-choice question from a given text input and returns a dictionary 
        containing the question, options, correct answer, distractors, and explanations.
"""

import json
import re

def fix_malformed_json(file_path):
    """
    Fixes a malformed JSON file containing multiple root objects and 
    loads it into a Python list of dictionaries.
    This function addresses the issue of JSON files that have multiple root objects 
    by wrapping them in an array
    and ensuring proper comma separation between objects. It then attempts to parse 
    the fixed JSON string.
    Args:
        file_path (str): The path to the JSON file to be fixed and loaded.
    Returns:
        list: A list of dictionaries representing the fixed JSON objects if parsing is successful.
        None: If there is an error in parsing the JSON, None is returned 
        and an error message is printed.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        json_string = file.read()

    # Step 1: Wrap JSON objects in an array
    fixed_json_string = f"[{json_string}]"

    # Step 2: Remove newlines between objects and add commas
    fixed_json_string = re.sub(r'}\s*{', r'},{', fixed_json_string)

    # Step 3: Parse the fixed JSON
    try:
        return json.loads(fixed_json_string)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

# Example usage
FILE_PATH = "data/economics.json" # "data/machine_learning_for_healthcare.json"
data = fix_malformed_json(FILE_PATH)

if data:
    print("Fixed JSON loaded successfully!")
    #print(json.dumps(data, indent=4))  # Pretty-print for inspection
else:
    print("Failed to fix and load JSON.")

def parse_question(text):
    """
    Parses a multiple-choice question from a given text input.

    Args:
        text (str): The text containing the multiple-choice question.

    Returns:
        dict: A dictionary containing the question, options, correct answer,
                distractors, and explanations.
    """

    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]

    if len(lines) < 10:
        raise ValueError("Input text does not have the expected number of lines.")
    question = lines[0].replace('Question: ', '').strip()
    options = {line[0]: line[3:].strip() for line in lines[1:5]}
    explanations = {line[0]: line[3:].strip() for line in lines[6:10]}
    correct_answer = lines[5].replace('Correct Answer: ', '').strip()
    if correct_answer not in options:
        raise ValueError("Correct answer key is not in the options.")
    # Create a list of distractors excluding the correct answer
    distractors = [options[key] for key in options if key != correct_answer]

    if len(distractors) < 3:
        raise ValueError("Not enough distractors available.")
    question_data = {
        'question': question,
        'correct_answer': options[correct_answer],
        'correct_explanation': explanations[correct_answer],
        'distractor1': distractors[0],
        'distractor1_explanation': explanations[[key for key in options 
                                                 if options[key] == distractors[0]][0]],
        'distractor2': distractors[1],
        'distractor2_explanation': explanations[[key for key in options 
                                                 if options[key] == distractors[1]][0]],
        'distractor3': distractors[2],
        'distractor3_explanation': explanations[[key for key in options 
                                                 if options[key] == distractors[2]][0]]
    }

    return question_data
