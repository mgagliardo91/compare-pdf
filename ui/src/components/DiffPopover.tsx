import { Popover, Box, Typography, Chip, IconButton } from '@mui/material';
import { useDiffStore } from '../store/diffStore';
import CloseIcon from '@mui/icons-material/Close';

interface DiffPopoverProps {
  open: boolean;
  anchorEl: HTMLElement | null;
  diffIndex: number | null;
  onClose: () => void;
  isPinned: boolean;
}

const DiffPopover = ({ open, anchorEl, diffIndex, onClose, isPinned }: DiffPopoverProps) => {
  const { diffData } = useDiffStore();

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

  return (
    <Popover
      open={open}
      anchorEl={anchorEl}
      onClose={onClose}
      anchorOrigin={{
        vertical: 'bottom',
        horizontal: 'left',
      }}
      transformOrigin={{
        vertical: 'top',
        horizontal: 'left',
      }}
      disableRestoreFocus
      sx={{
        pointerEvents: isPinned ? 'auto' : 'none',
      }}
      slotProps={{
        paper: {
          sx: {
            pointerEvents: isPinned ? 'auto' : 'none',
            maxWidth: 500,
            p: 2,
            mt: 1,
          },
        },
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
    </Popover>
  );
};

export default DiffPopover;
