"""
Multiple-Choice Question Prompt for Learning
"""

PROMPT = """
You are an AI assistant tasked with creating multiple-choice questions for learning.
You are given a chunk of text, a brief summary of that text, the main topic it belongs to, and a subtopics.

Generate a single multiple-choice question with the following properties:
- All the needed context must be in the question itself. Students don't see the text or summary.
- One True Answer: The correct answer must be directly supported by the information in the text and/or summary provided. Give an explanation for why this option is correct.
-Three Plausible Distractors: 
    - The incorrect answer options must be related to the main topic or subtopic.
    - They should be plausible, common misconceptions, or something a reader might easily confuse.
    - They should not simply be direct negations of the text, nor should they be generally true statements that might confuse the student. 
    - You also need to give explanations for why each distractor is incorrect, but relevant to the question.

Here's the information:

Text Chunk: "{text}"

Summary: "{summary}"

Main Topic: "{main_topic}"

Subtopic: "{subtopics}"

The questions should be clear and give all the information needed, not requiring the reader to refer back to the context.
The question MUST NOT containt the folowing or similar phrases:
"According to the text", "Based on the provided text", "According to the lecture slides", "as discussed", "as highlighted in the provided material",
"In this lecture", "according to the provided information", "key focus of the discussion"
Instead, directly ask the questions. Do NOT specify which lecture, text, or source the question is based on. 
They don't know which text you are referring to, nor the context outside of the question.

Your Output Should Be Formatted as Follows:

Question: [Insert the multiple choice question here]

A: [Answer Option A]

B: [Answer Option B]

C: [Answer Option C]

D: [Answer Option D]

Correct Answer: [The letter of the correct answer A, B, C, or D]

A: [Explanation for this option]

B: [Explanation for this option]

C: [Explanation for this option]

D: [Explanation for this option]
"""
CHECK_IF_SIMILAR = """
Analyze if the answer options is contextually similar to a option from the answer set. 
Contextual similarity means that, while the wording may differ, the underlying meaning, concept, or information conveyed is essentially the same.
If the answer set is empty, the answer isn't contextually similar to any other answer.

Input:

Answer Option: {answer_option}

Answer Set: {answer_set}

The output should be in the next format:

Contextually Similar: [Yes/No]
Explanation: [Explanation of why the answer is contextually similar or not]
"""
