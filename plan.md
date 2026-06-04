# Field Constraints Plan

## 1. `FormQuestion` — Pydantic model in `app/features/form/models.py`

### Simple field constraints
- `id`: add `min_length=1`
- `text`: add `min_length=1`, `max_length=500`
- `answer_type`: already constrained via `Literal["text", "select"]` — no change
- `answer_select_options`: no standalone constraint change
- `answer_select_multiple`: no standalone constraint change
- `required`: no change

### Cross-field validation (add `@model_validator(mode="after")`)
- When `answer_type == "select"`: `answer_select_options` must be non-None and non-empty; `answer_select_multiple` must be non-None
- When `answer_type == "text"`: `answer_select_options` must be None; `answer_select_multiple` must be None

New import needed: `model_validator` from `pydantic`. The `Field` import from `pydantic` is also needed (or keep using plain assignment and use `Field(...)` for the constrained fields).

---

## 2. `ResponseAnswer` — Pydantic model in `app/features/response/models.py`

### Simple field constraint
- `question_id`: add `min_length=1`

### Cross-field validation (add `@model_validator(mode="after")`)
- When `answer_type == "text"`: `text_answer` must be non-None and non-empty; `select_answer` must be None
- When `answer_type == "select"`: `select_answer` must be non-None and non-empty; `text_answer` must be None

Same new imports as above.

---

## 3. Request Schemas — `app/features/form/schemas.py`

- `FormCreateRequest.title`: add `min_length=1`, `max_length=255`
- `FormCreateRequest.description`: add `min_length=1`, `max_length=2000`
- `FormUpdateRequest.title`: add `min_length=1`, `max_length=255` (applied only when value is provided, since it's Optional)
- `FormUpdateRequest.description`: add `min_length=1`, `max_length=2000` (same)
- No changes to `questions` or `is_published`

Import `Field` from `pydantic` to express these constraints. In Pydantic v2, `Optional[str] = Field(default=None, min_length=1)` applies the constraint only when a value is actually provided.

---

## 4. Service-layer validation — `app/features/response/service.py`

In `ResponseService.submit()`, after fetching the form, add validation loops before creating the response:

- Build a dict of `{question_id: question}` from `form.questions`
- For each answer in `schema.answers`:
  - Check the `question_id` exists in the form — return 422 if not
  - Check `answer_type` matches the question's `answer_type` — return 422 if mismatch
  - If `answer_type == "select"`, check each value in `select_answer` is within the question's `answer_select_options` — return 422 listing invalid options
- Optionally (recommended): collect all answered `question_id`s and verify every question with `required=True` has been answered — return 422 listing missing required questions

---

## 5. Tests — update `tests/test_form.py` and `tests/test_response.py`

### Form tests to add (in `TestCreateForm`):
- Creating a form with `title=""` returns 422
- Creating a form with question `text=""` returns 422
- Creating a form with `answer_type="select"` but `answer_select_options=None` returns 422
- Creating a form with `answer_type="text"` but `answer_select_options=["A"]` returns 422

### Response tests to add (in `TestSubmitResponse`):
- Submitting with `answer_type="text"` but `text_answer=None` returns 422
- Submitting with `answer_type="select"` but `select_answer=None` returns 422
- Submitting with `answer_type="text"` and `select_answer=["A"]` returns 422
- Submitting a `question_id` not in the form returns 422
- Submitting answer type mismatching the question's `answer_type` returns 422
- Submitting an invalid select option (not in question's `answer_select_options`) returns 422
- Omitting an answer for a required question returns 422

---

## Important notes

1. **No database migrations needed** — all validation is at the Pydantic/application layer
2. **Existing fixtures should be checked** — `sample_form_data` in both test files pairs `answer_type: "text"` with `answer_select_options: null` and `answer_select_multiple: null`, which satisfies the new conditional validators. The select-type question has appropriate options set. `sample_response_data` similarly pairs correct answer types with their corresponding fields.
3. **The test `test_create_form_no_questions`** sends no `questions` field at all — this remains valid since the field is Optional.
