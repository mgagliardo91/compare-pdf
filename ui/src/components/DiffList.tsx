import { Box, List, ListItem, ListItemButton, ListItemText, Typography, Chip } from '@mui/material';
import PushPinIcon from '@mui/icons-material/PushPin';
import { useDiffStore } from '../store/diffStore';
import type { DiffItem } from '../types/diff';

interface DiffListProps {
  onDiffClick: (diffIndex: number, pageA: number, pageB: number) => void;
}

const DiffList = ({ onDiffClick }: DiffListProps) => {
  const { diffData, activeDiffIndex, isPinned } = useDiffStore();

  if (!diffData) return null;

  const getOperationColor = (operation: string) => {
    switch (operation) {
      case 'replace':
        return 'warning';
      case 'insert':
        return 'success';
      case 'delete':
        return 'error';
      default:
        return 'default';
    }
  };

  const getOperationLabel = (operation: string) => {
    return operation.charAt(0).toUpperCase() + operation.slice(1);
  };

  const renderCharDiffPreview = (item: DiffItem) => {
    if (!item.char_diffs || item.char_diffs.length === 0) {
      // Fallback to text blocks if no char diffs
      const text = item.text_a || item.text_b || '';
      const maxLength = 60;
      if (text.length <= maxLength) return <span>{text}</span>;
      return <span>{text.substring(0, maxLength) + '...'}</span>;
    }

    // Find the first non-equal char diff (the actual change)
    const firstChange = item.char_diffs.find(d => d.operation !== 'equal');
    if (!firstChange) {
      // All equal? Just show beginning
      const text = item.text_a || item.text_b || '';
      const maxLength = 60;
      if (text.length <= maxLength) return <span>{text}</span>;
      return <span>{text.substring(0, maxLength) + '...'}</span>;
    }

    // Get context before, the change, and context after
    const changeIndex = item.char_diffs.indexOf(firstChange);
    const contextBefore = 15; // chars of context
    const contextAfter = 15;

    const parts: JSX.Element[] = [];
    
    // Add context before (only if there are items before the change)
    if (changeIndex > 0) {
      let beforeText = '';
      let beforeLength = 0;
      for (let i = changeIndex - 1; i >= 0 && beforeLength < contextBefore; i--) {
        const diff = item.char_diffs[i];
        const text = diff.text_a || diff.text_b || '';
        if (beforeLength + text.length <= contextBefore) {
          beforeText = text + beforeText;
          beforeLength += text.length;
        } else {
          beforeText = '...' + text.substring(text.length - (contextBefore - beforeLength)) + beforeText;
          break;
        }
      }
      if (beforeText) parts.push(<span key="before">{beforeText}</span>);
    }

    // Add the changes with highlighting
    let afterLength = 0;
    for (let i = changeIndex; i < item.char_diffs.length && afterLength < contextAfter; i++) {
      const diff = item.char_diffs[i];
      const text = diff.text_a || diff.text_b || '';
      const displayText = afterLength + text.length <= contextAfter 
        ? text 
        : text.substring(0, contextAfter - afterLength) + '...';
      
      if (diff.operation === 'delete') {
        parts.push(
          <span key={`diff-${i}`} style={{ color: '#d32f2f', textDecoration: 'line-through' }}>
            {displayText}
          </span>
        );
      } else if (diff.operation === 'insert') {
        parts.push(
          <span key={`diff-${i}`} style={{ color: '#388e3c', fontWeight: 'bold' }}>
            {displayText}
          </span>
        );
      } else if (diff.operation === 'replace') {
        parts.push(
          <span key={`diff-${i}-del`} style={{ color: '#d32f2f', textDecoration: 'line-through' }}>
            {diff.text_a}
          </span>
        );
        parts.push(
          <span key={`diff-${i}-ins`} style={{ color: '#388e3c', fontWeight: 'bold' }}>
            {diff.text_b}
          </span>
        );
      } else {
        parts.push(<span key={`diff-${i}`}>{displayText}</span>);
      }
      
      afterLength += text.length;
      if (afterLength >= contextAfter) break;
    }

    return <>{parts}</>;
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, bgcolor: 'grey.50', borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6">Differences ({diffData.total_differences})</Typography>
        <Typography variant="caption" color="text.secondary">
          Click to navigate
        </Typography>
      </Box>
      <List sx={{ flex: 1, overflow: 'auto', p: 0 }}>
        {diffData.diff_items.map((item, index) => {
          const isActive = activeDiffIndex === index;
          const isPinnedItem = isActive && isPinned;
          const prevItem = index > 0 ? diffData.diff_items[index - 1] : null;
          const showPageSeparator = !prevItem || prevItem.page_a !== item.page_a;
          
          return (
            <Box key={index}>
              {showPageSeparator && (
                <Box sx={{ 
                  py: 1, 
                  px: 2, 
                  bgcolor: 'grey.100',
                  borderBottom: 1,
                  borderColor: 'divider'
                }}>
                  <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 500 }}>
                    Page {item.page_a}
                  </Typography>
                </Box>
              )}
              <ListItem 
                disablePadding
                sx={{ 
                  borderBottom: 1, 
                  borderColor: 'divider',
                  bgcolor: isActive ? 'action.selected' : 'transparent'
                }}
              >
                <ListItemButton 
                  onClick={() => onDiffClick(index, item.page_a, item.page_b)}
                  sx={{ py: 1.5, px: 2, position: 'relative' }}
                >
                {isPinnedItem && (
                  <PushPinIcon 
                    sx={{ 
                      position: 'absolute',
                      top: 8,
                      right: 8,
                      fontSize: 16,
                      color: 'primary.main',
                      transform: 'rotate(45deg)'
                    }} 
                  />
                )}
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5, pr: 3 }}>
                      <Typography variant="caption" color="text.secondary">
                        Page {item.page_a} → {item.page_b}
                      </Typography>
                      <Chip 
                        label={getOperationLabel(item.operation)}
                        color={getOperationColor(item.operation)}
                        size="small"
                      />
                    </Box>
                  }
                  secondary={
                    <Box sx={{ mt: 0.5, pr: 3 }}>
                      <Typography variant="body2" component="div" sx={{ fontStyle: 'italic' }}>
                        {renderCharDiffPreview(item)}
                      </Typography>
                    </Box>
                  }
                />
              </ListItemButton>
            </ListItem>
          </Box>
          );
        })}
      </List>
    </Box>
  );
};

export default DiffList;
