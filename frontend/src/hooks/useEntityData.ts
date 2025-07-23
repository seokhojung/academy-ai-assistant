import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../lib/api-client';

// 스마트 캐싱 전략
export const useEntityData = (entityType: string) => {
  const queryClient = useQueryClient();

  // 데이터 조회 (캐시 우선)
  const query = useQuery({
    queryKey: [entityType],
    queryFn: () => apiClient.getEntities(entityType),
    staleTime: 5 * 60 * 1000, // 5분 신선도
    gcTime: 30 * 60 * 1000, // 30분 가비지 컬렉션 시간
    refetchOnWindowFocus: false,
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  // 낙관적 업데이트 뮤테이션
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => 
      apiClient.updateEntity(entityType, id, data),
    
    // 낙관적 업데이트
    onMutate: async ({ id, data }) => {
      // 진행 중인 쿼리 취소
      await queryClient.cancelQueries({ queryKey: [entityType] });
      
      // 이전 데이터 백업
      const previousData = queryClient.getQueryData([entityType]);
      
      // 낙관적 업데이트
      queryClient.setQueryData([entityType], (old: any[]) => 
        old?.map(item => item.id === id ? { ...item, ...data } : item)
      );
      
      return { previousData };
    },
    
    // 에러 시 롤백
    onError: (err, variables, context) => {
      if (context?.previousData) {
        queryClient.setQueryData([entityType], context.previousData);
      }
    },
    
    // 완료 시 캐시 무효화
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: [entityType] });
    },
  });

  // 생성 뮤테이션
  const createMutation = useMutation({
    mutationFn: (data: any) => apiClient.createEntity(entityType, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [entityType] });
    },
  });

  // 삭제 뮤테이션
  const deleteMutation = useMutation({
    mutationFn: (id: number) => apiClient.deleteEntity(entityType, id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: [entityType] });
      const previousData = queryClient.getQueryData([entityType]);
      
      queryClient.setQueryData([entityType], (old: any[]) => 
        old?.filter(item => item.id !== id)
      );
      
      return { previousData };
    },
    onError: (err, variables, context) => {
      if (context?.previousData) {
        queryClient.setQueryData([entityType], context.previousData);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: [entityType] });
    },
  });

  return {
    data: query.data || [],
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
    
    // 뮤테이션 액션들
    updateEntity: updateMutation.mutate,
    createEntity: createMutation.mutate,
    deleteEntity: deleteMutation.mutate,
    
    // 뮤테이션 상태들
    isUpdating: updateMutation.isPending,
    isCreating: createMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
};

// 오프라인 지원 훅 (간소화)
export const useOfflineSync = () => {
  const queryClient = useQueryClient();

  const syncPendingChanges = async () => {
    try {
      // 모든 쿼리 다시 가져오기
      await queryClient.refetchQueries();
      console.log('오프라인 동기화 완료');
    } catch (error) {
      console.error('동기화 실패:', error);
    }
  };

  return { syncPendingChanges };
};

// 배치 처리 훅
export const useBatchOperations = (entityType: string) => {
  const queryClient = useQueryClient();

  const batchUpdate = useMutation({
    mutationFn: async (operations: Array<{ id: number; data: any }>) => {
      const results = await Promise.allSettled(
        operations.map(op => apiClient.updateEntity(entityType, op.id, op.data))
      );
      return results;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [entityType] });
    },
  });

  const batchDelete = useMutation({
    mutationFn: async (ids: number[]) => {
      const results = await Promise.allSettled(
        ids.map(id => apiClient.deleteEntity(entityType, id))
      );
      return results;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [entityType] });
    },
  });

  return {
    batchUpdate: batchUpdate.mutate,
    batchDelete: batchDelete.mutate,
    isBatchUpdating: batchUpdate.isPending,
    isBatchDeleting: batchDelete.isPending,
  };
}; 