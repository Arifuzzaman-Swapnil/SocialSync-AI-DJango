import { useState, useCallback } from 'react';
import { strategyService } from '../services/strategyService';
import type { PromptHistoryEntry } from '../types';

export function usePromptHistory(brandId: number | null, feature: string) {
  const [history, setHistory] = useState<PromptHistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    if (!brandId) return;
    setLoading(true);
    try {
      const data = await strategyService.getPromptHistory(brandId, feature);
      setHistory(data.history || []);
    } catch {
      setHistory([]);
    }
    setLoading(false);
  }, [brandId, feature]);

  return { history, loading, load };
}

export default usePromptHistory;
