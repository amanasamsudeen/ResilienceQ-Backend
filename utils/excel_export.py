from openpyxl import Workbook
from datetime import datetime
from pathlib import Path
from utils.questions import QUESTIONS


def generate_excel(payload):
    wb = Workbook()
    ws = wb.active
    ws.title = "ResilienceQ Assessment"

    # Personal Info
    ws.append(["Field", "Value"])
    ws.append(["Full Name", payload.personalInfo.full_name])
    ws.append(["Email", payload.personalInfo.email])
    ws.append(["Gender", payload.personalInfo.gender])
    ws.append(["Date of Birth", payload.personalInfo.dob])
    ws.append(["Education", payload.personalInfo.education])
    ws.append(["Occupation", payload.personalInfo.occupation])
    ws.append([])

    # Answers with Questions
    ws.append(["Question No", "Question", "Answer"])

    for i, ans in enumerate(payload.answers):
        question_text = QUESTIONS[i] if i < len(QUESTIONS) else "N/A"
        ws.append([i + 1, question_text, ans])

    # Export folder
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resilienceq_{timestamp}.xlsx"
    file_path = export_dir / filename

    wb.save(file_path)

    return file_path
