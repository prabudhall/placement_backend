from typing import Union

import gensim
import pandas as pd
from bertopic import BERTopic
from fastapi import APIRouter, Response
from nltk.stem import WordNetLemmatizer
from pydantic import BaseModel

router = APIRouter()
mapping_data = pd.read_csv("cn_subject/mapping.csv")
model = BERTopic.load("cn_subject/model")
print("model loaded")

def ls(text):
    return WordNetLemmatizer().lemmatize(text, pos='v')

def pp(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 1:
            result.append(ls(token))
    result = ' '.join(result)
    return result

def get_topics_with_mapping(ques_list):

    # Process each question and get topics
    topic_list_with_question = []
    for idx, ques in enumerate(ques_list):
        preprocessed_question = pp(ques)
        similar_topics, _ = model.find_topics(preprocessed_question, top_n=2)

        # Map bucket_topic_number to book_topic_number with the highest non-zero score
        book_topic_number_1, book_topic_number_2 = None, None
        score_1, score_2 = 0.0, 0.0
        is_topic_interchange_done = False
        for topic_number in similar_topics:
            # Filter the mapping data for the current bucket_topic_number
            topic_data = mapping_data[mapping_data['bucket_topic_number'] == topic_number + 1]

            # Get the book_topic_number and corresponding score
            if not topic_data.empty:
                current_score = topic_data['score'].max()
                current_book_topic_number = topic_data.loc[topic_data['score'].idxmax()]['book_topic_number']

                # Assign to variables based on score
                if current_score >= score_1:
                    score_2, score_1 = score_1, current_score
                    book_topic_number_2, book_topic_number_1 = book_topic_number_1, current_book_topic_number
                    is_topic_interchange_done = True
                elif current_score >= score_2:
                    score_2 = current_score
                    book_topic_number_2 = current_book_topic_number

        # Get the names of topics
        book_topic_1 = mapping_data[mapping_data['book_topic_number'] == book_topic_number_1]['book_topic'].values[
            0] if book_topic_number_1 is not None else None
        book_topic_2 = mapping_data[mapping_data['book_topic_number'] == book_topic_number_2]['book_topic'].values[
            0] if book_topic_number_2 is not None else None

        question_topic_dict = {}
        if is_topic_interchange_done:
            question_topic_dict = {
                "question": ques,
                "matching_topic": [
                    {
                        "bertopic": mapping_data[mapping_data['bucket_topic_number'] == similar_topics[1] + 1]["bucket_topic"],
                        "book_topic": book_topic_1,
                        "score": score_1
                    },
                    {
                        "bertopic": mapping_data[mapping_data['bucket_topic_number'] == similar_topics[0] + 1]["bucket_topic"],
                        "book_topic": book_topic_2,
                        "score": score_2
                    }
                ]
            }
        else:
            question_topic_dict = {
                "question": ques,
                "matching_topic": [
                    {
                        "bertopic": mapping_data[mapping_data['bucket_topic_number'] == similar_topics[0] + 1]["bucket_topic"],
                        "book_topic": book_topic_1,
                        "score": score_1
                    },
                    {
                        "bertopic": mapping_data[mapping_data['bucket_topic_number'] == similar_topics[1] + 1]["bucket_topic"],
                        "book_topic": book_topic_2,
                        "score": score_2
                    }
                ]
            }

        # Append dictionary containing question and topic with score into list
        topic_list_with_question.append(question_topic_dict)

    return topic_list_with_question


class Questions(BaseModel):
    question: Union[str, None] = None
    question_list: Union[list, None] = None

@router.get("/single/question")
def get_single_question_output(question: Questions, response: Response):
    if not question.question:
        response.status_code = 400
        return {"message": "question missing"}
    question = question.question
    print(question)
    question_topic_dict = get_topics_with_mapping([question])[0]
    print(question_topic_dict)
    return {
        "message": "Topic predicted successfully",
        "data": question_topic_dict
    }

@router.get("/multiple/question")
def get_single_question_output(question_list: Questions, response: Response):
    if not question_list.question_list:
        response.status_code = 400
        return {"message": "question missing"}
    question_list = question_list.question_list

    question_topic_dict_list = get_topics_with_mapping([question_list])

    return {
        "message": "Topics predicted successfully",
        "data": question_topic_dict_list
    }

