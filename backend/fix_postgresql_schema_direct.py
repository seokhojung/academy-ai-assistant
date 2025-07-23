#!/usr/bin/env python3
"""
PostgreSQL 스키마 직접 수정 스크립트
이 스크립트는 PostgreSQL에 직접 접근하여 material 테이블의 누락된 컬럼들을 추가합니다.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 환경 변수에서 데이터베이스 URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL 환경 변수가 설정되지 않았습니다.")
    print("Render 대시보드에서 DATABASE_URL을 확인하세요.")
    sys.exit(1)

def fix_postgresql_schema_direct():
    """PostgreSQL 스키마를 직접 수정"""
    try:
        print("🔧 PostgreSQL 스키마 직접 수정 시작...")
        print(f"데이터베이스 URL: {DATABASE_URL[:50]}...")
        
        # 엔진 생성
        engine = create_engine(
            DATABASE_URL,
            echo=True,  # SQL 쿼리 로그 출력
            pool_pre_ping=True,
            pool_recycle=300
        )
        
        # 세션 생성
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            print("\n1️⃣ 기존 material 테이블 컬럼 확인...")
            
            # 현재 material 테이블의 컬럼 확인
            result = session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'material'
                ORDER BY ordinal_position;
            """))
            
            existing_columns = []
            for row in result.fetchall():
                existing_columns.append(row[0])
                print(f"  - {row[0]} ({row[1]}, nullable: {row[2]})")
            
            print(f"\n총 {len(existing_columns)}개 컬럼 발견")
            
            # 추가할 컬럼들
            missing_columns = {
                'author': 'VARCHAR(100)',
                'publisher': 'VARCHAR(100)',
                'isbn': 'VARCHAR(20)',
                'description': 'VARCHAR(500)',
                'publication_date': 'TIMESTAMP',
                'edition': 'VARCHAR(20)',
                'quantity': 'INTEGER',
                'min_quantity': 'INTEGER',
                'price': 'DOUBLE PRECISION',
                'expiry_date': 'TIMESTAMP',
                'is_active': 'BOOLEAN',
                'created_at': 'TIMESTAMP',
                'updated_at': 'TIMESTAMP'
            }
            
            print("\n2️⃣ 누락된 컬럼 추가...")
            
            # 각 컬럼을 개별적으로 추가
            for col_name, col_type in missing_columns.items():
                if col_name not in existing_columns:
                    print(f"  추가 중: {col_name} {col_type}")
                    try:
                        session.execute(text(f"ALTER TABLE material ADD COLUMN {col_name} {col_type}"))
                        session.commit()
                        print(f"    ✅ {col_name} 컬럼 추가 완료")
                    except Exception as e:
                        print(f"    ❌ {col_name} 컬럼 추가 실패: {e}")
                        session.rollback()
                else:
                    print(f"  ✅ {col_name}: 이미 존재")
            
            print("\n3️⃣ 기본값 설정...")
            
            # 기본값 설정
            default_settings = [
                ("ALTER TABLE material ALTER COLUMN is_active SET DEFAULT true", "is_active 기본값"),
                ("ALTER TABLE material ALTER COLUMN quantity SET DEFAULT 0", "quantity 기본값"),
                ("ALTER TABLE material ALTER COLUMN min_quantity SET DEFAULT 5", "min_quantity 기본값"),
                ("ALTER TABLE material ALTER COLUMN price SET DEFAULT 0.0", "price 기본값")
            ]
            
            for sql, description in default_settings:
                try:
                    session.execute(text(sql))
                    session.commit()
                    print(f"  ✅ {description} 설정 완료")
                except Exception as e:
                    print(f"  ❌ {description} 설정 실패: {e}")
                    session.rollback()
            
            print("\n4️⃣ 최종 컬럼 확인...")
            
            # 수정 후 컬럼 확인
            result = session.execute(text("""
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_name = 'material'
                ORDER BY ordinal_position;
            """))
            
            final_columns = []
            for row in result.fetchall():
                final_columns.append(row[0])
                print(f"  - {row[0]} ({row[1]})")
            
            print(f"\n총 {len(final_columns)}개 컬럼")
            
            # 필수 컬럼 확인
            required_columns = ['id', 'name', 'subject', 'grade', 'author']
            missing_required = [col for col in required_columns if col not in final_columns]
            
            if missing_required:
                print(f"\n❌ 여전히 누락된 필수 컬럼: {missing_required}")
                return False
            else:
                print(f"\n✅ 모든 필수 컬럼이 존재합니다!")
                return True
                
    except Exception as e:
        print(f"❌ 스키마 수정 중 오류: {e}")
        return False

def test_material_query():
    """material 테이블 쿼리 테스트"""
    try:
        print("\n🧪 material 테이블 쿼리 테스트...")
        
        engine = create_engine(DATABASE_URL, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # material 테이블에서 모든 컬럼을 포함한 쿼리 실행
            result = session.execute(text("""
                SELECT material.id AS material_id, 
                       material.name AS material_name, 
                       material.subject AS material_subject, 
                       material.grade AS material_grade, 
                       material.author AS material_author, 
                       material.isbn AS material_isbn, 
                       material.description AS material_description, 
                       material.publication_date AS material_publication_date, 
                       material.edition AS material_edition, 
                       material.quantity AS material_quantity, 
                       material.min_quantity AS material_min_quantity, 
                       material.price AS material_price, 
                       material.expiry_date AS material_expiry_date, 
                       material.is_active AS material_is_active, 
                       material.created_at AS material_created_at, 
                       material.updated_at AS material_updated_at 
                FROM material
                LIMIT 1
            """))
            
            # 결과 확인
            row = result.fetchone()
            if row:
                print("✅ material 테이블 쿼리 성공!")
                print(f"  첫 번째 레코드: {row[1]} ({row[2]})")  # name, subject
            else:
                print("✅ material 테이블 쿼리 성공! (데이터 없음)")
                
        return True
        
    except Exception as e:
        print(f"❌ material 테이블 쿼리 실패: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PostgreSQL 스키마 직접 수정 스크립트 시작")
    print("=" * 50)
    
    # 스키마 수정
    success = fix_postgresql_schema_direct()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ 스키마 수정 완료!")
        
        # 테스트 쿼리 실행
        test_success = test_material_query()
        
        if test_success:
            print("\n🎉 모든 작업이 성공적으로 완료되었습니다!")
            print("이제 AI 챗봇이 정상적으로 작동할 것입니다.")
        else:
            print("\n⚠️ 스키마는 수정되었지만 테스트 쿼리에 실패했습니다.")
    else:
        print("\n❌ 스키마 수정에 실패했습니다.")
        print("Render 로그를 확인하여 추가 오류를 확인하세요.") 