"""Add teacher and lecture fields for statistics

Revision ID: 820b0458b417
Revises: 
Create Date: 2025-07-24 10:52:57.611335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '820b0458b417'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lecture', sa.Column('difficulty_level', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('lecture', sa.Column('class_duration', sa.Integer(), nullable=True))
    op.add_column('lecture', sa.Column('total_sessions', sa.Integer(), nullable=True))
    op.add_column('lecture', sa.Column('completed_sessions', sa.Integer(), nullable=True))
    op.add_column('lecture', sa.Column('student_satisfaction', sa.Float(), nullable=True))
    op.add_column('lecture', sa.Column('teacher_rating', sa.Float(), nullable=True))
    op.add_column('teacher', sa.Column('experience_years', sa.Integer(), nullable=True))
    op.add_column('teacher', sa.Column('education_level', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('teacher', sa.Column('specialization', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('teacher', sa.Column('hire_date', sa.DateTime(), nullable=True))
    op.add_column('teacher', sa.Column('contract_type', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('teacher', sa.Column('max_lectures', sa.Integer(), nullable=True))
    op.add_column('teacher', sa.Column('rating', sa.Float(), nullable=True))
    op.add_column('teacher', sa.Column('total_teaching_hours', sa.Integer(), nullable=True))
    op.add_column('teacher', sa.Column('certification', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    
    # 기본값 설정
    op.execute("UPDATE lecture SET difficulty_level = 'intermediate' WHERE difficulty_level IS NULL")
    op.execute("UPDATE lecture SET class_duration = 90 WHERE class_duration IS NULL")
    op.execute("UPDATE lecture SET total_sessions = 16 WHERE total_sessions IS NULL")
    op.execute("UPDATE lecture SET completed_sessions = 0 WHERE completed_sessions IS NULL")
    op.execute("UPDATE teacher SET experience_years = 0 WHERE experience_years IS NULL")
    op.execute("UPDATE teacher SET education_level = 'bachelor' WHERE education_level IS NULL")
    op.execute("UPDATE teacher SET specialization = '' WHERE specialization IS NULL")
    op.execute("UPDATE teacher SET hire_date = CURRENT_TIMESTAMP WHERE hire_date IS NULL")
    op.execute("UPDATE teacher SET contract_type = 'part_time' WHERE contract_type IS NULL")
    op.execute("UPDATE teacher SET max_lectures = 5 WHERE max_lectures IS NULL")
    op.execute("UPDATE teacher SET total_teaching_hours = 0 WHERE total_teaching_hours IS NULL")
    op.execute("UPDATE teacher SET certification = '[]' WHERE certification IS NULL")
    
    # NOT NULL로 변경
    op.alter_column('lecture', 'difficulty_level', nullable=False)
    op.alter_column('lecture', 'class_duration', nullable=False)
    op.alter_column('lecture', 'total_sessions', nullable=False)
    op.alter_column('lecture', 'completed_sessions', nullable=False)
    op.alter_column('teacher', 'experience_years', nullable=False)
    op.alter_column('teacher', 'education_level', nullable=False)
    op.alter_column('teacher', 'specialization', nullable=False)
    op.alter_column('teacher', 'hire_date', nullable=False)
    op.alter_column('teacher', 'contract_type', nullable=False)
    op.alter_column('teacher', 'max_lectures', nullable=False)
    op.alter_column('teacher', 'total_teaching_hours', nullable=False)
    op.alter_column('teacher', 'certification', nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('teacher', 'certification')
    op.drop_column('teacher', 'total_teaching_hours')
    op.drop_column('teacher', 'rating')
    op.drop_column('teacher', 'max_lectures')
    op.drop_column('teacher', 'contract_type')
    op.drop_column('teacher', 'hire_date')
    op.drop_column('teacher', 'specialization')
    op.drop_column('teacher', 'education_level')
    op.drop_column('teacher', 'experience_years')
    op.drop_column('lecture', 'teacher_rating')
    op.drop_column('lecture', 'student_satisfaction')
    op.drop_column('lecture', 'completed_sessions')
    op.drop_column('lecture', 'total_sessions')
    op.drop_column('lecture', 'class_duration')
    op.drop_column('lecture', 'difficulty_level')
    # ### end Alembic commands ###
