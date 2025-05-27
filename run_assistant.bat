@echo off
REM Suppress Qt DPI warnings
set QT_LOGGING_RULES=qt.qpa.window=false

REM Run the text summary assistant
python text_summary_assistant.py 