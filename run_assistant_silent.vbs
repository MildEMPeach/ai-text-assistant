Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "python text_summary_assistant.py", 0, False
Set WshShell = Nothing 