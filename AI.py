import os
import ast
import csv
import openai
import textwrap
import pandas as pd
from pathlib import Path
from config import config
from pypdf import PdfReader
from openai.embeddings_utils import cosine_similarity


# OpenAi models to use
COMPLETIONS_MODEL = "text-davinci-003"      # used for answering questions
EMBEDDING_MODEL = "text-embedding-ada-002"  # used for embedding text
openai.api_key = config.OpenAI


# get the text, run it through OpenAI and return the embedded text
def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> list[float]:
    result = openai.Embedding.create(
      model=model,
      input=text
    )
    return result["data"][0]["embedding"]


# get the question and the desired context and create a custom prompt to send to OpenAi
def construct_prompt(question: str, context) -> str:
    question_vector = get_embedding(question, EMBEDDING_MODEL)  # Embed the question
    # convert every row in "Embedded" column to lists
    context["Embedded"] = context["Embedded"].apply(lambda s: list(ast.literal_eval(s)))
    # make cosine similarity between each chunk of embedded text and the embedded question
    context["Similarities"] = context["Embedded"].apply(lambda x: cosine_similarity(x, question_vector))
    context_sorted = context.sort_values("Similarities", ascending=False).head(7)   # sort the best 7 similarities
    # Create a header for the prompt to model the AI response
    header = """Reply with a detailed text of maximum 200 words in which you explain the answer and if you do not find the information in the text 
    provided reply with 'I don't know' "\n\nContext:\n"""

    return header + "".join(context_sorted["Text"].head().tolist()) + question


def answer_questions(question, file_name):
    file_path = os.path.join("Uploaded_Files", file_name)  # get the file path of the file "file_name"
    file_text_name = Path(file_path).stem + "_text.csv"         # create a resembling name for the .txt file
    ftn_path = os.path.join("Embedded_Files", file_text_name)  # file_text_name path including the name
    reader = PdfReader(file_path)
    # Create .csv file with a column with chunks of text from the file and
    # another columns with the embedding of the text
    if not os.path.isfile(ftn_path):
        with open(ftn_path, "w", encoding="utf-8", newline='') as df:
            writer = csv.writer(df)
            writer.writerow(["Text", "Embedded"])

            for page in reader.pages:           # read PDF file page by page
                page_text_list = textwrap.wrap(page.extract_text(), width=500) # make chunks of text of 500 characters
                for item in page_text_list:     # embed each text and write to .csv file
                    writer.writerow([item, get_embedding(item, EMBEDDING_MODEL)])
    # read the completed csv file
    df2 = pd.read_csv(ftn_path)
    # sent a prompt to OpenAI with question and context and receive the answer
    response = openai.Completion.create(
        max_tokens=200,
        engine=COMPLETIONS_MODEL,
        temperature=0.4,
        prompt=construct_prompt(question=question, context=df2)
    )

    return response["choices"][0]["text"].strip(" \n")