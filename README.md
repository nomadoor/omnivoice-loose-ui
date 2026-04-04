# OmniVoice Loose UI

[![日本語](https://img.shields.io/badge/README-%E6%97%A5%E6%9C%AC%E8%AA%9E-1f1f1f?style=flat-square)](./README.ja.md)

## Original OmniVoice

This UI is for OmniVoice.

- Original repo: https://github.com/k2-fsa/OmniVoice
- Model / project details should be checked there first.

## What This Is

A small local Web UI for OmniVoice.

- left: job history
- right: current generation settings
- bottom: text composer

This is not a chat app. One input text becomes one generation job.

## Setup

```bat
install.bat
```

## Run

```bat
run.bat
```

Options:

```bat
run.bat --no-browser
run.bat --port 9000
run.bat --port 9000 --no-browser
```

For dev:

```bat
run-dev.bat
```

## Basic Usage

1. Open the app.
2. Set language / reference audio / voice instruction / speed / duration / num step.
3. Type text at the bottom.
4. Press `Run` or `Ctrl/Cmd + Enter`.
5. Wait for the job to move through `queued -> running -> done / error`.
6. When done, use `Play` or `Download`.

## Reference Audio

- You can drag and drop audio or browse for a file.
- Uploaded files are saved in `backend/uploads`.
- Saved reference audio can be picked again from the dropdown.

## Notes

- The model may be downloaded on first run.
- Hugging Face cache is stored in `backend/hf-cache`.
- Generated audio is saved in `backend/generated`.
- App state is saved in `backend/state.json`.
