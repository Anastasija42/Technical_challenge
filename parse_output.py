"""
This script parses a multiple-choice question from a given text input.
It extracts the question, options, correct answer, and explanations,
and organizes them into a structured dictionary format.
"""

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

# Example usage
TEXT = """Question: [Insert the multiple choice question here]

A: [Answer Option A]

B: [Answer Option B]

C: [Answer Option C]

D: [Answer Option D]

Correct Answer: D

A: [Explanation for Option A]

B: [Explanation for Option B]

C: [Explanation for Option C]

D: [Explanation for Option D]
"""

print(parse_question(TEXT))
