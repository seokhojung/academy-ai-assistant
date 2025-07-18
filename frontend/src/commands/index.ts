import { Command } from '../hooks/useHistoryManager';

// API 클라이언트 인터페이스
export interface ApiClient {
  updateEntity(entityType: string, id: number, data: any): Promise<any>;
  createEntity(entityType: string, data: any): Promise<any>;
  deleteEntity(entityType: string, id: number): Promise<any>;
}

// 편집 Command
export class EditEntityCommand implements Command {
  constructor(
    private entityType: string,
    private id: number,
    private oldData: any,
    private newData: any,
    private apiClient: ApiClient,
    private onLocalUpdate: (data: any) => void
  ) {}

  async execute(): Promise<void> {
    // 데이터 검증 및 변환
    const validatedData = this.validateAndTransformData(this.newData);
    await this.apiClient.updateEntity(this.entityType, this.id, validatedData);
    this.onLocalUpdate(validatedData);
  }

  async undo(): Promise<void> {
    // 데이터 검증 및 변환
    const validatedData = this.validateAndTransformData(this.oldData);
    await this.apiClient.updateEntity(this.entityType, this.id, validatedData);
    this.onLocalUpdate(validatedData);
  }

  canExecute(): boolean {
    return this.id && this.newData && this.oldData;
  }

  get description(): string {
    return `${this.entityType} 편집 (ID: ${this.id})`;
  }

  private validateAndTransformData(data: any): any {
    console.log('[EditEntityCommand] 원본 데이터:', data);
    
    const transformed = { ...data };
    
    // is_active 필드 변환 (문자열 -> boolean)
    if (transformed.is_active === "활성") {
      transformed.is_active = true;
    } else if (transformed.is_active === "비활성") {
      transformed.is_active = false;
    }
    
    // 엔티티 타입별 검증 및 변환
    switch (this.entityType) {
      case 'students':
        this.validateStudentData(transformed);
        break;
      case 'teachers':
        this.validateTeacherData(transformed);
        break;
      case 'materials':
        this.validateMaterialData(transformed);
        break;
      case 'lectures':
        this.validateLectureData(transformed);
        break;
      default:
        // 기본 검증
        if (transformed.name === "" || transformed.name === null) {
          throw new Error("이름은 필수입니다.");
        }
    }
    
    console.log('[EditEntityCommand] 변환된 데이터:', transformed);
    return transformed;
  }

  private validateStudentData(data: any): void {
    // tuition_fee 필드 변환 (문자열 -> float)
    if (typeof data.tuition_fee === 'string') {
      const parsed = parseFloat(data.tuition_fee);
      data.tuition_fee = isNaN(parsed) ? 0.0 : parsed;
    }
    
    // tuition_due_date 필드 변환 (빈 문자열 -> null)
    if (data.tuition_due_date === "" || data.tuition_due_date === null) {
      data.tuition_due_date = null;
    }
    
    // phone 필드 변환 (빈 문자열 -> null)
    if (data.phone === "" || data.phone === null) {
      data.phone = null;
    }
    
    // grade 필드 변환 (빈 문자열 -> null)
    if (data.grade === "" || data.grade === null) {
      data.grade = null;
    }
    
    // email 필드 검증 (빈 문자열 방지 및 형식 검증)
    if (data.email === "" || data.email === null) {
      throw new Error("이메일은 필수입니다.");
    }
    
    // 이메일 형식 검증
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(data.email)) {
      throw new Error("유효한 이메일 형식이 아닙니다.");
    }
    
    // name 필드 검증 (빈 문자열 방지)
    if (data.name === "" || data.name === null) {
      throw new Error("이름은 필수입니다.");
    }
  }

  private validateTeacherData(data: any): void {
    // hourly_rate 필드 변환 (문자열 -> float)
    if (typeof data.hourly_rate === 'string') {
      const parsed = parseFloat(data.hourly_rate);
      data.hourly_rate = isNaN(parsed) ? 0.0 : parsed;
    }
    
    // phone 필드 변환 (빈 문자열 -> null)
    if (data.phone === "" || data.phone === null) {
      data.phone = null;
    }
    
    // email 필드 검증 (빈 문자열 방지 및 형식 검증)
    if (data.email === "" || data.email === null) {
      throw new Error("이메일은 필수입니다.");
    }
    
    // 이메일 형식 검증
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(data.email)) {
      throw new Error("유효한 이메일 형식이 아닙니다.");
    }
    
    // name 필드 검증 (빈 문자열 방지)
    if (data.name === "" || data.name === null) {
      throw new Error("이름은 필수입니다.");
    }
    
    // subject 필드 검증 (강사인 경우)
    if (data.subject === "" || data.subject === null) {
      throw new Error("담당 과목은 필수입니다.");
    }
  }

  private validateMaterialData(data: any): void {
    // price 필드 변환 (문자열 -> float)
    if (typeof data.price === 'string') {
      const parsed = parseFloat(data.price);
      data.price = isNaN(parsed) ? 0.0 : parsed;
    }
    
    // quantity 필드 변환 (문자열 -> int)
    if (typeof data.quantity === 'string') {
      const parsed = parseInt(data.quantity);
      data.quantity = isNaN(parsed) ? 0 : parsed;
    }
    
    // min_quantity 필드 변환 (문자열 -> int)
    if (typeof data.min_quantity === 'string') {
      const parsed = parseInt(data.min_quantity);
      data.min_quantity = isNaN(parsed) ? 5 : parsed;
    }
    
    // 빈 문자열을 null로 변환
    const fieldsToNullify = ['description', 'publisher', 'author', 'isbn', 'edition', 'publication_date', 'expiry_date'];
    fieldsToNullify.forEach(field => {
      if (data[field] === "" || data[field] === null) {
        data[field] = null;
      }
    });
    
    // 필수 필드 검증
    if (!data.name || data.name.trim() === "") {
      throw new Error("교재명은 필수입니다.");
    }
    if (!data.subject || data.subject.trim() === "") {
      throw new Error("과목은 필수입니다.");
    }
    if (!data.grade || data.grade.trim() === "") {
      throw new Error("학년은 필수입니다.");
    }
  }

  private validateLectureData(data: any): void {
    // price 필드 변환 (문자열 -> float)
    if (typeof data.price === 'string') {
      const parsed = parseFloat(data.price);
      data.price = isNaN(parsed) ? 0.0 : parsed;
    }
    
    // duration 필드 변환 (문자열 -> int)
    if (typeof data.duration === 'string') {
      const parsed = parseInt(data.duration);
      data.duration = isNaN(parsed) ? 0 : parsed;
    }
    
    // 빈 문자열을 null로 변환
    const fieldsToNullify = ['description', 'location', 'notes'];
    fieldsToNullify.forEach(field => {
      if (data[field] === "" || data[field] === null) {
        data[field] = null;
      }
    });
    
    // 필수 필드 검증
    if (!data.title || data.title.trim() === "") {
      throw new Error("강의 제목은 필수입니다.");
    }
    if (!data.subject || data.subject.trim() === "") {
      throw new Error("과목은 필수입니다.");
    }
  }
}

// 추가 Command
export class AddEntityCommand implements Command {
  private createdId?: number;

  constructor(
    private entityType: string,
    private data: any,
    private apiClient: ApiClient,
    private onLocalAdd: (data: any) => void,
    private onLocalRemove: (id: number) => void
  ) {}

  async execute(): Promise<void> {
    const validatedData = this.validateAndTransformData(this.data);
    const result = await this.apiClient.createEntity(this.entityType, validatedData);
    this.createdId = result.id;
    this.onLocalAdd(result);
  }

  private validateAndTransformData(data: any): any {
    console.log('[AddEntityCommand] 원본 데이터:', data);
    
    const transformed = { ...data };
    
    // is_active 필드 변환 (문자열 -> boolean)
    if (transformed.is_active === "활성") {
      transformed.is_active = true;
    } else if (transformed.is_active === "비활성") {
      transformed.is_active = false;
    }
    
    // price 필드 변환 (문자열 -> float)
    if (typeof transformed.price === 'string') {
      const parsed = parseFloat(transformed.price);
      transformed.price = isNaN(parsed) ? 0.0 : parsed;
    }
    
    // quantity 필드 변환 (문자열 -> int)
    if (typeof transformed.quantity === 'string') {
      const parsed = parseInt(transformed.quantity);
      transformed.quantity = isNaN(parsed) ? 0 : parsed;
    }
    
    // min_quantity 필드 변환 (문자열 -> int)
    if (typeof transformed.min_quantity === 'string') {
      const parsed = parseInt(transformed.min_quantity);
      transformed.min_quantity = isNaN(parsed) ? 5 : parsed;
    }
    
    // 빈 문자열을 null로 변환
    const fieldsToNullify = ['description', 'publisher', 'author', 'isbn', 'edition', 'publication_date', 'expiry_date'];
    fieldsToNullify.forEach(field => {
      if (transformed[field] === "" || transformed[field] === null) {
        transformed[field] = null;
      }
    });
    
    // 필수 필드 검증 및 기본값 설정
    if (this.entityType === 'materials') {
      if (!transformed.name || transformed.name.trim() === "") {
        throw new Error("교재명은 필수입니다.");
      }
      if (!transformed.subject || transformed.subject.trim() === "") {
        throw new Error("과목은 필수입니다.");
      }
      if (!transformed.grade || transformed.grade.trim() === "") {
        throw new Error("학년은 필수입니다.");
      }
    } else if (this.entityType === 'lectures') {
      // 강의 필수 필드 기본값 설정
      if (!transformed.subject || transformed.subject === null) {
        transformed.subject = "미정";
      }
      if (!transformed.grade || transformed.grade === null) {
        transformed.grade = "미정";
      }
      if (!transformed.schedule || transformed.schedule === null) {
        transformed.schedule = "미정";
      }
      if (!transformed.classroom || transformed.classroom === null) {
        transformed.classroom = "미정";
      }
      
      // 필수 필드 검증
      if (!transformed.title || transformed.title.trim() === "") {
        throw new Error("강의 제목은 필수입니다.");
      }
    }
    
    console.log('[AddEntityCommand] 변환된 데이터:', transformed);
    return transformed;
  }

  async undo(): Promise<void> {
    if (this.createdId) {
      await this.apiClient.deleteEntity(this.entityType, this.createdId);
      this.onLocalRemove(this.createdId);
    }
  }

  canExecute(): boolean {
    return this.data && Object.keys(this.data).length > 0;
  }

  get description(): string {
    return `${this.entityType} 추가`;
  }
}

// 삭제 Command
export class DeleteEntityCommand implements Command {
  constructor(
    private entityType: string,
    private id: number,
    private data: any,
    private apiClient: ApiClient,
    private onLocalRemove: (id: number) => void,
    private onLocalAdd: (data: any) => void
  ) {}

  async execute(): Promise<void> {
    await this.apiClient.deleteEntity(this.entityType, this.id);
    this.onLocalRemove(this.id);
  }

  async undo(): Promise<void> {
    await this.apiClient.createEntity(this.entityType, this.data);
    this.onLocalAdd(this.data);
  }

  canExecute(): boolean {
    return this.id && this.data;
  }

  get description(): string {
    return `${this.entityType} 삭제 (ID: ${this.id})`;
  }
}

// 배치 Command (여러 명령어를 한 번에 실행)
export class BatchCommand implements Command {
  private _description: string;

  constructor(
    private commands: Command[],
    description: string = '배치 작업'
  ) {
    this._description = description;
  }

  async execute(): Promise<void> {
    await Promise.all(this.commands.map(cmd => cmd.execute()));
  }

  async undo(): Promise<void> {
    // 역순으로 실행
    for (let i = this.commands.length - 1; i >= 0; i--) {
      await this.commands[i].undo();
    }
  }

  canExecute(): boolean {
    return this.commands.length > 0 && this.commands.every(cmd => cmd.canExecute());
  }

  get description(): string {
    return this._description;
  }
}

// 로컬 상태 변경 Command (서버 호출 없이 로컬만 변경)
export class LocalStateCommand implements Command {
  private _description: string;

  constructor(
    private oldState: any,
    private newState: any,
    private onStateChange: (state: any) => void,
    description: string = '로컬 상태 변경'
  ) {
    this._description = description;
  }

  async execute(): Promise<void> {
    this.onStateChange(this.newState);
  }

  async undo(): Promise<void> {
    this.onStateChange(this.oldState);
  }

  canExecute(): boolean {
    return this.oldState !== undefined && this.newState !== undefined;
  }

  get description(): string {
    return this._description;
  }
} 