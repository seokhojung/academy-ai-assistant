from .student import Student
from .teacher import Teacher, TeacherCreate, TeacherUpdate
from .material import Material, MaterialCreate, MaterialUpdate
from .user import User
from .lecture import Lecture, LectureCreate, LectureUpdate

__all__ = [
    "Student", 
    "Teacher", "TeacherCreate", "TeacherUpdate",
    "Material", "MaterialCreate", "MaterialUpdate", 
    "User",
    "Lecture", "LectureCreate", "LectureUpdate"
] 