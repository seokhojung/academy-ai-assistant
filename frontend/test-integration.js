/**
 * Academy AI Assistant 프론트엔드 연동 테스트
 * Next.js와 백엔드 API 연동을 테스트합니다.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const FRONTEND_URL = process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000';

class FrontendIntegrationTester {
    constructor() {
        this.testResults = {};
        this.session = null;
    }

    printHeader(title) {
        console.log('\n' + '='.repeat(60));
        console.log(`  ${title}`);
        console.log('='.repeat(60));
    }

    printResult(testName, success, message = '', data = null) {
        const status = success ? '✅ PASS' : '❌ FAIL';
        console.log(`${status} ${testName}`);
        if (message) {
            console.log(`   └─ ${message}`);
        }
        if (data) {
            console.log(`   └─ 데이터: ${JSON.stringify(data, null, 2)}`);
        }
        this.testResults[testName] = success;
    }

    async testBackendConnection() {
        this.printHeader('백엔드 연결 테스트');

        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            if (response.ok) {
                const data = await response.json();
                this.printResult('백엔드 서버 연결', true, '서버 정상 동작');
                return true;
            } else {
                this.printResult('백엔드 서버 연결', false, `HTTP ${response.status}`);
                return false;
            }
        } catch (error) {
            this.printResult('백엔드 서버 연결', false, `연결 실패: ${error.message}`);
            return false;
        }
    }

    async testFrontendConnection() {
        this.printHeader('프론트엔드 연결 테스트');

        try {
            const response = await fetch(`${FRONTEND_URL}/api/health`);
            if (response.ok) {
                const data = await response.json();
                this.printResult('프론트엔드 서버 연결', true, '서버 정상 동작');
                return true;
            } else {
                this.printResult('프론트엔드 서버 연결', false, `HTTP ${response.status}`);
                return false;
            }
        } catch (error) {
            this.printResult('프론트엔드 서버 연결', false, `연결 실패: ${error.message}`);
            return false;
        }
    }

    async testAuthentication() {
        this.printHeader('인증 시스템 테스트');

        try {
            // 1. 로그인 테스트
            const loginData = {
                email: 'test@example.com',
                password: 'testpassword'
            };

            const loginResponse = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(loginData)
            });

            if (loginResponse.ok) {
                const loginResult = await loginResponse.json();
                this.session = loginResult.access_token;
                this.printResult('로그인 API', true, '로그인 성공');
            } else {
                this.printResult('로그인 API', false, `HTTP ${loginResponse.status}`);
                // 테스트용 JWT 토큰 생성 (실제로는 프론트엔드에서 처리)
                this.session = 'test-jwt-token';
            }

            // 2. 인증된 요청 테스트
            if (this.session) {
                const authResponse = await fetch(`${API_BASE_URL}/api/v1/students/`, {
                    headers: {
                        'Authorization': `Bearer ${this.session}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (authResponse.ok) {
                    this.printResult('인증된 API 요청', true, '인증 헤더 정상 처리');
                } else {
                    this.printResult('인증된 API 요청', false, `HTTP ${authResponse.status}`);
                }
            }

            return true;
        } catch (error) {
            this.printResult('인증 시스템 테스트', false, `오류: ${error.message}`);
            return false;
        }
    }

    async testStudentAPI() {
        this.printHeader('학생 API 연동 테스트');

        try {
            // 1. 학생 목록 조회
            const listResponse = await fetch(`${API_BASE_URL}/api/v1/students/`, {
                headers: {
                    'Authorization': `Bearer ${this.session}`,
                    'Content-Type': 'application/json'
                }
            });

            if (listResponse.ok) {
                const students = await listResponse.json();
                this.printResult('학생 목록 조회', true, `총 ${students.total || 0}명의 학생`);
            } else {
                this.printResult('학생 목록 조회', false, `HTTP ${listResponse.status}`);
            }

            // 2. 학생 등록
            const newStudent = {
                name: '테스트 학생',
                email: `test.student.${Date.now()}@example.com`,
                phone: '010-1234-5678',
                grade: '고등학교 1학년',
                tuition_fee: 500000.0,
                tuition_due_date: '2024-12-31T00:00:00'
            };

            const createResponse = await fetch(`${API_BASE_URL}/api/v1/students/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.session}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newStudent)
            });

            if (createResponse.ok) {
                const createdStudent = await createResponse.json();
                this.printResult('학생 등록', true, `학생 ID: ${createdStudent.id}`);

                // 3. 학생 상세 조회
                const detailResponse = await fetch(`${API_BASE_URL}/api/v1/students/${createdStudent.id}`, {
                    headers: {
                        'Authorization': `Bearer ${this.session}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (detailResponse.ok) {
                    const studentDetail = await detailResponse.json();
                    this.printResult('학생 상세 조회', true, `이름: ${studentDetail.name}`);
                } else {
                    this.printResult('학생 상세 조회', false, `HTTP ${detailResponse.status}`);
                }
            } else {
                this.printResult('학생 등록', false, `HTTP ${createResponse.status}`);
            }

            return true;
        } catch (error) {
            this.printResult('학생 API 연동 테스트', false, `오류: ${error.message}`);
            return false;
        }
    }

    async testTeacherAPI() {
        this.printHeader('강사 API 연동 테스트');

        try {
            // 1. 강사 목록 조회
            const listResponse = await fetch(`${API_BASE_URL}/api/v1/teachers/`, {
                headers: {
                    'Authorization': `Bearer ${this.session}`,
                    'Content-Type': 'application/json'
                }
            });

            if (listResponse.ok) {
                const teachers = await listResponse.json();
                this.printResult('강사 목록 조회', true, `총 ${teachers.total || 0}명의 강사`);
            } else {
                this.printResult('강사 목록 조회', false, `HTTP ${listResponse.status}`);
            }

            // 2. 강사 등록
            const newTeacher = {
                name: '테스트 강사',
                email: `test.teacher.${Date.now()}@example.com`,
                phone: '010-1111-2222',
                specialty: '수학'
            };

            const createResponse = await fetch(`${API_BASE_URL}/api/v1/teachers/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.session}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newTeacher)
            });

            if (createResponse.ok) {
                const createdTeacher = await createResponse.json();
                this.printResult('강사 등록', true, `강사 ID: ${createdTeacher.id}`);
            } else {
                this.printResult('강사 등록', false, `HTTP ${createResponse.status}`);
            }

            return true;
        } catch (error) {
            this.printResult('강사 API 연동 테스트', false, `오류: ${error.message}`);
            return false;
        }
    }

    async testMaterialAPI() {
        this.printHeader('교재 API 연동 테스트');

        try {
            // 1. 교재 목록 조회
            const listResponse = await fetch(`${API_BASE_URL}/api/v1/materials/`, {
                headers: {
                    'Authorization': `Bearer ${this.session}`,
                    'Content-Type': 'application/json'
                }
            });

            if (listResponse.ok) {
                const materials = await listResponse.json();
                this.printResult('교재 목록 조회', true, `총 ${materials.total || 0}개의 교재`);
            } else {
                this.printResult('교재 목록 조회', false, `HTTP ${listResponse.status}`);
            }

            // 2. 교재 등록
            const newMaterial = {
                title: '테스트 교재',
                author: '테스트 저자',
                publisher: '테스트 출판사',
                isbn: `978-${Date.now()}`,
                stock: 10,
                price: 25000.0
            };

            const createResponse = await fetch(`${API_BASE_URL}/api/v1/materials/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.session}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newMaterial)
            });

            if (createResponse.ok) {
                const createdMaterial = await createResponse.json();
                this.printResult('교재 등록', true, `교재 ID: ${createdMaterial.id}`);
            } else {
                this.printResult('교재 등록', false, `HTTP ${createResponse.status}`);
            }

            return true;
        } catch (error) {
            this.printResult('교재 API 연동 테스트', false, `오류: ${error.message}`);
            return false;
        }
    }

    async testAIChatAPI() {
        this.printHeader('AI 채팅 API 연동 테스트');

        try {
            // 1. 기본 채팅 테스트
            const chatMessage = {
                message: '안녕하세요! 학원 관리 시스템에 대해 간단히 설명해주세요.'
            };

            const chatResponse = await fetch(`${API_BASE_URL}/api/v1/ai/chat`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.session}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(chatMessage)
            });

            if (chatResponse.ok) {
                const chatResult = await chatResponse.json();
                this.printResult('AI 채팅', true, `응답 길이: ${chatResult.response?.length || 0} 문자`);
            } else {
                this.printResult('AI 채팅', false, `HTTP ${chatResponse.status}`);
            }

            // 2. 자연어 명령 테스트
            const commandMessage = {
                command: '김철수 학생의 수강료 납부 현황을 알려주세요'
            };

            const commandResponse = await fetch(`${API_BASE_URL}/api/v1/ai/command`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.session}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(commandMessage)
            });

            if (commandResponse.ok) {
                const commandResult = await commandResponse.json();
                this.printResult('자연어 명령', true, '명령 파싱 완료');
            } else {
                this.printResult('자연어 명령', false, `HTTP ${commandResponse.status}`);
            }

            return true;
        } catch (error) {
            this.printResult('AI 채팅 API 연동 테스트', false, `오류: ${error.message}`);
            return false;
        }
    }

    async testExcelAPI() {
        this.printHeader('Excel API 연동 테스트');

        try {
            // 1. Excel 재생성 요청
            const rebuildResponse = await fetch(`${API_BASE_URL}/api/v1/excel/rebuild/students`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.session}`,
                    'Content-Type': 'application/json'
                }
            });

            if (rebuildResponse.ok) {
                const rebuildResult = await rebuildResponse.json();
                this.printResult('Excel 재생성 요청', true, `태스크 ID: ${rebuildResult.task_id}`);

                // 2. 태스크 상태 확인
                if (rebuildResult.task_id) {
                    const statusResponse = await fetch(`${API_BASE_URL}/api/v1/excel/status/${rebuildResult.task_id}`, {
                        headers: {
                            'Authorization': `Bearer ${this.session}`,
                            'Content-Type': 'application/json'
                        }
                    });

                    if (statusResponse.ok) {
                        const statusResult = await statusResponse.json();
                        this.printResult('Excel 재생성 상태 확인', true, `상태: ${statusResult.status}`);
                    } else {
                        this.printResult('Excel 재생성 상태 확인', false, `HTTP ${statusResponse.status}`);
                    }
                }
            } else {
                this.printResult('Excel 재생성 요청', false, `HTTP ${rebuildResponse.status}`);
            }

            return true;
        } catch (error) {
            this.printResult('Excel API 연동 테스트', false, `오류: ${error.message}`);
            return false;
        }
    }

    async testFrontendPages() {
        this.printHeader('프론트엔드 페이지 테스트');

        try {
            const pages = [
                { path: '/', name: '홈페이지' },
                { path: '/students', name: '학생 관리' },
                { path: '/teachers', name: '강사 관리' },
                { path: '/materials', name: '교재 관리' },
                { path: '/chat', name: 'AI 채팅' },
                { path: '/excel', name: 'Excel 관리' }
            ];

            for (const page of pages) {
                try {
                    const response = await fetch(`${FRONTEND_URL}${page.path}`);
                    if (response.ok) {
                        this.printResult(`${page.name} 접근`, true, `HTTP ${response.status}`);
                    } else {
                        this.printResult(`${page.name} 접근`, false, `HTTP ${response.status}`);
                    }
                } catch (error) {
                    this.printResult(`${page.name} 접근`, false, `연결 실패: ${error.message}`);
                }
            }

            return true;
        } catch (error) {
            this.printResult('프론트엔드 페이지 테스트', false, `오류: ${error.message}`);
            return false;
        }
    }

    async runAllTests() {
        console.log('Academy AI Assistant 프론트엔드 연동 테스트 시작');
        console.log('='.repeat(60));

        // 백엔드 연결 테스트
        const backendConnected = await this.testBackendConnection();
        if (!backendConnected) {
            console.log('❌ 백엔드 서버가 실행되지 않았습니다. 먼저 서버를 시작해주세요.');
            return false;
        }

        // 프론트엔드 연결 테스트
        const frontendConnected = await this.testFrontendConnection();
        if (!frontendConnected) {
            console.log('❌ 프론트엔드 서버가 실행되지 않았습니다. 먼저 서버를 시작해주세요.');
            return false;
        }

        // 인증 테스트
        await this.testAuthentication();

        // API 연동 테스트
        await this.testStudentAPI();
        await this.testTeacherAPI();
        await this.testMaterialAPI();
        await this.testAIChatAPI();
        await this.testExcelAPI();

        // 프론트엔드 페이지 테스트
        await this.testFrontendPages();

        // 결과 요약
        this.printHeader('프론트엔드 연동 테스트 결과 요약');

        const totalTests = Object.keys(this.testResults).length;
        const passedTests = Object.values(this.testResults).filter(result => result).length;
        const failedTests = totalTests - passedTests;

        console.log(`총 테스트: ${totalTests}`);
        console.log(`성공: ${passedTests}`);
        console.log(`실패: ${failedTests}`);
        console.log(`성공률: ${((passedTests / totalTests) * 100).toFixed(1)}%`);

        if (failedTests > 0) {
            console.log('\n실패한 테스트:');
            for (const [testName, result] of Object.entries(this.testResults)) {
                if (!result) {
                    console.log(`  - ${testName}`);
                }
            }
        }

        console.log('\n' + '='.repeat(60));

        if (failedTests === 0) {
            console.log('🎉 모든 프론트엔드 연동 테스트가 성공했습니다!');
            console.log('Next.js와 백엔드 API가 정상적으로 연동됩니다.');
        } else {
            console.log('⚠️  일부 프론트엔드 연동 테스트가 실패했습니다.');
            console.log('실패한 항목을 확인하고 수정해주세요.');
        }

        return failedTests === 0;
    }
}

// Node.js 환경에서 실행
if (typeof window === 'undefined') {
    const tester = new FrontendIntegrationTester();
    
    console.log('프론트엔드 연동 테스트를 시작하기 전에 다음을 확인해주세요:');
    console.log('1. FastAPI 서버가 실행 중인지 확인');
    console.log('2. Next.js 개발 서버가 실행 중인지 확인');
    console.log('3. 환경 변수가 올바르게 설정되었는지 확인');
    console.log('\n계속하시겠습니까? (y/n): ');
    
    process.stdin.once('data', async (data) => {
        const response = data.toString().trim().toLowerCase();
        if (response === 'y' || response === 'yes' || response === '예') {
            const success = await tester.runAllTests();
            
            if (success) {
                console.log('\n다음 단계:');
                console.log('1. 실제 사용자 인터페이스 테스트');
                console.log('2. 성능 테스트');
                console.log('3. 보안 테스트');
            } else {
                console.log('\n확인이 필요한 항목:');
                console.log('1. 서버 실행 상태');
                console.log('2. API 엔드포인트 구현');
                console.log('3. 환경 변수 설정');
                console.log('4. 네트워크 연결 상태');
            }
            
            process.exit(success ? 0 : 1);
        } else {
            console.log('테스트를 취소했습니다.');
            process.exit(0);
        }
    });
}

// 브라우저 환경에서 실행
if (typeof window !== 'undefined') {
    window.FrontendIntegrationTester = FrontendIntegrationTester;
}

module.exports = FrontendIntegrationTester; 