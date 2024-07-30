from models import *
import os
from github import Github
import anthropic

ai = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_KEY"))

LLM_MODEL = "claude-3-5-sonnet-20240620"

def generate_faqs(org: str, repo: str) -> List[FAQPair]:
    issues = get_issues(org, repo)
    faqs = []
    for issue in issues:
        faqs.extend(issue_to_faqs(issue))
    reduced_faqs = reduce_faqs(faqs)
    return reduced_faqs


def issue_to_faqs(issue: GithubIssue) -> List[FAQPair]:
    response = ai.messages.create(
        model=LLM_MODEL,
        max_tokens=512,
        temperature=0.0,
        system="""
You are a GitHub issue bot that generates FAQs from GitHub issues.
The FAQs should be common questions that users have asked where a solution was agreed upon.
Answers should be really short and concise, ideally one sentence, maximum three.
Developers will look at this at a glance before filing an issue.
Only generate FAQ pairs for resolved issues.
""",
        tools=[
            {
                "name": "submit_faqs",
                "description": "Submits a list of question answer pairs.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "faqs": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {"type": "string"},
                                    "answer": {"type": "string"},
                                },
                                "required": ["question", "answer"],
                            },
                        }
                    },
                    "required": ["faqs"],
                },
            }
        ],
        tool_choice={"type": "tool", "name": "submit_faqs"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": issue.to_prompt(),
                    },
                ],
            },
        ],
    )
    print(response.content[0])
    print("-----------------")
    answer = response.content[0].input["faqs"]
    print(answer)
    return [
        FAQPair(
            question=faq["question"],
            answer=faq["answer"],
        )
        for faq in answer
    ]


def reduce_faqs(faqs: List[FAQPair]) -> List[FAQPair]:
    response = ai.messages.create(
        model=LLM_MODEL,
        max_tokens=8192,
        temperature=0.0,
        extra_headers={
            "anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15",
        },
        system="""
You are a GitHub issue bot that generates FAQs from GitHub issues.
You will be provided a list of pre-generated FAQ pairs.
You will create a new list of pairs that is suitable for developer consumption.
Answers should be really short and concise, ideally one sentence, maximum three.
Developers will look at this at a glance before filing an issue.
Make sure that duplicate pairs are de-duplicated.
You can reword pairs if necessary.
""",
        tools=[
            {
                "name": "submit_faqs",
                "description": "Submits a list of question answer pairs.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "faqs": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {"type": "string"},
                                    "answer": {"type": "string"},
                                },
                                "required": ["question", "answer"],
                            },
                        }
                    },
                    "required": ["faqs"],
                },
            }
        ],
        tool_choice={"type": "tool", "name": "submit_faqs"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": str(faqs),
                    },
                ],
            },
        ],
    )
    answer = response.content[0].input["faqs"]
    return [
        FAQPair(
            question=faq["question"],
            answer=faq["answer"],
        )
        for faq in answer
    ]


def get_issues(org: str, repo: str) -> List[GithubIssue]:
    github_token = os.getenv("GITHUB_TOKEN")
    g = Github(github_token)
    repo = g.get_repo(f"{org}/{repo}")
    gIssues = repo.get_issues(state="all")
    issues = []
    for issue in gIssues:
        comments = [comment.body for comment in issue.get_comments()]
        print(issue.title)
        print(issue.body)
        print(comments)
        issues.append(
            GithubIssue(
                title=issue.title if issue.title else "",
                body=issue.body if issue.body else "",
                comments=comments if comments else [],
            )
        )
    return issues
