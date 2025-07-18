import { useState, useCallback } from 'react';
import { useToast } from './use-toast';

// Command 인터페이스
export interface Command {
  execute(): Promise<void>;
  undo(): Promise<void>;
  canExecute(): boolean;
  description: string;
}

// HistoryManager 클래스
class HistoryManager {
  private commands: Command[] = [];
  private currentIndex = -1;
  private maxCommands = 100; // 최대 히스토리 개수 제한

  async executeCommand(command: Command, toast?: any): Promise<boolean> {
    if (!command.canExecute()) {
      console.warn('Command cannot be executed:', command.description);
      return false;
    }

    try {
      await command.execute();
      
      // 현재 인덱스 이후의 히스토리 제거 (새로운 분기)
      this.commands = this.commands.slice(0, this.currentIndex + 1);
      this.commands.push(command);
      this.currentIndex++;
      
      // 메모리 관리
      this.cleanupOldCommands();
      
      return true;
    } catch (error) {
      console.error('Command execution failed:', error);
      // 사용자에게 에러 알림
      if (error instanceof Error) {
        if (toast) {
          toast({
            title: "작업 실패",
            description: error.message,
            variant: "destructive",
          });
        } else {
          alert(`작업 실패: ${error.message}`);
        }
      } else {
        if (toast) {
          toast({
            title: "작업 실패",
            description: "작업 중 오류가 발생했습니다.",
            variant: "destructive",
          });
        } else {
          alert('작업 중 오류가 발생했습니다.');
        }
      }
      return false;
    }
  }

  async undo(): Promise<boolean> {
    if (this.currentIndex < 0) {
      console.warn('No commands to undo');
      return false;
    }

    try {
      await this.commands[this.currentIndex].undo();
      this.currentIndex--;
      return true;
    } catch (error) {
      console.error('Undo failed:', error);
      return false;
    }
  }

  async redo(): Promise<boolean> {
    if (this.currentIndex >= this.commands.length - 1) {
      console.warn('No commands to redo');
      return false;
    }

    try {
      this.currentIndex++;
      await this.commands[this.currentIndex].execute();
      return true;
    } catch (error) {
      console.error('Redo failed:', error);
      return false;
    }
  }

  canUndo(): boolean {
    return this.currentIndex >= 0;
  }

  canRedo(): boolean {
    return this.currentIndex < this.commands.length - 1;
  }

  clearHistory(): void {
    this.commands = [];
    this.currentIndex = -1;
  }

  getHistoryInfo(): { total: number; current: number; canUndo: boolean; canRedo: boolean } {
    return {
      total: this.commands.length,
      current: this.currentIndex + 1,
      canUndo: this.canUndo(),
      canRedo: this.canRedo()
    };
  }

  private cleanupOldCommands(): void {
    if (this.commands.length > this.maxCommands) {
      const removeCount = this.commands.length - this.maxCommands;
      this.commands = this.commands.slice(removeCount);
      this.currentIndex = Math.max(-1, this.currentIndex - removeCount);
    }
  }
}

// useHistoryManager 훅
export function useHistoryManager() {
  const [historyManager] = useState(() => new HistoryManager());
  const [historyInfo, setHistoryInfo] = useState(historyManager.getHistoryInfo());
  const { toast } = useToast();

  const executeCommand = useCallback(async (command: Command): Promise<boolean> => {
    const success = await historyManager.executeCommand(command, toast);
    setHistoryInfo(historyManager.getHistoryInfo());
    return success;
  }, [historyManager, toast]);

  const undo = useCallback(async (): Promise<boolean> => {
    const success = await historyManager.undo();
    setHistoryInfo(historyManager.getHistoryInfo());
    return success;
  }, [historyManager]);

  const redo = useCallback(async (): Promise<boolean> => {
    const success = await historyManager.redo();
    setHistoryInfo(historyManager.getHistoryInfo());
    return success;
  }, [historyManager]);

  const clearHistory = useCallback((): void => {
    historyManager.clearHistory();
    setHistoryInfo(historyManager.getHistoryInfo());
  }, [historyManager]);

  return {
    executeCommand,
    undo,
    redo,
    clearHistory,
    canUndo: historyInfo.canUndo,
    canRedo: historyInfo.canRedo,
    historyInfo
  };
} 