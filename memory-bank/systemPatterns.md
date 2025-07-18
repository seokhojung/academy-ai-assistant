# System Patterns

## 아키텍처 패턴

### 1. Command Pattern (Undo/Redo 시스템)
**목적**: 사용자 작업의 실행/취소/재실행을 위한 표준 패턴

#### 구조
```typescript
interface Command {
  execute(): Promise<void>;
  undo(): Promise<void>;
}

class HistoryManager {
  private commands: Command[] = [];
  private currentIndex = -1;
  
  async executeCommand(command: Command) {
    await command.execute();
    this.commands = this.commands.slice(0, this.currentIndex + 1);
    this.commands.push(command);
    this.currentIndex++;
  }
  
  async undo() {
    if (this.currentIndex >= 0) {
      await this.commands[this.currentIndex].undo();
      this.currentIndex--;
    }
  }
  
  async redo() {
    if (this.currentIndex < this.commands.length - 1) {
      this.currentIndex++;
      await this.commands[this.currentIndex].execute();
    }
  }
}
```

#### 장점
- ✅ **표준 패턴**: 검증된 방법론
- ✅ **확장성**: 새로운 명령어 추가 용이
- ✅ **테스트 용이성**: 각 Command 독립 테스트
- ✅ **에러 처리**: 각 단계별 에러 처리 가능

#### 구현 예시
```typescript
class EditStudentCommand implements Command {
  constructor(
    private studentId: number,
    private oldData: any,
    private newData: any,
    private apiClient: ApiClient
  ) {}
  
  async execute() {
    await this.apiClient.updateStudent(this.studentId, this.newData);
  }
  
  async undo() {
    await this.apiClient.updateStudent(this.studentId, this.oldData);
  }
}
```

### 2. 환경별 전략 패턴

#### 로컬 개발 환경
- **메모리 기반 히스토리**: 빠른 응답
- **즉시 로컬 반영**: 편집 시 즉시 상태 업데이트
- **디버깅 지원**: 콘솔 로그 및 상태 추적

#### 웹 배포 환경
- **하이브리드 방식**: 로컬 캐시 + 서버 동기화
- **데이터 일관성**: 편집 시 즉시 서버 반영
- **에러 복구**: 네트워크 오류 시 자동 롤백

### 3. 상태 관리 패턴

#### Command Stack 관리
```typescript
interface CommandState {
  commands: Command[];
  currentIndex: number;
  canUndo: boolean;
  canRedo: boolean;
}
```

#### 데이터 상태 동기화
```typescript
interface DataState {
  localData: any[];
  serverData: any[];
  isSynchronized: boolean;
  lastSyncTime: Date;
}
```

## 컴포넌트 패턴

### 1. ExcelPreviewTable 컴포넌트
**역할**: 엑셀 미리보기 및 데이터 편집 인터페이스

#### 의존성
- HistoryManager: Undo/Redo 기능
- ApiClient: 서버 통신
- DataGrid: 데이터 표시 및 편집

#### 상태 관리
```typescript
interface ExcelPreviewTableState {
  data: any[];
  loading: boolean;
  error: string | null;
  historyManager: HistoryManager;
  hasUnsavedChanges: boolean;
}
```

### 2. HistoryManager 훅
**역할**: Command Pattern 기반 히스토리 관리

#### 인터페이스
```typescript
interface UseHistoryManager {
  executeCommand: (command: Command) => Promise<void>;
  undo: () => Promise<void>;
  redo: () => Promise<void>;
  canUndo: boolean;
  canRedo: boolean;
  clearHistory: () => void;
}
```

## 데이터 플로우 패턴

### 1. 편집 플로우
```
사용자 편집 → Command 생성 → HistoryManager.executeCommand() → 
서버 API 호출 → 로컬 상태 업데이트 → UI 업데이트
```

### 2. Undo 플로우
```
Undo 버튼 클릭 → HistoryManager.undo() → 
Command.undo() → 서버 API 호출 → 로컬 상태 업데이트 → UI 업데이트
```

### 3. Redo 플로우
```
Redo 버튼 클릭 → HistoryManager.redo() → 
Command.execute() → 서버 API 호출 → 로컬 상태 업데이트 → UI 업데이트
```

## 에러 처리 패턴

### 1. Command 실행 실패
```typescript
try {
  await command.execute();
} catch (error) {
  // 1. 로컬 상태 롤백
  // 2. 사용자에게 에러 알림
  // 3. 히스토리에서 해당 Command 제거
}
```

### 2. 네트워크 오류 복구
```typescript
class NetworkErrorHandler {
  static async retryWithBackoff<T>(
    operation: () => Promise<T>,
    maxRetries: number = 3
  ): Promise<T> {
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await operation();
      } catch (error) {
        if (i === maxRetries - 1) throw error;
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
      }
    }
  }
}
```

## 테스트 패턴

### 1. Command 단위 테스트
```typescript
describe('EditStudentCommand', () => {
  it('should execute successfully', async () => {
    const command = new EditStudentCommand(1, oldData, newData, mockApiClient);
    await command.execute();
    expect(mockApiClient.updateStudent).toHaveBeenCalledWith(1, newData);
  });
  
  it('should undo successfully', async () => {
    const command = new EditStudentCommand(1, oldData, newData, mockApiClient);
    await command.undo();
    expect(mockApiClient.updateStudent).toHaveBeenCalledWith(1, oldData);
  });
});
```

### 2. HistoryManager 통합 테스트
```typescript
describe('HistoryManager', () => {
  it('should handle undo/redo correctly', async () => {
    const manager = new HistoryManager();
    const command = new EditStudentCommand(1, oldData, newData, mockApiClient);
    
    await manager.executeCommand(command);
    expect(manager.canUndo()).toBe(true);
    
    await manager.undo();
    expect(manager.canRedo()).toBe(true);
    
    await manager.redo();
    expect(manager.canUndo()).toBe(true);
  });
});
```

## 성능 최적화 패턴

### 1. Command 배치 처리
```typescript
class BatchCommand implements Command {
  constructor(private commands: Command[]) {}
  
  async execute() {
    await Promise.all(this.commands.map(cmd => cmd.execute()));
  }
  
  async undo() {
    await Promise.all(this.commands.map(cmd => cmd.undo()));
  }
}
```

### 2. 메모리 관리
```typescript
class HistoryManager {
  private maxCommands = 100; // 최대 히스토리 개수 제한
  
  private cleanupOldCommands() {
    if (this.commands.length > this.maxCommands) {
      this.commands = this.commands.slice(-this.maxCommands);
      this.currentIndex = Math.min(this.currentIndex, this.commands.length - 1);
    }
  }
}
``` 