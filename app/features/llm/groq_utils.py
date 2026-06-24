"""Groq utils"""

import json
from typing import List, Optional

from groq import AsyncGroq
from groq.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageParam,
)

from app.features.llm.schemas import FormQuestionList

GROQ_MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """
    You are an expert at designing form questions for data collection.

    You will receive an existing form state (a list of questions) and a new
    instruction from the user. Modify the existing form state to satisfy the
    new instruction — add, remove, or change questions as needed. Only generate
    a brand new form from scratch if the current state is empty or the
    instruction explicitly asks for one.

    Rules:
    - Each question has an id (q1, q2, q3, ...) that defines display order and must start from q1.
    - Questions can be one of two answer types:
      - "text": a free-text input. Do not set answer_select_options or answer_select_multiple.
      - "select": a dropdown / choice input. Must include answer_select_options (list of 2–6 choices) and answer_select_multiple (true if multiple selections allowed, false if single).
    - The required field indicates whether the question must be answered.
    - Question text must be clear, concise, and specific. Use second person ("you") where natural.
    - Do not include instructions like "select all that apply" in the question text — use answer_select_multiple instead.
    - Generate 3–10 questions unless the user specifies otherwise.
    - If the prompt is vague or outside form question generation, make reasonable assumptions or return an empty questions list.
    - Output ONLY valid JSON matching the schema. No explanations, no markdown.
"""


async def run_inference(
    client: AsyncGroq,
    conversation_history: List[ChatCompletionMessageParam],
) -> ChatCompletionMessage:
    completion = await client.chat.completions.create(
        model=GROQ_MODEL,
        messages=conversation_history,
        max_completion_tokens=1024,
        reasoning_format="hidden",
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "form_question",
                "description": "A list of form questions",
                "schema": FormQuestionList.model_json_schema(),
            },
        },
    )

    return completion.choices[0].message


def parse_message(message: ChatCompletionMessage) -> Optional[FormQuestionList]:
    if message.content:
        raw_output = json.loads(message.content)
        validated_output = FormQuestionList.model_validate(raw_output)
        return validated_output
