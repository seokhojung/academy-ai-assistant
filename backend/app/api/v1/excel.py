from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import io
import os
from datetime import datetime
from ..core.database import get_db
from ..models.student import Student
from ..models.teacher import Teacher
from ..models.material import Material
from ..models.lecture import Lecture

router = APIRouter()

# 엑셀 파일 저장 디렉토리
EXCEL_DIR = "excel_files"
os.makedirs(EXCEL_DIR, exist_ok=True)

@router.post("/upload/{entity_type}")
async def upload_excel_file(
    entity_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    엑셀 파일을 업로드하고 데이터베이스에 반영합니다.
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="엑셀 파일(.xlsx, .xls)만 업로드 가능합니다.")
    
    try:
        # 파일 내용 읽기
        content = await file.read()
        df = pd.read_excel(io.BytesIO(content))
        
        # 엔티티 타입에 따른 처리
        if entity_type == "students":
            return await process_student_excel(df, db)
        elif entity_type == "teachers":
            return await process_teacher_excel(df, db)
        elif entity_type == "materials":
            return await process_material_excel(df, db)
        elif entity_type == "lectures":
            return await process_lecture_excel(df, db)
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 엔티티 타입입니다.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 처리 중 오류가 발생했습니다: {str(e)}")

@router.get("/download/{entity_type}")
async def download_excel_file(
    entity_type: str,
    db: Session = Depends(get_db)
):
    """
    데이터베이스 데이터를 엑셀 파일로 다운로드합니다.
    """
    try:
        if entity_type == "students":
            return await generate_student_excel(db)
        elif entity_type == "teachers":
            return await generate_teacher_excel(db)
        elif entity_type == "materials":
            return await generate_material_excel(db)
        elif entity_type == "lectures":
            return await generate_lecture_excel(db)
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 엔티티 타입입니다.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 생성 중 오류가 발생했습니다: {str(e)}")

@router.post("/rebuild/{entity_type}")
async def rebuild_excel_file(
    entity_type: str,
    db: Session = Depends(get_db)
):
    """
    데이터베이스 데이터로 엑셀 파일을 재생성합니다.
    """
    try:
        if entity_type == "students":
            return await rebuild_student_excel(db)
        elif entity_type == "teachers":
            return await rebuild_teacher_excel(db)
        elif entity_type == "materials":
            return await rebuild_material_excel(db)
        elif entity_type == "lectures":
            return await rebuild_lecture_excel(db)
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 엔티티 타입입니다.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 재생성 중 오류가 발생했습니다: {str(e)}")

# 학생 데이터 처리 함수들
async def process_student_excel(df: pd.DataFrame, db: Session):
    """학생 엑셀 파일 처리"""
    try:
        # 컬럼명 매핑
        column_mapping = {
            '이름': 'name',
            '이메일': 'email', 
            '전화번호': 'phone',
            '학년': 'grade',
            '수강료': 'tuition_fee',
            '상태': 'is_active'
        }
        
        # 컬럼명 변경
        df = df.rename(columns=column_mapping)
        
        # 데이터베이스에 저장
        for _, row in df.iterrows():
            student = Student(
                name=row.get('name', ''),
                email=row.get('email', ''),
                phone=row.get('phone', ''),
                grade=row.get('grade', ''),
                tuition_fee=float(row.get('tuition_fee', 0)),
                is_active=row.get('is_active', '활성') == '활성'
            )
            db.add(student)
        
        db.commit()
        return {"message": f"{len(df)}명의 학생 데이터가 성공적으로 업로드되었습니다."}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"학생 데이터 처리 중 오류: {str(e)}")

async def generate_student_excel(db: Session):
    """학생 데이터 엑셀 파일 생성"""
    try:
        students = db.query(Student).filter(Student.is_active == True).all()
        
        # DataFrame 생성
        data = []
        for student in students:
            data.append({
                '이름': student.name,
                '이메일': student.email,
                '전화번호': student.phone,
                '학년': student.grade,
                '수강료': student.tuition_fee,
                '상태': '활성' if student.is_active else '비활성',
                '등록일': student.created_at.strftime('%Y-%m-%d')
            })
        
        df = pd.DataFrame(data)
        
        # 엑셀 파일 생성
        filename = f"students_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(EXCEL_DIR, filename)
        df.to_excel(filepath, index=False)
        
        return FileResponse(
            filepath,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"학생 엑셀 파일 생성 중 오류: {str(e)}")

async def rebuild_student_excel(db: Session):
    """학생 엑셀 파일 재생성"""
    return await generate_student_excel(db)

# 강사 데이터 처리 함수들
async def process_teacher_excel(df: pd.DataFrame, db: Session):
    """강사 엑셀 파일 처리"""
    try:
        column_mapping = {
            '이름': 'name',
            '이메일': 'email',
            '전화번호': 'phone',
            '과목': 'subject',
            '시급': 'hourly_rate',
            '상태': 'is_active'
        }
        
        df = df.rename(columns=column_mapping)
        
        for _, row in df.iterrows():
            teacher = Teacher(
                name=row.get('name', ''),
                email=row.get('email', ''),
                phone=row.get('phone', ''),
                subject=row.get('subject', ''),
                hourly_rate=float(row.get('hourly_rate', 0)),
                is_active=row.get('is_active', '활성') == '활성'
            )
            db.add(teacher)
        
        db.commit()
        return {"message": f"{len(df)}명의 강사 데이터가 성공적으로 업로드되었습니다."}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"강사 데이터 처리 중 오류: {str(e)}")

async def generate_teacher_excel(db: Session):
    """강사 데이터 엑셀 파일 생성"""
    try:
        teachers = db.query(Teacher).filter(Teacher.is_active == True).all()
        
        data = []
        for teacher in teachers:
            data.append({
                '이름': teacher.name,
                '이메일': teacher.email,
                '전화번호': teacher.phone,
                '과목': teacher.subject,
                '시급': teacher.hourly_rate,
                '상태': '활성' if teacher.is_active else '비활성',
                '등록일': teacher.created_at.strftime('%Y-%m-%d')
            })
        
        df = pd.DataFrame(data)
        filename = f"teachers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(EXCEL_DIR, filename)
        df.to_excel(filepath, index=False)
        
        return FileResponse(
            filepath,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"강사 엑셀 파일 생성 중 오류: {str(e)}")

async def rebuild_teacher_excel(db: Session):
    """강사 엑셀 파일 재생성"""
    return await generate_teacher_excel(db)

# 교재 데이터 처리 함수들
async def process_material_excel(df: pd.DataFrame, db: Session):
    """교재 엑셀 파일 처리"""
    try:
        column_mapping = {
            '교재명': 'name',
            '과목': 'subject',
            '학년': 'grade',
            '출판사': 'publisher',
            '저자': 'author',
            'ISBN': 'isbn',
            '수량': 'quantity',
            '가격': 'price',
            '상태': 'is_active'
        }
        
        df = df.rename(columns=column_mapping)
        
        for _, row in df.iterrows():
            material = Material(
                name=row.get('name', ''),
                subject=row.get('subject', ''),
                grade=row.get('grade', ''),
                publisher=row.get('publisher', ''),
                author=row.get('author', ''),
                isbn=row.get('isbn', ''),
                quantity=int(row.get('quantity', 0)),
                min_quantity=int(row.get('quantity', 0) // 2),  # 기본값
                price=float(row.get('price', 0)),
                is_active=row.get('is_active', '활성') == '활성'
            )
            db.add(material)
        
        db.commit()
        return {"message": f"{len(df)}개의 교재 데이터가 성공적으로 업로드되었습니다."}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"교재 데이터 처리 중 오류: {str(e)}")

async def generate_material_excel(db: Session):
    """교재 데이터 엑셀 파일 생성"""
    try:
        materials = db.query(Material).filter(Material.is_active == True).all()
        
        data = []
        for material in materials:
            data.append({
                '교재명': material.name,
                '과목': material.subject,
                '학년': material.grade,
                '출판사': material.publisher,
                '저자': material.author,
                'ISBN': material.isbn,
                '수량': material.quantity,
                '가격': material.price,
                '상태': '활성' if material.is_active else '비활성',
                '등록일': material.created_at.strftime('%Y-%m-%d')
            })
        
        df = pd.DataFrame(data)
        filename = f"materials_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(EXCEL_DIR, filename)
        df.to_excel(filepath, index=False)
        
        return FileResponse(
            filepath,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"교재 엑셀 파일 생성 중 오류: {str(e)}")

async def rebuild_material_excel(db: Session):
    """교재 엑셀 파일 재생성"""
    return await generate_material_excel(db)

# 강의 데이터 처리 함수들
async def process_lecture_excel(df: pd.DataFrame, db: Session):
    """강의 엑셀 파일 처리"""
    try:
        column_mapping = {
            '강의명': 'title',
            '과목': 'subject',
            '학년': 'grade',
            '최대인원': 'max_students',
            '현재인원': 'current_students',
            '수강료': 'tuition_fee',
            '스케줄': 'schedule',
            '강의실': 'classroom',
            '상태': 'is_active'
        }
        
        df = df.rename(columns=column_mapping)
        
        for _, row in df.iterrows():
            lecture = Lecture(
                title=row.get('title', ''),
                subject=row.get('subject', ''),
                grade=row.get('grade', ''),
                max_students=int(row.get('max_students', 0)),
                current_students=int(row.get('current_students', 0)),
                tuition_fee=int(row.get('tuition_fee', 0)),
                schedule=row.get('schedule', ''),
                classroom=row.get('classroom', ''),
                is_active=row.get('is_active', '활성') == '활성'
            )
            db.add(lecture)
        
        db.commit()
        return {"message": f"{len(df)}개의 강의 데이터가 성공적으로 업로드되었습니다."}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"강의 데이터 처리 중 오류: {str(e)}")

async def generate_lecture_excel(db: Session):
    """강의 데이터 엑셀 파일 생성"""
    try:
        lectures = db.query(Lecture).filter(Lecture.is_active == True).all()
        
        data = []
        for lecture in lectures:
            data.append({
                '강의명': lecture.title,
                '과목': lecture.subject,
                '학년': lecture.grade,
                '최대인원': lecture.max_students,
                '현재인원': lecture.current_students,
                '수강료': lecture.tuition_fee,
                '스케줄': lecture.schedule,
                '강의실': lecture.classroom,
                '상태': '활성' if lecture.is_active else '비활성',
                '등록일': lecture.created_at.strftime('%Y-%m-%d')
            })
        
        df = pd.DataFrame(data)
        filename = f"lectures_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(EXCEL_DIR, filename)
        df.to_excel(filepath, index=False)
        
        return FileResponse(
            filepath,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"강의 엑셀 파일 생성 중 오류: {str(e)}")

async def rebuild_lecture_excel(db: Session):
    """강의 엑셀 파일 재생성"""
    return await generate_lecture_excel(db) 