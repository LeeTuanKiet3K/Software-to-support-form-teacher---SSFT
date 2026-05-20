from app.features.academic.AcademicService import AcademicService

# Check tren firebase de thay ket qua

academicService = AcademicService()

fakeData = {
    "student_id": "student_1",
    "class_id": "CLASS_A",
    "gpa": 1.8,

    "subjects": [
        {
            "subject_name": "Mathematics",
            "score": 4
        },
        {
            "subject_name": "Physics",
            "score": 3
        },
        {
            "subject_name": "Programming",
            "score": 7
        }
    ],

    "is_low_score": False,
    "ai_check_sent": False,
    "student_responded": False
}

result = academicService.inputGrade(fakeData)

print("RESULT =", result)