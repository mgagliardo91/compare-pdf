export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface CharDiff {
  operation: 'equal' | 'delete' | 'insert' | 'replace';
  text_a: string | null;
  text_b: string | null;
  start_a: number;
  end_a: number;
  start_b: number;
  end_b: number;
}

export interface DiffItem {
  operation: 'replace' | 'insert' | 'delete' | 'equal';
  page_a: number | null;
  page_b: number | null;
  text_a: string | null;
  text_b: string | null;
  bounding_boxes_a: BoundingBox[];
  bounding_boxes_b: BoundingBox[];
  unified_diff?: string;
  char_diffs?: CharDiff[];
}

export interface DiffResult {
  pdf_a_path: string;
  pdf_b_path: string;
  total_pages_a: number;
  total_pages_b: number;
  total_differences: number;
  diff_items: DiffItem[];
}
