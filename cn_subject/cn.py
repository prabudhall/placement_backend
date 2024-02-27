from typing import Union

from fastapi import APIRouter, Response
from pydantic import BaseModel

router = APIRouter()

class Questions(BaseModel):
    question: Union[str, None] = None
    question_list: Union[list, None] = None

@router.get("/single/question")
def get_single_question_output(question: Questions, response: Response):
    if not question.question:
        response.status_code = 400
        return {"message": "question missing"}
    question = question

    return {
        "message": "it will return the predicted topic of a single question"
    }

@router.get("/multiple/question")
def get_single_question_output(question_list: Questions, response: Response):
    if not question_list.question_list:
        response.status_code = 400
        return {"message": "question missing"}
    question_list = question_list

    return {
        "message": "it will return the predicted topics of multiple questions coming in a list"
    }

