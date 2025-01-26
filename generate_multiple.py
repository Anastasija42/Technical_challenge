"""
Module: generate_multiple
This module provides functionality to generate multiple unique questions from given data chunks, 
save them to JSON and text files, and print the generated questions in a specific format.
Functions:
    generate_unique_question(chunk, existing_answers, yes_count, yes):
        Generates a unique question that is not contextually similar to existing answers.
    generate_multiple_questions(chunk, num_questions=5):
        Generates multiple unique questions from a given data chunk.
    generate_questions_for_all_chunks(data):
        Generates questions for all chunks in the provided data.
    save_questions_to_file(input_json, output_txt):
        Saves questions from a JSON file to a text file in a specific format.
"""

import json
import random
import os
import time
from datetime import datetime

from llm_api import model
from tools import fix_malformed_json
from prompt import CHECK_IF_SIMILAR
from generate_one import generate_question

def generate_unique_question(chunk, existing_answers,yes_count, yes):
    """
    Generates a unique question that is not contextually similar to existing answers.

    Args:
        chunk (dict): A dictionary containing information about the text chunk.
        existing_answers (set): A set of existing answers to compare for similarity.
        yes_count (int): The count of 'Yes' responses for contextual similarity.
        yes (bool): A flag indicating if the question is contextually similar.

    Returns:
        dict: A dictionary containing the generated question data.
        int: The updated count of 'Yes' responses for contextual similarity.
        bool: A flag indicating if the question is contextually similar.
    """
    while True:
        question_data = generate_question(chunk)
        # Error in the JSON dataset - skip this chunk
        if 'error' in question_data:
            yes_count = 3
            yes = True
            return question_data, yes_count, yes

        response_answer = model.generate_content(CHECK_IF_SIMILAR.format(
            answer_option=question_data['correct_answer'],
            answer_set=", ".join(existing_answers)))

        if response_answer.text.startswith("Contextually Similar: Yes"):
            yes = True
            yes_count += 1
        return question_data, yes_count, yes

def generate_multiple_questions(chunk, num_questions = 5, minimum = 3, max_yes = 2):
    """
    Generates multiple unique questions from a given data chunk.

    Args:
        chunk (dict): A dictionary containing information about the text chunk.
        num_questions (int): The number of questions to generate.
        minimum (int): The minimum number of questions to generate.
        max_yes (int): The maximum number of 'Yes' responses for contextual similarity.

    Returns:
        list: A list of dictionaries containing the generated question data.
    """
    questions = []
    existing_answers = set()
    yes_count = 0
    for i in range(num_questions):
        yes = False
        question_data, yes_count, yes = generate_unique_question(chunk,
                                                                 existing_answers,
                                                                 yes_count, yes)
        if i >= minimum and yes_count >= max_yes:
            return questions

        if not yes:
            questions.append(question_data)
            existing_answers.add(question_data.get('correct_answer'))
        else:
            continue
    return questions


# Function to generate questions for all chunks
def generate_questions_for_all_chunks(data):
    """
    Generates questions for all chunks in the provided data.

    Args:
        data (list): A list of dictionaries containing information about text chunks.

    Returns:
        list: A list of dictionaries containing the generated question data for each chunk.
    """
    all_questions = []
    for chunk in data:
        if chunk['type'] == 'chunk':
            question_data = generate_multiple_questions(chunk)
            # Sleep for 1 minute to avoid rate limiting - adjustment in the documentation
            time.sleep(60)
            all_questions.append(question_data)
    return all_questions

def save_questions_to_file(input_json, output_txt):
    """
    Saves questions from a JSON file to a text file in a specific format.

    Args:
        input_json (str): The path to the JSON file containing the questions.
        output_txt (str): The path to the text file to save the questions to.
    """

    with open(input_json, 'r', encoding='utf-8') as json_file:
        all_questions = json.load(json_file)

    with open(output_txt, 'w', encoding='utf-8') as txt_file:
        for _, questions in enumerate(all_questions):
            try:
                for i, question in enumerate(questions):
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
                    txt_file.write(f"Question n. {question['index']}.{i}: {question['question']}\n")
                    txt_file.write(f"A: {answers[0]}\n")
                    txt_file.write(f"B: {answers[1]}\n")
                    txt_file.write(f"C: {answers[2]}\n")
                    txt_file.write(f"D: {answers[3]}\n")
                    # Find the new label for the correct answer
                    correct_label = 'ABCD'[answers.index(question['correct_answer'])]
                    txt_file.write(f"Correct Answer: {correct_label}\n\n")
            except KeyError as e:
                print(f"KeyError: Missing key {e} in question {question}")
            except IndexError as e:
                print(f"IndexError: {e} in question {question}")
            except TypeError as e:
                print(f"TypeError: {e} in question {question}")
            except ValueError as e:
                print(f"ValueError: {e} in question {question}")

# Load the data from a JSON file
FILE_PATH = "data/machine_learning_for_healthcare.json"
base_name = os.path.basename(FILE_PATH).split('.')[0]
print(base_name)
loaded_data = fix_malformed_json(FILE_PATH)

# Generate questions for all chunks
gen_questions = generate_questions_for_all_chunks(loaded_data)

# Generate file names based on the file path and timestamp
base_name = os.path.basename(FILE_PATH).split('.')[0]
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
JSON_FILE_NAME = os.path.join('generated_questions',
                              f"{base_name}_multiple_questions_{timestamp}.json")
TXT_FILE_NAME = os.path.join('generated_questions',
                             f"{base_name}_multiple_questions_{timestamp}.txt")

# Save all questions to a JSON file
with open(JSON_FILE_NAME, 'w', encoding='utf-8') as json_file_:
    json.dump(gen_questions, json_file_, ensure_ascii=False, indent=4)

# Save all questions to a text file
save_questions_to_file(JSON_FILE_NAME, TXT_FILE_NAME)
