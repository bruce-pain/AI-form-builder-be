"""Deterministic instruction engine for form editing"""

from copy import deepcopy
from typing import List, Optional

from app.core.logger import logger
from app.features.llm.schemas import (
    AddQuestionInstruction,
    FormInstruction,
    FormResponse,
    RemoveQuestionInstruction,
    ReorderQuestionsInstruction,
    SetDescriptionInstruction,
    SetTitleInstruction,
    UpdateQuestionInstruction,
)


class InstructionError(ValueError):
    """Raised when an instruction cannot be applied"""


def apply_instructions(
    current_state: Optional[FormResponse],
    instructions: List[FormInstruction],
) -> FormResponse:
    state = (
        deepcopy(current_state)
        if current_state
        else FormResponse(title=None, description=None, questions=[])
    )

    for i, instruction in enumerate(instructions):
        logger.info(
            "Applying instruction %d/%d: %s",
            i + 1,
            len(instructions),
            _summarize_instruction(instruction),
        )
        _apply_one(state, instruction)

    logger.info(
        "Instructions applied | title: %s | questions: %d",
        state.title,
        len(state.questions),
    )

    return state


def _summarize_instruction(instruction: FormInstruction) -> str:
    if isinstance(instruction, SetTitleInstruction):
        return f"set_title -> '{instruction.title[:60]}'"
    if isinstance(instruction, SetDescriptionInstruction):
        return f"set_description -> '{instruction.description[:60]}'"
    if isinstance(instruction, AddQuestionInstruction):
        return f"add_question id='{instruction.question.id}' after='{instruction.after_id}'"
    if isinstance(instruction, UpdateQuestionInstruction):
        return f"update_question id='{instruction.question_id}'"
    if isinstance(instruction, RemoveQuestionInstruction):
        return f"remove_question id='{instruction.question_id}'"
    if isinstance(instruction, ReorderQuestionsInstruction):
        return f"reorder_questions ids={instruction.question_ids}"
    return f"unknown instruction: {type(instruction).__name__}"


def _apply_one(state: FormResponse, instruction: FormInstruction) -> None:
    if isinstance(instruction, SetTitleInstruction):
        state.title = instruction.title

    elif isinstance(instruction, SetDescriptionInstruction):
        state.description = instruction.description

    elif isinstance(instruction, AddQuestionInstruction):
        _check_question_id_unique(state, instruction.question.id)
        if instruction.after_id is not None:
            idx = _find_question_index(state, instruction.after_id)
            state.questions.insert(idx + 1, instruction.question)
        else:
            state.questions.append(instruction.question)

    elif isinstance(instruction, UpdateQuestionInstruction):
        idx = _find_question_index(state, instruction.question_id)
        state.questions[idx] = instruction.question

    elif isinstance(instruction, RemoveQuestionInstruction):
        idx = _find_question_index(state, instruction.question_id)
        state.questions.pop(idx)

    elif isinstance(instruction, ReorderQuestionsInstruction):
        existing_ids = {q.id for q in state.questions}
        new_ids = instruction.question_ids
        if set(new_ids) != existing_ids:
            raise InstructionError(
                "reorder_questions IDs must match existing question IDs exactly"
            )
        id_to_question = {q.id: q for q in state.questions}
        state.questions = [id_to_question[qid] for qid in new_ids]


def _check_question_id_unique(state: FormResponse, qid: str) -> None:
    if any(q.id == qid for q in state.questions):
        raise InstructionError(f"question id '{qid}' already exists")


def _find_question_index(state: FormResponse, qid: str) -> int:
    for i, q in enumerate(state.questions):
        if q.id == qid:
            return i
    raise InstructionError(f"question id '{qid}' not found")
