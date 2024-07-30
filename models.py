from pydantic import BaseModel
from typing import List


class FAQPair(BaseModel):
    question: str
    answer: str

class FAQResponse(BaseModel):
    faq_pairs: List[FAQPair]


class GithubIssue(BaseModel):
    title: str
    body: str
    comments: List[str]

    def to_prompt(self) -> str:
        prompt = ""
        prompt += f"Title: {self.title}\n"
        prompt += f"Body: {self.body}\n"
        prompt += "Comments:\n"
        for comment in self.comments:
            prompt += f"    {comment}\n"
        return prompt
