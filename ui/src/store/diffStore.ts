import { create } from 'zustand';
import type { DiffResult, DiffItem } from '../types/diff';

interface DiffStore {
  diffData: DiffResult | null;
  activeDiffIndex: number | null;
  isLoading: boolean;
  error: string | null;
  isPinned: boolean;
  isScrolling: boolean;
  
  setDiffData: (data: DiffResult) => void;
  setActiveDiffIndex: (index: number | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setIsPinned: (pinned: boolean) => void;
  setIsScrolling: (scrolling: boolean) => void;
  getActiveDiffItem: () => DiffItem | null;
}

export const useDiffStore = create<DiffStore>((set, get) => ({
  diffData: null,
  activeDiffIndex: null,
  isLoading: false,
  error: null,
  isPinned: false,
  isScrolling: false,
  
  setDiffData: (data) => set({ diffData: data }),
  setActiveDiffIndex: (index) => set({ activeDiffIndex: index }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setIsPinned: (pinned) => set({ isPinned: pinned }),
  setIsScrolling: (scrolling) => set({ isScrolling: scrolling }),
  
  getActiveDiffItem: () => {
    const { diffData, activeDiffIndex } = get();
    if (!diffData || activeDiffIndex === null) return null;
    return diffData.diff_items[activeDiffIndex] || null;
  },
}));
