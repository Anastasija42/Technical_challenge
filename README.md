# Technical Challenge - solution

Candidate: Anastasija Rakić

# Analysis of the objective

AI models have advanced to a point where they can generate high-quality questions and answers solely through effective prompt engineering.

- The first approach was to make sure that the questions themselves contained all the information needed to answer them and not refer back to the text and other information provided for generating:

<aside>

👍
```
Question: Which treaty primarily aimed to prepare the European Union's institutions for the 2004 enlargement?
A: The Treaty of Maastricht (1992)
B: The Treaty of Nice (2001)
C: The Treaty of Lisbon (2007)
D: The Treaty of Amsterdam (1997)

Correct Answer: B
```
</aside>

Besides the wrong answer C (2007. being after 2004.), the other distractors seem plausible.

<aside>
👎
  
```
Question: What factor significantly contributed to the long-standing problems in Portugal's housing market, as described in the text?
A: Insufficient foreign direct investment (FDI) in the housing sector.
B: High interest rates making mortgages unaffordable for many citizens.
C: A complex interplay of interests among banks, construction firms, and municipalities.
D: A lack of government regulation in the construction industry.

Correct Answer: C
```
</aside>

Both questions were generated from the same prompt, and although the second format was less prominent, it was a point that needed to be considered.

- How detailed or specific should the questions be? Should particular types require different prompting?  (More about different prompting based on different types of study materials later)

With the specified format, the model effectively generates both highly specific questions and broader overview ones, often based on the main topics. An example of a broader question:

<aside>
↔️

```
Question: Which of the following is NOT a primary layer type found in a typical Convolutional Neural Network (CNN) architecture?
A: Pooling Layer
B: Convolutional Layer
C: Recurrent Layer
D: Fully-Connected Layer

Correct Answer: C
```
</aside>

- Are there constraints on the type of distractors (e.g., similar concepts, similar terms, synonyms, numerical errors,  or related concepts that are incorrect)?

Maybe the most important part is making the distractors plausible but untrue. They should not simply be direct negations of the text, nor should they be generally true statements that might confuse the student (when a question is vague enough that these answers could also be true, or the question is too specific to the provided text, so other true answers don’t apply). In the previous examples, the model generated pretty satisfactory distractors, the recurrent layer being a related concept, the treaty being in some European city… 

When developing a feature, it is natural and essential to create a method for **evaluating** it besides relying on human evaluation during development. LLM evaluators are very popular and showcase good results, but they are LLM calls that cost a certain amount. They could judge the clarity, difficulty, quality of distractors, and relevance with good prompting.  Feedback from users on specific questions would also be used to improve the questions.

As the questions should be only from the literature, there is no need to try to find additional information.  A RAG (retrieval-augmented generation) approach could be used for fact-checking, but I didn’t identify the need with the generated answers.

Since this is a proof-of-concept in development and there are only two documents, I will focus solely on the human (my) evaluation. One way to improve the generated distractors is to request that the LLM also describe why the distractors are untrue to the question - requesting it to make observations. It would use more tokens and cost more, but in the end, we can compare the quality of the questions.  

Besides ensuring the distractors are adequate, it could also be used for additional information when practicing—if a user fails to answer, he gets an explanation.

- How many questions are expected per paragraph/document?

At first, I generated only one question from one chunk, but I think it would be beneficial to generate as many as possible (as long as they make sense). They should also have an index of which chunk they are from, so when someone wants to practice, they can select just one from each part, so there is a reasonable amount, or they can specify which part they want to practice more, getting more questions from that part. I also thought of grading them by difficulty, but I haven’t explored it. 

When generating just one question for a chunk, I could generate questions for the whole document, but I was often met with exceeding the quota (I was using the free Gemini plan). That’s why I didn’t try to scale to handle large documents and process multiple paragraphs at once.

- Should the pipeline support multiple languages or only one?

The pipeline should eventually support multiple languages, but it's important to note that different languages present unique challenges and may require specific models tailored to their linguistic structures. To keep things manageable and ensure quality, it would be best to start with English initially and expand to other languages later.

# The implementation

### Different prompts for improvement?

The final prompt for generating questions is still simple but effective. It provides all the necessary context for truly answering; considering that university subjects are usually very broad, it must be this way. Still, an improvement for the future would be to keep the questions a little bit shorter so they don’t tire the student too much, and they sometimes explain the topic too much. When a specific problem is faced, it often helps to better the prompt with a few-shot examples - instead of this way, generate the question like this. It would also be beneficial to make different prompts for different kinds of questions - some simpler and straightforward, making them usually a little bit easier to answer, and others more complex and demanding of truly understanding the material. Due to limited time, I haven’t explored all the possibilities, but I felt the need to comment on them.  

### "Content Processing Error”

I noticed that two chunks in one of the JSON state a content processing error (*”This content could not be processed due to content filtering or other restrictions.”*). I am unsure if this happened due to the nature of the chunk (contains images or just bullet points), but this way, a lot of information is lost. If it's due to other kinds of restrictions, I just implemented some checks; if the chunk contains an error, it wouldn’t be looked at for the question generation.

### Multiple questions for a chunk

The first approach was to generate just one question from a chunk, but I knew that that way, so many potential questions would be lost. So, I developed the following principle:

It can generate a maximum number of questions per chunk, trying not to overuse the resource. Another way would be to state in the prompt how many questions I want and how different I want them, but that would be a little bit more unpredictable to parse and could lead to questions of less quality. 

An LLM evaluator checks if the new answer is similar to any of the already given answers. I found this to be the easiest way to differentiate between too-similar questions. 

If the maximum number of questions generated is 8, there is also a minimum, for example, 3.

A similar-question count also stops the generation after generating a similar question multiple times if the minimum question rate is reached. 

After running some tests, I found this solution satisfactory enough for this challenge due to my limited time, but it certainly can be improved.

Here is an example of generating multiple from one chunk and which questions didn’t pass the not-similar test.

<aside>
♊

A part of the example file “**repeating_questions_example.txt**”:
```
Question: A research study on clinical-grade decision support in computational pathology detailed a novel method for analyzing pathology images.  This method utilized extensive datasets (including CAMELYON16 and ImageNet), achieved high sensitivity and specificity (AUC of 0.989 for an ensemble model), and aimed to reduce pathologist workload by 75%.  Which of the following was NOT a key feature of this approach?
A: The approach was designed for seamless integration into existing clinical workflows.
B: The research successfully demonstrated improved generalization to real-world pathology data.
C: The method did not require manual annotations of pathology slides.
D: The study focused on microscopic analysis of single cells, specifically targeting nuclear features for cancer grading.

Correct Answer: D

*Contextually Similar: No
Explanation: The answer option describes a research methodology focusing on microscopic cell analysis for cancer diagnosis. The answer set presents a performance metric (AUC score) of a system, likely a machine learning model.  These are completely different concepts; one describes a research method, the other a system's performance.  There is no overlap in meaning or information.*

Question: A new clinical-grade decision support system for computational pathology was developed.  The system utilizes deep learning,  achieves high accuracy (AUC of 0.989 for an ensemble model in one example), and aims to improve the efficiency of pathology workflows.  Which of the following is NOT a key feature or outcome of this system as described?
A: The system operates without requiring manual annotations of images.
B: The system utilizes significantly larger datasets compared to previous studies in the field, leading to improved generalization.
C: The system primarily focuses on the manual classification of individual cells within tissue samples using a traditional microscopy-based approach.
D: The system's integration into clinical workflows was designed to reduce pathologist workload by approximately 75%.

Correct Answer: C

*Contextually Similar: Yes
Explanation:The answer option describes a manual, microscopy-based approach to classifying individual cells in tissue samples.  The first answer in the answer set ("The study focused on microscopic analysis of single cells, specifically targeting nuclear features for cancer grading") directly aligns with this. Both options describe a method of analyzing individual cells using microscopy.  While the answer option doesn't specify cancer grading or nuclear features, the core concept of manual microscopic analysis of single cells is shared.*
```
</aside>

The final output is a JSON file that includes comprehensive information for each question. This includes the question itself, the correct answer, distractors, explanations for both the correct answer and distractors and the index of the content chunk from which the question was generated.

<aside>
📖

```
{
    "question": "Frozen rents in Portugal, implemented in the 1950s, created which of the following market imbalances?",
    "correct_answer": "Excess demand for rental housing, coupled with reduced supply due to unattractive rental yields for landlords.",
    "correct_explanation": "This is the correct answer. The text explicitly states that frozen rents created excess demand for rental housing because prices did not reflect market forces. Simultaneously, the low rental yields discouraged landlords from offering their properties, leading to reduced supply.",
    "distractor1": "Increased housing supply and decreased demand, leading to lower construction activity.",
    "distractor1_explanation": "This option is incorrect because the frozen rents did not lead to increased housing supply; instead, they resulted in a contraction of supply. Landlords were not incentivized to offer rental properties due to low returns, leading to less construction. The market did not become more balanced but severely imbalanced.",
    "distractor2": "A balanced market where prices adjusted efficiently to meet supply and demand.",
    "distractor2_explanation": "This option is incorrect as it is the opposite of what happened.  The frozen rents prevented the market from adjusting through price signals, thus creating a major imbalance.",
    "distractor3": "Stimulated a rapid increase in homeownership among lower-income households.",
    "distractor3_explanation": "While frozen rents might seem to encourage homeownership, the passage highlights this as a negative consequence, leading to issues with labor mobility and misallocation of resources, not a positive outcome for lower-income households.  The unintended consequence of the rent freeze was a shift towards homeownership, leading to poor resource allocation and other problems.",
    "index": 10
},

```

</aside>

I also implemented functions for handling TXT files, allowing the questions to be written in the format `chunk.number_of_question_for_that_chunk`.

<aside>
📖
  
```
Question n. 1.0: The Simple Linear Iterative Clustering (SLIC) algorithm uses which of the following techniques to initially divide an image before refining clusters using the k-means Lloyd algorithm?
A: A hierarchical clustering approach, recursively dividing the image into smaller regions.
B: A random sampling approach, selecting pixel clusters at random for initial centroid assignment.
C: A grid-based approach, dividing the image into tiles of a specified size.
D: A region-growing approach, starting from seed pixels and expanding regions based on similarity.
Correct Answer: C

Question n. 1.1: The Simple Linear Iterative Clustering (SLIC) algorithm, used in image segmentation, employs a regularizer parameter (R) and a region size parameter (RS).  The image is initially divided into a grid, and k-means clustering is applied.  How does the regularizer parameter impact the SLIC algorithm's output, given the relationship R/RS in the feature w(x,y)?
A: The regularizer (R) is inversely proportional to the region size (RS), leading to smaller superpixels when R is large.
B: The regularizer (R) controls the balance between the visual appearance of clusters and their spatial consistency.
C: The regularizer (R) solely affects the speed of the k-means clustering process.
D: The regularizer (R) directly determines the number of superpixels generated.
Correct Answer: B
```

</aside>

### Code readability

For good practice, I usually check the code with *mypy* and *pylint.* I didn’t work too much on the information in the notebook because I have focused on it here. 

**One improvement would be adding a logger** when generating the questions. This would prevent progress from being lost and allow for more easily analyzing what led to the error. 

I incorporated a `time.sleep()` command to prevent exhausting resources. However, a **more efficient approach would involve implementing a retry mechanism:** attempting to call the LLM and waiting for the required duration before retrying in case of an error. This would optimize resource usage while handling potential failures dynamically.

# Conceptual question:

### If you could redesign the initial steps of the Learning API, would you change the data structure in which documents are represented (i.e. chunks and a summary)? If so, how would you change it and why?

A graph model of chunks might be more suitable instead of a linear model of chunks. Each chunk could be a node in the graph, connected via edges based on semantic or topical relationships.

If a question is generated based on a specific topic, the LLM can query the graph to retrieve contextually related chunks, even if they are spread across different document parts. This approach could lead to more complex questions integrating various aspects of the topic, effectively testing a deeper understanding of it. Such a format could be applied within an RAG system, where, while analyzing a single chunk, the system retrieves all relevant information from a graph-based database to enhance its response.

I would adjust the process so that the chunks include information from slides that primarily contain pictures and formulas, utilizing specialized picture-to-text models to interpret and explain the information presented in them.

I would also change the way the chunks are formatted—they should not be a fixed number of pages but take into account more semantic meaning.

### The original JSON files - just a note

I implemented a function to read the JSON files, as they were improperly formatted, with the end of the file expected after the first item.
