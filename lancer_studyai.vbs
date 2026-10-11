Set shell = CreateObject("WScript.Shell")
shell.CurrentDirectory = "C:\Users\HP\Documents\studyIA"
shell.Run "cmd /c .venv\Scripts\python.exe app.py > studyai.log 2>&1", 0, False
WScript.Sleep 4000
shell.Run "http://127.0.0.1:5000"