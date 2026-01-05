import { Popper, Box, Typography, Chip, IconButton, Paper, ClickAwayListener } from '@mui/material';
import React from 'react';
import { useDiffStore } from '../store/diffStore';
import CloseIcon from '@mui/icons-material/Close';

interface DiffPopoverProps {
  open: boolean;
  anchorEl: HTMLElement | null;
  diffIndex: number | null;
  onClose: () => void;
  isPinned: boolean;
  side?: 'a' | 'b';
  siblingRef?: React.RefObject<HTMLDivElement>;
}

const DiffPopover = ({ open, anchorEl, diffIndex, onClose, isPinned, side = 'a', siblingRef }: DiffPopoverProps) => {
  const { diffData } = useDiffStore();
  const popperRef = React.useRef<HTMLDivElement>(null);

  if (!diffData || diffIndex === null) return null;

  const diffItem = diffData.diff_items[diffIndex];
  if (!diffItem) return null;

  const getOperationColor = (op: string) => {
    const colors = {
      replace: 'warning',
      insert: 'success',
      delete: 'error',
    };
    return colors[op as keyof typeof colors] || 'default';
  };

  const handleClickAway = (event: MouseEvent | TouchEvent) => {
    if (!isPinned) return;
    
    const target = event.target as HTMLElement;
    
    // Check if click is inside ANY popper paper (this one or sibling)
    const clickedInsidePopper = target.closest('[data-popper-paper="true"]');
    if (clickedInsidePopper) {
      return;
    }
    
    // Click is outside all poppers, close them
    onClose();
  };

  return (
    <Popper
      open={open}
      anchorEl={anchorEl}
      placement={side === 'a' ? 'bottom-start' : 'bottom-end'}
      modifiers={[
        {
          name: 'offset',
          options: {
            offset: [0, 8],
          },
        },
      ]}
      sx={{
        zIndex: 1300,
      }}
    >
      <ClickAwayListener onClickAway={handleClickAway}>
        <Paper
          ref={popperRef}
          data-popper-paper="true"
          sx={{
            maxWidth: 500,
            p: 2,
            userSelect: 'text',
            pointerEvents: 'auto',
            boxShadow: 3,
          }}
        >
      <Box>
        <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
          <Chip
            label={diffItem.operation.toUpperCase()}
            color={getOperationColor(diffItem.operation) as any}
            size="small"
          />
          <Typography variant="caption" color="text.secondary">
            Page {diffItem.page_a || diffItem.page_b}
          </Typography>
          {isPinned && (
            <IconButton size="small" onClick={onClose} sx={{ ml: 'auto' }}>
              <CloseIcon fontSize="small" />
            </IconButton>
          )}
        </Box>

        {diffItem.text_a && (
          <Box sx={{ mb: 1 }}>
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'bold' }}>
              Original:
            </Typography>
            <Typography variant="body2" sx={{ bgcolor: '#ffebee', p: 1, borderRadius: 1, fontFamily: 'monospace', fontSize: '0.85rem', whiteSpace: 'pre-wrap' }}>
              {diffItem.text_a}
            </Typography>
          </Box>
        )}

        {diffItem.text_b && (
          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'bold' }}>
              Modified:
            </Typography>
            <Typography variant="body2" sx={{ bgcolor: '#e8f5e9', p: 1, borderRadius: 1, fontFamily: 'monospace', fontSize: '0.85rem', whiteSpace: 'pre-wrap' }}>
              {diffItem.text_b}
            </Typography>
          </Box>
        )}

        {diffItem.char_diffs && diffItem.char_diffs.length > 0 && (
          <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'bold' }}>
              Character-level diff:
            </Typography>
            <Box sx={{ mt: 1, fontFamily: 'monospace', fontSize: '0.85rem', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
              {diffItem.char_diffs.map((charDiff, idx) => {
                if (charDiff.operation === 'equal') {
                  return <span key={idx}>{charDiff.text_a}</span>;
                } else if (charDiff.operation === 'delete') {
                  return (
                    <span key={idx} style={{ backgroundColor: '#ffcdd2', textDecoration: 'line-through', color: '#c62828' }}>
                      {charDiff.text_a}
                    </span>
                  );
                } else if (charDiff.operation === 'insert') {
                  return (
                    <span key={idx} style={{ backgroundColor: '#c8e6c9', color: '#2e7d32', fontWeight: 'bold' }}>
                      {charDiff.text_b}
                    </span>
                  );
                } else if (charDiff.operation === 'replace') {
                  return (
                    <span key={idx}>
                      <span style={{ backgroundColor: '#ffcdd2', textDecoration: 'line-through', color: '#c62828' }}>
                        {charDiff.text_a}
                      </span>
                      <span style={{ backgroundColor: '#c8e6c9', color: '#2e7d32', fontWeight: 'bold' }}>
                        {charDiff.text_b}
                      </span>
                    </span>
                  );
                }
                return null;
              })}
            </Box>
          </Box>
        )}
      </Box>
        </Paper>
      </ClickAwayListener>
    </Popper>
  );
};

export default DiffPopover;
