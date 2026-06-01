# Autonomous Web Navigation Agent

A command-line tool that uses a vision-capable model and Playwright to navigate GitHub and extract structured release information. A sample output is provided under: `outputs\run_20260531_210337\sample_output.json`

The default task starts from `https://github.com`, searches for `openclaw/openclaw`, opens the repository's Releases section, extracts useful release information, and writes a final JSON result.

## Requirements

- Python 3.10+
- A vision-capable OpenAI-compatible model
- Playwright Chromium

## Setup

Clone the repository and enter the project folder:

```bash
git clone <your-repo-url>
cd autonomous-web-navigation-agent
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Install the Playwright Chromium browser:

```bash
python -m playwright install chromium
```

Create a `.env` file from the example file:

```bash
cp .env.example .env
```

Then edit `.env` and add your API key:

```env
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-5.4
BASE_URL=
MODEL_TEMPERATURE=0.2
MODEL_MAX_TOKENS=
MODEL_TIMEOUT=30
MODEL_MAX_RETRIES=3
```

## Run

### Default task

```bash
python navigate.py
```

This runs the default task for:

```text
openclaw/openclaw
```

### Specify a GitHub repository

```bash
python navigate.py --repo microsoft/playwright
```

### Use a custom natural-language prompt

```bash
python navigate.py --prompt "Go to GitHub and find the latest release of openclaw/openclaw. List the main key features from the release notes."
```

### Change the start URL

```bash
python navigate.py --start-url "https://github.com"
```

### Increase the max step limit

```bash
python navigate.py --max-steps 20
```

## Output

Each run writes output to a timestamped folder under:

```text
outputs/run_YYYYMMDD_HHMMSS/
```

Important files:

```text
final_output.json
```

The final concise structured result.

```text
extracted_information.json
```

Intermediate extracted information from pages where the agent chose to extract content.

```text
run_log.json
```

Full debug log with actions, model decisions, extraction history, and final status.

```text
screenshots/
```

Step-by-step screenshots of the browser state.

## Final Output Format

`final_output.json` uses this format:

```json
{
  "task": "Find the repository openclaw/openclaw and extract the latest release information as JSON.",
  "status": "success",
  "result": {
    "repository": "openclaw/openclaw",
    "release_title": "openclaw 2026.5.31-beta.3",
    "tag": "v2026.5.31-beta.3",
    "author": "steipete",
    "publish_date": "2026.5.31"
  },
  "limitations": []
}
```

Possible `status` values:

```text
success
partial
failed
```

## Sample Output

A sample run is included under:

```text
outputs/sample_submission/
```

Recommended files in the sample folder:

```text
outputs/sample_submission/final_output.json
outputs/sample_submission/extracted_information.json
outputs/sample_submission/run_log.json
outputs/sample_submission/screenshots/
```

## Notes

More details about design decisions, trade-offs, limitations, and future improvements are documented in `observations.pdf`.
