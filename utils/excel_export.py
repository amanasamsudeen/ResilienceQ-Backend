from openpyxl import Workbook
from datetime import datetime
from pathlib import Path
from schemas.assessment import AssessmentSubmission
from utils.questions import QUESTIONS



def generate_excel(payload: AssessmentSubmission):

    data = payload.model_dump()
    info = data["personalInfo"]
    answers = data["answers"]

    wb = Workbook()
    ws = wb.active
    ws.title = "ResilienceQ Assessment"

    ws.append(["Field", "Value"])
    ws.append(["Full Name", info["full_name"]])
    ws.append(["Email", info["email"]])
    ws.append(["Gender", info["gender"]])
    ws.append(["Date of Birth", str(info["dob"])])
    ws.append(["Education", info["education"]])
    ws.append(["Occupation", info["occupation"]])
    ws.append([])

    ws.append(["Question No", "Question", "Answer"])

    for i, ans in enumerate(answers):
        question_text = QUESTIONS[i] if i < len(QUESTIONS) else "N/A"
        ws.append([i + 1, question_text, ans])

    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"resilienceq_{timestamp}.xlsx"
    file_path = export_dir / filename

    wb.save(file_path)

    return file_path

