# Assignment Feedback API

This API generates feedback for student assignments by querying an externally hosted LLM. It is currently based on the openai GPT-4o model, so effectively acts as an interface with the OpenAI API with some extra functionality to enable interaction with the rest of the AI edtech app. It is based on Flask but intended to be used locally at this stage, with data passed to the app.py script via localhost.

## Setup

1. Clone the repository
2. Install dependencies
3. Make a `.env` file containing correct API keys (eg OPENAI_API_KEY = "") or add these to system environmental vars

## Usage

Start the local server:

```python app.py```

Send a POST request to `/api/feedback` with the following form data:

### Required Fields

| Parameter         | Type           | Required | Description                                                         |
|-------------------|----------------|----------|---------------------------------------------------------------------|
| `assignment_id`   | `string`       | Yes      | Unique identifier for the assignment                                |
| `assignment_title`| `string`       | Yes      | Title of the assignment                                             |
| `question_id`     | `string`       | Yes      | Unique identifier for the question                                  |
| `question_title`  | `string`       | Yes      | Title of the question                                               |
| `subject`         | `string`       | Yes      | Subject of the assignment (e.g., 'History')                         |
| `qualification`   | `string`       | Yes      | Qualification level (e.g., 'GCSE')                                  |
| `submission`      | `string` or `file` | Yes  | Student's submission, can be either text string or file specifier (but only text for anthropic at the moment) |
| `mark_scheme`     | `file`         | Yes      | Mark scheme file                                                    |

### Optional Fields

| Parameter             | Type     | Required | Description                                                                                     |
|-----------------------|----------|----------|-------------------------------------------------------------------------------------------------|
| `model`               | `string` | No       | LLM model to use. Currently both OpenAI ("openai") and Anthropic ("anthropic") are available (default: "openai")         |
| `max_completion_tokens` | `integer`| No      | Maximum tokens for LLM response. May fail if this is set too low due to JSON parsing errors (default: 1000) |
| `temperature`         | `float`  | No       | LLM temperature setting. Should mostly be kept at 0 but left optional for tinkering (default: 0) |

Note that the only file type supported at the moment is PDF, but image/other file support may be implemented later.

Example cURL request (see example_files):

```
curl -X POST 'http://127.0.0.1:5000/api/feedback' -H 'Content-Type: multipart/form-data' -F 'assignment_id=123' -F 'assignment_title=Explain two consequences of the Soviet invasion of Afghanistan' -F 'subject=history' -F 'qualification=GCSE' -F 'submission=@example_files/example-submission.pdf' -F 'model=openai' -F 'mark_scheme=@example_files/example-ms.pdf'
```

The API will return a JSON response with feedback categorized into SPaG (Spelling, Punctuation and Grammar), historical accuracy, overall comments, and marking, eg:

{
    "category": "SPaG",
    "citations": null,
    "colour": "orange",
    "correct_or_feedback": "criticism",
    "end": [
        1070
    ],
    "incorrect": "critisicm",
    "start": [
        1061
    ]
}

Each feedback group has output formatted slightly differently (eg different fields may be null) depending on its intended use on frontend.

The API is still in development, so there are some missing features:
- Other model options, eg anthropic's claude
- Highlighting merited sections for the overall_feedback/marking fields

and some known bugs:
- Potentially incorrect start/end indexes in the response, due to inconsistencies with how strings are parsed at different stages in the process (eg escape characters causing problems). This can be observed from testing with highlight_text.py
- LLM hallucinations, eg outputting 'incorrect' passages slightly differently to how they appeared in the original submission
- Occasional 403 forbidden requests, usually fixed by restarting the localhost server
- Occasional OpenAIError errors when the servers are having issues

Please submit issues for any other bugs, thanks.