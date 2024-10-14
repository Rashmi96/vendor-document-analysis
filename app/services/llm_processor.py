import warnings
from tenacity import retry, stop_after_attempt, wait_random_exponential
from vertexai.language_models import TextEmbeddingModel, TextGenerationModel
import re
import pandas as pd
import numpy as np
import json
from app.services.text_extractor import extract
from app import Config
import tiktoken

warnings.filterwarnings("ignore")

def extract_fields_with_llm():
    final_data = extract()

    pdf_data = pd.DataFrame.from_dict(final_data)
    pdf_data = pdf_data.sort_values(by=["file_name"])
    pdf_data.reset_index(inplace=True, drop=True)

    pdf_data_sample = pdf_data.copy()
    pdf_data_sample["content"] = pdf_data_sample["content"].apply(
        lambda x: re.sub("[^A-Za-z0-9]+", " ", x)
    )
    pdf_data_sample["chunks"] = pdf_data_sample["content"].apply(split_text)
    pdf_data_sample = pdf_data_sample.explode("chunks")
    pdf_data_sample = pdf_data_sample.sort_values(by=["file_name"])
    pdf_data_sample.reset_index(inplace=True, drop=True)
    pdf_data_sample["chunks"] = pdf_data_sample["chunks"].fillna("")

    pdf_data_sample["embedding"] = pdf_data_sample["chunks"].apply(lambda x: compute_embedding(x))
    pdf_data_sample["embedding"] = pdf_data_sample["embedding"].apply(lambda x: np.array(x) if x is not None else None)

    with open(Config.PROMPT_QUESTION) as f:
        data = json.load(f)

    documentids = ['MG206855','MK231582','NY222079','SG222341']
    prompt_answers = []
    for document in documentids:
        for question_data in data['documentResponse'][0]['documentDetails']:
            question = question_data['question'] + f" For {document}"
            context, top_matched_df = get_context_from_question(
                question, vector_store=pdf_data_sample, sort_index_value=5
            )

            prompt = f"""Answer the question with only to the point. If the answer is not contained in the context, say "NULL".

            Context:
            {context}?

            Question:
            {question}

            Answer:
            """
            generated_answer = "Generated answer for " + question
            generation_model = TextGenerationModel.from_pretrained("text-bison@001")
            if count_tokens(prompt) > Config.TOKEN_LIMIT:
                prompt_chunks = get_chunks_iter(prompt, maxlength=Config.MAX_TOKENS_PER_REQUEST)
                for chunk in prompt_chunks:
                    generated_answer = generation_model.predict(chunk).text
            else:
                generated_answer = generation_model.predict(prompt).text
            prompt_answers.append({
                'Document': document,
                'Answer': generated_answer
            })

    # Create a DataFrame from the list of prompt answers
    df = pd.DataFrame(prompt_answers)
    df.to_csv("/static/reports/processed_data.csv",header=True)


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(10))
def text_generation_model_with_backoff(**kwargs):
    generation_model = TextGenerationModel.from_pretrained("text-bison@001")
    return generation_model.predict(**kwargs).text


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(10))
def embedding_model_with_backoff(text=[]):
    embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
    embeddings = embedding_model.get_embeddings(text)
    return [each.values for each in embeddings][0]


def get_chunks_iter(text, maxlength):
    start = 0
    end = 0
    final_chunk = []
    while start + maxlength < len(text) and end != -1:
        end = text.rfind(" ", start, start + maxlength + 1)
        final_chunk.append(text[start:end])
        start = end + 1
    final_chunk.append(text[start:])
    return final_chunk


def split_text(row):
    chunk_iter = get_chunks_iter(row, Config.CHUNK_SIZE)
    return chunk_iter


def count_tokens(prompt):
    # Use tiktoken to count tokens
    enc = tiktoken.get_encoding("p50k_base")  # Choose the appropriate encoding for your model
    tokens = enc.encode(prompt)
    return len(tokens)


def get_context_from_question(question, vector_store, sort_index_value=2):
    global query_vector
    query_vector = np.array(embedding_model_with_backoff([question]))
    top_matched = (
        vector_store["embedding"]
            .apply(get_dot_product)
            .sort_values(ascending=False)[:sort_index_value]
            .index
    )
    top_matched_df = vector_store[vector_store.index.isin(top_matched)][
        ["file_name", "chunks"]
    ]
    context = " ".join(
        vector_store[vector_store.index.isin(top_matched)]["chunks"].values
    )
    return context, top_matched_df


def compute_embedding(chunk):
    try:
        return embedding_model_with_backoff([chunk])
    except Exception as e:
        print(f"Error computing embedding for chunk: {chunk}, Error: {e}")
        return None


def get_dot_product(row):
    if row is None:
        return None
    return np.dot(row, query_vector)