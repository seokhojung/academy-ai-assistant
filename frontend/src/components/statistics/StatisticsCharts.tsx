import React from 'react';
import { Chart } from '@/components/ui/Chart';
import { 
  StudentStatistics, 
  LectureStatistics, 
  TeacherStatistics, 
  MaterialStatistics 
} from '@/hooks/useStatistics';

interface StatisticsChartsProps {
  studentStats?: StudentStatistics;
  lectureStats?: LectureStatistics;
  teacherStats?: TeacherStatistics;
  materialStats?: MaterialStatistics;
}

export const StudentStatisticsChart: React.FC<{ data?: StudentStatistics }> = ({ data }) => {
  if (!data) return <div>데이터를 불러오는 중...</div>;

  // 학년별 분포 차트 데이터
  const gradeData = Object.entries(data.grade_distribution).map(([grade, count]) => ({
    name: grade,
    value: count,
    count: count
  }));

  return (
    <div className="space-y-6">
      <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">학년별 학생 분포</h3>
        <Chart
          data={gradeData}
          type="pie"
          title="학년별 학생 분포"
          xAxisKey="name"
          yAxisKey="count"
          colors={['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">학생 상태</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">전체 학생</span>
              <span className="font-semibold text-gray-900 dark:text-white">{data.total_students}명</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">활성 학생</span>
              <span className="font-semibold text-green-600 dark:text-green-400">{data.active_students}명</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">비활성 학생</span>
              <span className="font-semibold text-red-600 dark:text-red-400">{data.inactive_students}명</span>
            </div>
          </div>
        </div>

        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">수강료 현황</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">총 수익</span>
              <span className="font-semibold text-blue-600 dark:text-blue-400">
                {data.tuition_stats.total_revenue.toLocaleString()}원
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">평균 수강료</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                {data.tuition_stats.average_tuition.toLocaleString()}원
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">체납 학생</span>
              <span className="font-semibold text-orange-600 dark:text-orange-400">
                {data.tuition_stats.overdue_count}명
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export const LectureStatisticsChart: React.FC<{ data?: LectureStatistics }> = ({ data }) => {
  if (!data) return <div>데이터를 불러오는 중...</div>;

  // 과목별 분포 차트 데이터
  const subjectData = Object.entries(data.subject_distribution).map(([subject, count]) => ({
    name: subject,
    value: count,
    count: count
  }));

  // 학년별 분포 차트 데이터
  const gradeData = Object.entries(data.grade_distribution).map(([grade, count]) => ({
    name: grade,
    value: count,
    count: count
  }));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">과목별 강의 분포</h3>
          <Chart
            data={subjectData}
            type="bar"
            title="과목별 강의 수"
            xAxisKey="name"
            yAxisKey="count"
            colors={['#3B82F6']}
          />
        </div>

        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">학년별 강의 분포</h3>
          <Chart
            data={gradeData}
            type="bar"
            title="학년별 강의 수"
            xAxisKey="name"
            yAxisKey="count"
            colors={['#10B981']}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">강의 현황</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">전체 강의</span>
              <span className="font-semibold text-gray-900 dark:text-white">{data.total_lectures}개</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">활성 강의</span>
              <span className="font-semibold text-green-600 dark:text-green-400">{data.active_lectures}개</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">비활성 강의</span>
              <span className="font-semibold text-red-600 dark:text-red-400">{data.inactive_lectures}개</span>
            </div>
          </div>
        </div>

        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">수강률 및 수익</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">평균 수강률</span>
              <span className="font-semibold text-blue-600 dark:text-blue-400">
                {data.enrollment_stats.enrollment_rate.toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">총 수강생</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                {data.enrollment_stats.total_enrollments}명
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">총 수익</span>
              <span className="font-semibold text-green-600 dark:text-green-400">
                {data.revenue_stats.total_revenue.toLocaleString()}원
              </span>
            </div>
          </div>
        </div>
      </div>

      {data.popular_lectures.length > 0 && (
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">인기 강의 TOP 5</h3>
          <div className="space-y-3">
            {data.popular_lectures.map((lecture, index) => (
              <div key={lecture.id} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <span className="text-sm font-medium text-gray-500 dark:text-gray-400">#{index + 1}</span>
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">{lecture.title}</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">{lecture.subject}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-gray-900 dark:text-white">
                    {lecture.current_students}/{lecture.max_students}명
                  </div>
                  <div className="text-sm text-blue-600 dark:text-blue-400">
                    {lecture.enrollment_rate.toFixed(1)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export const TeacherStatisticsChart: React.FC<{ data?: TeacherStatistics }> = ({ data }) => {
  if (!data) return <div>데이터를 불러오는 중...</div>;

  // 과목별 강사 분포 차트 데이터
  const subjectData = Object.entries(data.subject_teacher_distribution).map(([subject, count]) => ({
    name: subject,
    value: count,
    count: count
  }));

  return (
    <div className="space-y-6">
      <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">과목별 강사 분포</h3>
        <Chart
          data={subjectData}
          type="pie"
          title="과목별 강사 수"
          xAxisKey="name"
          yAxisKey="count"
          colors={['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">강사 현황</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">전체 강사</span>
              <span className="font-semibold text-gray-900 dark:text-white">{data.total_teachers}명</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">활성 강사</span>
              <span className="font-semibold text-green-600 dark:text-green-400">{data.active_teachers}명</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">비활성 강사</span>
              <span className="font-semibold text-red-600 dark:text-red-400">{data.inactive_teachers}명</span>
            </div>
          </div>
        </div>

        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">강사 성과 요약</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">평균 강의 수</span>
              <span className="font-semibold text-blue-600 dark:text-blue-400">
                {(data.teacher_performance.reduce((sum, t) => sum + t.lecture_count, 0) / Math.max(data.teacher_performance.length, 1)).toFixed(1)}개
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">평균 학생 수</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                {(data.teacher_performance.reduce((sum, t) => sum + t.total_students, 0) / Math.max(data.teacher_performance.length, 1)).toFixed(1)}명
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">평균 수강률</span>
              <span className="font-semibold text-green-600 dark:text-green-400">
                {(data.teacher_performance.reduce((sum, t) => sum + t.average_enrollment_rate, 0) / Math.max(data.teacher_performance.length, 1)).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {data.teacher_performance.length > 0 && (
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">강사별 성과</h3>
          <div className="space-y-3">
            {data.teacher_performance.map((teacher) => (
              <div key={teacher.teacher_id} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">{teacher.teacher_name}</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      강의 {teacher.lecture_count}개
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-gray-900 dark:text-white">
                    {teacher.total_students}명
                  </div>
                  <div className="text-sm text-blue-600 dark:text-blue-400">
                    {teacher.average_enrollment_rate}% 수강률
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export const MaterialStatisticsChart: React.FC<{ data?: MaterialStatistics }> = ({ data }) => {
  if (!data) return <div>데이터를 불러오는 중...</div>;

  // 과목별 교재 분포 차트 데이터
  const subjectData = Object.entries(data.subject_distribution).map(([subject, count]) => ({
    name: subject,
    value: count,
    count: count
  }));

  return (
    <div className="space-y-6">
      <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">과목별 교재 분포</h3>
        <Chart
          data={subjectData}
          type="pie"
          title="과목별 교재 수"
          xAxisKey="name"
          yAxisKey="count"
          colors={['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">교재 현황</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">전체 교재</span>
              <span className="font-semibold text-gray-900 dark:text-white">{data.total_materials}종</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">활성 교재</span>
              <span className="font-semibold text-green-600 dark:text-green-400">{data.active_materials}종</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">비활성 교재</span>
              <span className="font-semibold text-red-600 dark:text-red-400">{data.inactive_materials}종</span>
            </div>
          </div>
        </div>

        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">교재 사용 현황</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">사용 중인 교재</span>
              <span className="font-semibold text-blue-600 dark:text-blue-400">
                {data.material_usage.filter(m => m.usage_count > 0).length}종
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">미사용 교재</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                {data.material_usage.filter(m => m.usage_count === 0).length}종
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">평균 사용 횟수</span>
              <span className="font-semibold text-green-600 dark:text-green-400">
                {(data.material_usage.reduce((sum, m) => sum + m.usage_count, 0) / Math.max(data.material_usage.length, 1)).toFixed(1)}회
              </span>
            </div>
          </div>
        </div>
      </div>

      {data.material_usage.length > 0 && (
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">교재별 사용 현황</h3>
          <div className="space-y-3">
            {data.material_usage
              .sort((a, b) => b.usage_count - a.usage_count)
              .slice(0, 10)
              .map((material) => (
                <div key={material.material_id} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">{material.material_name}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">{material.subject}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900 dark:text-white">
                      {material.usage_count}회 사용
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}; 