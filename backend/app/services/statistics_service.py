from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlmodel import Session, select, func, and_
from app.models.student import Student
from app.models.lecture import Lecture
from app.models.teacher import Teacher
from app.models.material import Material


class StatisticsService:
    """통계 데이터를 계산하는 서비스 클래스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_student_statistics(self) -> Dict:
        """학생 관련 기본 통계"""
        try:
            # 전체 학생 수
            total_students = self.db.exec(select(func.count(Student.id))).first() or 0
            
            # 활성 학생 수
            active_students = self.db.exec(
                select(func.count(Student.id)).where(Student.is_active == True)
            ).first() or 0
            
            # 비활성 학생 수
            inactive_students = total_students - active_students
            
            # 학년별 분포
            grade_distribution = {}
            students_by_grade = self.db.exec(
                select(Student.grade, func.count(Student.id))
                .where(Student.grade.is_not(None))
                .group_by(Student.grade)
            ).all()
            
            for grade, count in students_by_grade:
                grade_distribution[grade] = count
            
            # 수강료 통계
            tuition_stats = self.db.exec(
                select(
                    func.sum(Student.tuition_fee).label('total_revenue'),
                    func.avg(Student.tuition_fee).label('average_tuition'),
                    func.count(Student.id).label('total_students')
                )
                .where(Student.is_active == True)
            ).first()
            
            # 체납 학생 수 (수강료 납부일이 지난 학생)
            overdue_students = self.db.exec(
                select(func.count(Student.id))
                .where(
                    and_(
                        Student.tuition_due_date < datetime.utcnow(),
                        Student.is_active == True
                    )
                )
            ).first() or 0
            
            # 최근 등록 학생 (최근 30일)
            recent_registrations = self.db.exec(
                select(func.count(Student.id))
                .where(
                    Student.created_at >= datetime.utcnow() - timedelta(days=30)
                )
            ).first() or 0
            
            return {
                "total_students": total_students,
                "active_students": active_students,
                "inactive_students": inactive_students,
                "grade_distribution": grade_distribution,
                "tuition_stats": {
                    "total_revenue": float(tuition_stats.total_revenue or 0),
                    "average_tuition": float(tuition_stats.average_tuition or 0),
                    "overdue_count": overdue_students,
                    "recent_registrations": recent_registrations
                }
            }
        except Exception as e:
            print(f"학생 통계 계산 오류: {e}")
            return {
                "total_students": 0,
                "active_students": 0,
                "inactive_students": 0,
                "grade_distribution": {},
                "tuition_stats": {
                    "total_revenue": 0,
                    "average_tuition": 0,
                    "overdue_count": 0,
                    "recent_registrations": 0
                }
            }
    
    def get_lecture_statistics(self) -> Dict:
        """강의 관련 기본 통계"""
        try:
            # 전체 강의 수
            total_lectures = self.db.exec(select(func.count(Lecture.id))).first() or 0
            
            # 활성 강의 수
            active_lectures = self.db.exec(
                select(func.count(Lecture.id)).where(Lecture.is_active == True)
            ).first() or 0
            
            # 비활성 강의 수
            inactive_lectures = total_lectures - active_lectures
            
            # 과목별 분포
            subject_distribution = {}
            lectures_by_subject = self.db.exec(
                select(Lecture.subject, func.count(Lecture.id))
                .group_by(Lecture.subject)
            ).all()
            
            for subject, count in lectures_by_subject:
                subject_distribution[subject] = count
            
            # 학년별 분포
            grade_distribution = {}
            lectures_by_grade = self.db.exec(
                select(Lecture.grade, func.count(Lecture.id))
                .group_by(Lecture.grade)
            ).all()
            
            for grade, count in lectures_by_grade:
                grade_distribution[grade] = count
            
            # 수강률 통계
            enrollment_stats = self.db.exec(
                select(
                    func.sum(Lecture.current_students).label('total_enrollments'),
                    func.sum(Lecture.max_students).label('total_capacity'),
                    func.avg(Lecture.current_students).label('average_enrollment'),
                    func.avg(Lecture.max_students).label('average_capacity')
                )
                .where(Lecture.is_active == True)
            ).first()
            
            # 수익 통계
            revenue_stats = self.db.exec(
                select(
                    func.sum(Lecture.tuition_fee * Lecture.current_students).label('total_revenue'),
                    func.avg(Lecture.tuition_fee).label('average_tuition')
                )
                .where(Lecture.is_active == True)
            ).first()
            
            # 인기 강의 TOP 5 (수강생 기준)
            popular_lectures = self.db.exec(
                select(Lecture)
                .where(Lecture.is_active == True)
                .order_by(Lecture.current_students.desc())
                .limit(5)
            ).all()
            
            return {
                "total_lectures": total_lectures,
                "active_lectures": active_lectures,
                "inactive_lectures": inactive_lectures,
                "subject_distribution": subject_distribution,
                "grade_distribution": grade_distribution,
                "enrollment_stats": {
                    "total_enrollments": enrollment_stats.total_enrollments or 0,
                    "total_capacity": enrollment_stats.total_capacity or 0,
                    "average_enrollment": float(enrollment_stats.average_enrollment or 0),
                    "average_capacity": float(enrollment_stats.average_capacity or 0),
                    "enrollment_rate": (
                        (enrollment_stats.total_enrollments or 0) / 
                        (enrollment_stats.total_capacity or 1) * 100
                    )
                },
                "revenue_stats": {
                    "total_revenue": float(revenue_stats.total_revenue or 0),
                    "average_tuition": float(revenue_stats.average_tuition or 0)
                },
                "popular_lectures": [
                    {
                        "id": lecture.id,
                        "title": lecture.title,
                        "subject": lecture.subject,
                        "current_students": lecture.current_students,
                        "max_students": lecture.max_students,
                        "enrollment_rate": (
                            lecture.current_students / lecture.max_students * 100
                            if lecture.max_students > 0 else 0
                        )
                    }
                    for lecture in popular_lectures
                ]
            }
        except Exception as e:
            print(f"강의 통계 계산 오류: {e}")
            return {
                "total_lectures": 0,
                "active_lectures": 0,
                "inactive_lectures": 0,
                "subject_distribution": {},
                "grade_distribution": {},
                "enrollment_stats": {
                    "total_enrollments": 0,
                    "total_capacity": 0,
                    "average_enrollment": 0,
                    "average_capacity": 0,
                    "enrollment_rate": 0
                },
                "revenue_stats": {
                    "total_revenue": 0,
                    "average_tuition": 0
                },
                "popular_lectures": []
            }
    
    def get_teacher_statistics(self) -> Dict:
        """강사 관련 기본 통계"""
        try:
            # 전체 강사 수
            total_teachers = self.db.exec(select(func.count(Teacher.id))).first() or 0
            
            # 활성 강사 수
            active_teachers = self.db.exec(
                select(func.count(Teacher.id)).where(Teacher.is_active == True)
            ).first() or 0
            
            # 비활성 강사 수
            inactive_teachers = total_teachers - active_teachers
            
            # 강사별 성과 (강의 수, 총 학생 수, 평균 수강률)
            teacher_performance = []
            teachers = self.db.exec(
                select(Teacher).where(Teacher.is_active == True)
            ).all()
            
            for teacher in teachers:
                # 해당 강사의 강의들
                teacher_lectures = self.db.exec(
                    select(Lecture).where(Lecture.teacher_id == teacher.id)
                ).all()
                
                lecture_count = len(teacher_lectures)
                total_students = sum(lecture.current_students for lecture in teacher_lectures)
                total_revenue = sum(
                    lecture.tuition_fee * lecture.current_students 
                    for lecture in teacher_lectures
                )
                
                # 평균 수강률 계산
                if teacher_lectures:
                    total_capacity = sum(lecture.max_students for lecture in teacher_lectures)
                    avg_enrollment_rate = (
                        total_students / total_capacity * 100 
                        if total_capacity > 0 else 0
                    )
                else:
                    avg_enrollment_rate = 0
                
                teacher_performance.append({
                    "teacher_id": teacher.id,
                    "teacher_name": teacher.name,
                    "lecture_count": lecture_count,
                    "total_students": total_students,
                    "average_enrollment_rate": round(avg_enrollment_rate, 2),
                    "total_revenue": total_revenue
                })
            
            # 과목별 강사 분포
            subject_teacher_distribution = {}
            for teacher in teachers:
                teacher_lectures = self.db.exec(
                    select(Lecture.subject).where(Lecture.teacher_id == teacher.id)
                ).all()
                
                for subject_lecture in teacher_lectures:
                    # subject_lecture는 이미 문자열이므로 직접 사용
                    if subject_lecture not in subject_teacher_distribution:
                        subject_teacher_distribution[subject_lecture] = set()
                    subject_teacher_distribution[subject_lecture].add(teacher.id)
            
            # set을 count로 변환
            subject_teacher_distribution = {
                subject: len(teacher_ids) 
                for subject, teacher_ids in subject_teacher_distribution.items()
            }
            
            return {
                "total_teachers": total_teachers,
                "active_teachers": active_teachers,
                "inactive_teachers": inactive_teachers,
                "teacher_performance": teacher_performance,
                "subject_teacher_distribution": subject_teacher_distribution
            }
        except Exception as e:
            print(f"강사 통계 계산 오류: {e}")
            import traceback
            traceback.print_exc()
            return {
                "total_teachers": 0,
                "active_teachers": 0,
                "inactive_teachers": 0,
                "teacher_performance": [],
                "subject_teacher_distribution": {}
            }
    
    def get_material_statistics(self) -> Dict:
        """교재 관련 기본 통계"""
        try:
            # 전체 교재 수
            total_materials = self.db.exec(select(func.count(Material.id))).first() or 0
            
            # 활성 교재 수
            active_materials = self.db.exec(
                select(func.count(Material.id)).where(Material.is_active == True)
            ).first() or 0
            
            # 비활성 교재 수
            inactive_materials = total_materials - active_materials
            
            # 과목별 교재 분포
            subject_distribution = {}
            materials_by_subject = self.db.exec(
                select(Material.subject, func.count(Material.id))
                .group_by(Material.subject)
            ).all()
            
            for subject, count in materials_by_subject:
                subject_distribution[subject] = count
            
            # 교재별 사용 현황 (어떤 강의에서 사용되는지)
            material_usage = []
            materials = self.db.exec(select(Material)).all()
            
            for material in materials:
                usage_count = self.db.exec(
                    select(func.count(Lecture.id))
                    .where(Lecture.material_id == material.id)
                ).first() or 0
                
                material_usage.append({
                    "material_id": material.id,
                    "material_name": material.name,
                    "subject": material.subject,
                    "usage_count": usage_count
                })
            
            return {
                "total_materials": total_materials,
                "active_materials": active_materials,
                "inactive_materials": inactive_materials,
                "subject_distribution": subject_distribution,
                "material_usage": material_usage
            }
        except Exception as e:
            print(f"교재 통계 계산 오류: {e}")
            return {
                "total_materials": 0,
                "active_materials": 0,
                "inactive_materials": 0,
                "subject_distribution": {},
                "material_usage": []
            }
    
    def get_overall_statistics(self) -> Dict:
        """전체 종합 통계"""
        try:
            student_stats = self.get_student_statistics()
            lecture_stats = self.get_lecture_statistics()
            teacher_stats = self.get_teacher_statistics()
            material_stats = self.get_material_statistics()
            
            # 전체 수익 (학생 수강료 + 강의 수강료)
            total_revenue = (
                student_stats["tuition_stats"]["total_revenue"] +
                lecture_stats["revenue_stats"]["total_revenue"]
            )
            
            return {
                "summary": {
                    "total_students": student_stats["total_students"],
                    "total_lectures": lecture_stats["total_lectures"],
                    "total_teachers": teacher_stats["total_teachers"],
                    "total_materials": material_stats["total_materials"],
                    "total_revenue": total_revenue
                },
                "student_stats": student_stats,
                "lecture_stats": lecture_stats,
                "teacher_stats": teacher_stats,
                "material_stats": material_stats
            }
        except Exception as e:
            print(f"전체 통계 계산 오류: {e}")
            return {
                "summary": {
                    "total_students": 0,
                    "total_lectures": 0,
                    "total_teachers": 0,
                    "total_materials": 0,
                    "total_revenue": 0
                },
                "student_stats": {},
                "lecture_stats": {},
                "teacher_stats": {},
                "material_stats": {}
            } 