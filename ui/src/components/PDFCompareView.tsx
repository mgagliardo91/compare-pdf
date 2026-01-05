import { Box, Typography, Paper } from '@mui/material';
import { Document, Page, pdfjs } from 'react-pdf';
import { useState, useRef, useImperativeHandle, forwardRef } from 'react';
import { useDiffStore } from '../store/diffStore';
import DiffOverlay from './DiffOverlay';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// Configure PDF.js worker - use the CDN with the correct URL
pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

export interface PDFCompareViewHandle {
  scrollToPage: (pageA: number, pageB: number, onComplete?: () => void) => void;
}

const PDFCompareView = forwardRef<PDFCompareViewHandle>((props, ref) => {
  const { diffData } = useDiffStore();
  const [numPagesA, setNumPagesA] = useState<number>(0);
  const [numPagesB, setNumPagesB] = useState<number>(0);
  const [pageWidth, setPageWidth] = useState<number>(0);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const pageRefsA = useRef<Map<number, HTMLDivElement>>(new Map());
  const pageRefsB = useRef<Map<number, HTMLDivElement>>(new Map());

  useImperativeHandle(ref, () => ({
    scrollToPage: (pageA: number, pageB: number, onComplete?: () => void) => {
      const pageElementA = pageRefsA.current.get(pageA);
      
      if (pageElementA && scrollContainerRef.current) {
        const targetTop = pageElementA.offsetTop - 20;
        const startTop = scrollContainerRef.current.scrollTop;
        const distance = Math.abs(targetTop - startTop);
        
        // Estimate scroll duration based on distance (smooth scroll is ~500ms for typical distances)
        const duration = Math.min(500, Math.max(200, distance * 0.3));
        
        scrollContainerRef.current.scrollTo({
          top: targetTop,
          behavior: 'smooth'
        });
        
        // Call onComplete after scroll duration
        if (onComplete) {
          setTimeout(onComplete, duration + 100); // Add 100ms buffer
        }
      } else if (onComplete) {
        // If no scroll needed, call immediately
        onComplete();
      }
    }
  }));

  if (!diffData) return null;

  // Get full URLs for PDFs
  const pdfAPath = import.meta.env.VITE_PDF_A_PATH;
  const pdfBPath = import.meta.env.VITE_PDF_B_PATH;

  const handleLoadSuccessA = ({ numPages }: { numPages: number }) => {
    setNumPagesA(numPages);
  };

  const handleLoadSuccessB = ({ numPages }: { numPages: number }) => {
    setNumPagesB(numPages);
  };

  const handlePageLoadSuccess = (page: any) => {
    if (!pageWidth) {
      // Store the original PDF page width (in PDF points, not pixels)
      // This will be used to calculate scale factor
      console.log('PDF page dimensions:', page.width, 'x', page.height, 'points');
      setPageWidth(page.width);
    }
  };

  const handleLoadError = (error: Error) => {
    console.error('PDF Load Error:', error);
  };

  return (
    <Box sx={{ display: 'flex', height: '100%', width: '100%', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ width: '50%', p: 2, bgcolor: 'grey.50' }}>
          <Typography variant="subtitle2">PDF A - {diffData.pdf_a_path}</Typography>
        </Box>
        <Box sx={{ width: '50%', p: 2, bgcolor: 'grey.50' }}>
          <Typography variant="subtitle2">PDF B - {diffData.pdf_b_path}</Typography>
        </Box>
      </Box>
      <Box 
        ref={scrollContainerRef}
        sx={{ 
          flex: 1, 
          overflow: 'auto'
        }}
      >
        <Box sx={{ display: 'flex', minHeight: '100%', minWidth: 1200 }}>
        <Box sx={{ width: '50%', position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', bgcolor: 'grey.100' }}>
          <Document
            file={pdfAPath}
            onLoadSuccess={handleLoadSuccessA}
            error={<Paper sx={{ p: 2, m: 2 }}><Typography color="error">Failed to load PDF A</Typography></Paper>}
          >
              {Array.from(new Array(numPagesA), (_, index) => (
                <Box 
                  key={`page_a_${index + 1}`} 
                  ref={(el) => {
                    if (el) pageRefsA.current.set(index + 1, el);
                  }}
                  sx={{ 
                    position: 'relative', 
                    mb: 3,
                    pb: 2,
                    borderBottom: index < numPagesA - 1 ? 2 : 0,
                    borderColor: 'divider',
                    boxShadow: index < numPagesA - 1 ? '0 4px 6px rgba(0,0,0,0.1)' : 'none'
                  }}
                >
                <Page
                  pageNumber={index + 1}
                  width={600}
                  onLoadSuccess={handlePageLoadSuccess}
                  renderTextLayer={true}
                  renderAnnotationLayer={false}
                />
                  <DiffOverlay
                    pageNumber={index + 1}
                    side="a"
                    renderedWidth={600}
                    rasterWidth={2550}
                  />
                </Box>
              ))}
            </Document>
          </Box>
          {/* Vertical divider */}
          <Box sx={{ 
            width: 0,
            borderLeft: 1,
            borderColor: 'divider'
          }} />
        <Box sx={{ width: '50%', position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', bgcolor: 'grey.100' }}>
          <Document
            file={pdfBPath}
            onLoadSuccess={handleLoadSuccessB}
            error={<Paper sx={{ p: 2, m: 2 }}><Typography color="error">Failed to load PDF B</Typography></Paper>}
          >
            {Array.from(new Array(numPagesB), (_, index) => (
              <Box 
                key={`page_b_${index + 1}`}
                ref={(el) => {
                  if (el) pageRefsB.current.set(index + 1, el);
                }}
                sx={{ 
                  position: 'relative', 
                  mb: 3,
                  pb: 2,
                  borderBottom: index < numPagesB - 1 ? 2 : 0,
                  borderColor: 'divider',
                  boxShadow: index < numPagesB - 1 ? '0 4px 6px rgba(0,0,0,0.1)' : 'none'
                }}
              >
                <Page
                  pageNumber={index + 1}
                  width={600}
                  renderTextLayer={true}
                  renderAnnotationLayer={false}
                />
                <DiffOverlay
                  pageNumber={index + 1}
                  side="b"
                  renderedWidth={600}
                  rasterWidth={2550}
                />
              </Box>
            ))}
          </Document>
        </Box>
        </Box>
      </Box>
    </Box>
  );
});

PDFCompareView.displayName = 'PDFCompareView';

export default PDFCompareView;
