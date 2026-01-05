import { Box, IconButton } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import { useDiffStore } from '../store/diffStore';
import { useState, useRef, useEffect } from 'react';
import React from 'react';
import DiffPopover from './DiffPopover';

interface DiffOverlayProps {
  pageNumber: number;
  side: 'a' | 'b';
  renderedWidth: number;
  rasterWidth: number;
}

const DiffOverlay = ({ pageNumber, side, renderedWidth, rasterWidth }: DiffOverlayProps) => {
  const { diffData, activeDiffIndex, setActiveDiffIndex, isPinned, setIsPinned, isScrolling } = useDiffStore();
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [hoveredDiffIndex, setHoveredDiffIndex] = useState<number | null>(null);
  const [hoverTimeout, setHoverTimeout] = useState<NodeJS.Timeout | null>(null);
  const boxRefs = useRef<Map<number, HTMLElement>>(new Map());

  // Coordinate cross-pane display: when activeDiffIndex changes, set anchor from refs if we have that diff
  // This enables showing popovers on both panes for replace operations (both hover and pinned)
  useEffect(() => {
    if (activeDiffIndex !== null && boxRefs.current.has(activeDiffIndex)) {
      const element = boxRefs.current.get(activeDiffIndex);
      if (element) {
        // Check if this is a replace operation by looking at the diff item
        const diffItem = diffData?.diff_items[activeDiffIndex];
        // Show on both panes for replace operations (hover or pinned)
        // Show on the relevant pane for delete/insert operations when pinned
        if (diffItem?.operation === 'replace' || isPinned) {
          setAnchorEl(element);
          setHoveredDiffIndex(activeDiffIndex);
        }
      }
    } else if (activeDiffIndex === null) {
      // Clear when no diff is active
      setAnchorEl(null);
      setHoveredDiffIndex(null);
    }
  }, [activeDiffIndex, isPinned, diffData]);

  // Close popovers on window resize to prevent misalignment
  useEffect(() => {
    const handleResize = () => {
      if (isPinned) {
        handleClose();
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [isPinned]);

  if (!diffData) return null;

  // Calculate scale factor for coordinate transformation
  // OCR was done at 300 DPI (2550px for 8.5" page)
  // We're rendering at 600px width
  const scaleFactor = renderedWidth / 2550;  // Always use 2550 as OCR raster width

  // Filter diffs for this page and side
  const pageDiffs = diffData.diff_items
    .map((item, index) => ({ item, index }))
    .filter(({ item }) => {
      if (side === 'a') {
        return item.page_a === pageNumber && item.bounding_boxes_a.length > 0;
      } else {
        return item.page_b === pageNumber && item.bounding_boxes_b.length > 0;
      }
    });

  const getColor = (operation: string, isActive: boolean) => {
    const colors = {
      replace: isActive ? '#ff9800' : '#ff980080',
      insert: isActive ? '#4caf50' : '#4caf5080',
      delete: isActive ? '#f44336' : '#f4433680',
    };
    return colors[operation as keyof typeof colors] || '#999';
  };

  const handleIconHover = (diffIndex: number, boxElement: HTMLElement) => {
    if (isPinned) return;
    
    setActiveDiffIndex(diffIndex);
    setHoveredDiffIndex(diffIndex);
    setAnchorEl(boxElement);
  };

  const handleIconLeave = () => {
    if (isPinned) return;
    
    setActiveDiffIndex(null);
    setHoveredDiffIndex(null);
    setAnchorEl(null);
  };

  const handleIconClick = (event: React.MouseEvent<HTMLButtonElement>, diffIndex: number, boxElement: HTMLElement) => {
    event.stopPropagation();
    
    if (isPinned && activeDiffIndex === diffIndex) {
      // If already pinned on this diff, unpin
      handleClose();
    } else {
      // Pin this diff
      setIsPinned(true);
      setActiveDiffIndex(diffIndex);
      setHoveredDiffIndex(diffIndex);
      setAnchorEl(boxElement);
    }
  };

  const handleClose = () => {
    // Unpin and close (global state affects both panes)
    setIsPinned(false);
    setActiveDiffIndex(null);
    setHoveredDiffIndex(null);
    setAnchorEl(null);
  };

  return (
    <>
      {pageDiffs.map(({ item, index }) => {
        const bboxes = side === 'a' ? item.bounding_boxes_a : item.bounding_boxes_b;
        const isActive = activeDiffIndex === index;

        return bboxes.map((bbox, bboxIndex) => {
          const x = bbox.x * scaleFactor;
          const y = bbox.y * scaleFactor;
          const width = bbox.width * scaleFactor;
          const height = bbox.height * scaleFactor;

          return (
            <React.Fragment key={`diff_${index}_bbox_${bboxIndex}`}>
              <Box
                ref={(el) => {
                  if (el && bboxIndex === 0) {
                    // Store reference to first bbox of each diff item
                    boxRefs.current.set(index, el);
                  }
                }}
                sx={{
                  position: 'absolute',
                  left: x,
                  top: y,
                  width,
                  height,
                  border: 2,
                  borderColor: getColor(item.operation, isActive),
                  backgroundColor: isActive ? `${getColor(item.operation, true)}20` : 'transparent',
                  pointerEvents: 'none',
                  zIndex: isActive ? 10 : 1,
                  transition: 'all 0.2s',
                }}
              />
              {bboxIndex === 0 && (
                <IconButton
                  size="small"
                  onMouseEnter={() => {
                    const boxEl = boxRefs.current.get(index);
                    if (boxEl) handleIconHover(index, boxEl);
                  }}
                  onMouseLeave={handleIconLeave}
                  onClick={(e) => {
                    const boxEl = boxRefs.current.get(index);
                    if (boxEl) handleIconClick(e, index, boxEl);
                  }}
                  sx={{
                    position: 'absolute',
                    left: x + width + 4,
                    top: y + (height / 2) - 12,
                    width: 20,
                    height: 20,
                    padding: 0,
                    zIndex: isActive ? 11 : 2,
                  }}
                >
                  <InfoIcon sx={{ fontSize: 20, color: getColor(item.operation, isActive) }} />
                </IconButton>
              )}
            </React.Fragment>
          );
        });
      })}

      <DiffPopover
        open={Boolean(anchorEl) && hoveredDiffIndex !== null && !isScrolling}
        anchorEl={anchorEl}
        diffIndex={hoveredDiffIndex}
        onClose={handleClose}
        isPinned={isPinned}
      />
    </>
  );
};

export default DiffOverlay;
