import { useEffect, useRef } from 'react';
import { ThemeProvider, createTheme, CssBaseline, Container, Box, Typography, CircularProgress, Alert } from '@mui/material';
import { useDiffStore } from './store/diffStore';
import PDFCompareView from './components/PDFCompareView';
import type { PDFCompareViewHandle } from './components/PDFCompareView';
import DiffList from './components/DiffList';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      dark: '#115293',
      light: '#42a5f5',
    },
  },
});

function App() {
  const { diffData, isLoading, error, setDiffData, setLoading, setError, setActiveDiffIndex, setIsPinned, setIsScrolling } = useDiffStore();
  const pdfCompareRef = useRef<PDFCompareViewHandle>(null);

  useEffect(() => {
    const loadAssets = async () => {
      setLoading(true);
      setError(null);

      try {
        // Check environment variables
        const pdfAPath = import.meta.env.VITE_PDF_A_PATH;
        const pdfBPath = import.meta.env.VITE_PDF_B_PATH;
        const diffJsonPath = import.meta.env.VITE_DIFF_JSON_PATH;

        if (!pdfAPath || !pdfBPath || !diffJsonPath) {
          throw new Error(
            'Missing environment variables. Please set VITE_PDF_A_PATH, VITE_PDF_B_PATH, and VITE_DIFF_JSON_PATH in .env file'
          );
        }

        // Load diff JSON
        const response = await fetch(diffJsonPath);
        if (!response.ok) {
          throw new Error(`Failed to load diff JSON from ${diffJsonPath}: ${response.statusText}`);
        }

        const data = await response.json();
        setDiffData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error loading assets');
      } finally {
        setLoading(false);
      }
    };

    loadAssets();
  }, [setDiffData, setLoading, setError]);

  if (isLoading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Container>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', gap: 2 }}>
            <CircularProgress />
            <Typography>Loading PDFs and diff data...</Typography>
          </Box>
        </Container>
      </ThemeProvider>
    );
  }

  if (error) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Container>
          <Box sx={{ mt: 4 }}>
            <Alert severity="error">
              <Typography variant="h6" gutterBottom>Error Loading Assets</Typography>
              <Typography>{error}</Typography>
              <Typography variant="body2" sx={{ mt: 2 }}>
                Please check:
                <ul>
                  <li>Environment variables are set in .env file</li>
                  <li>PDF files exist in public/pdfs/ directory</li>
                  <li>Diff JSON exists in public/diffs/ directory</li>
                </ul>
              </Typography>
            </Alert>
          </Box>
        </Container>
      </ThemeProvider>
    );
  }

  if (!diffData) {
    return null;
  }

  const handleDiffClick = (diffIndex: number, pageA: number, pageB: number) => {
    // Set scrolling state to prevent popover from showing during scroll
    setIsScrolling(true);
    setActiveDiffIndex(diffIndex);
    
    // Scroll to page
    pdfCompareRef.current?.scrollToPage(pageA, pageB);
    
    // After scroll completes, show pinned popover
    setTimeout(() => {
      setIsScrolling(false);
      setIsPinned(true);
    }, 700);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ width: '100%', height: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ 
          p: 2, 
          bgcolor: 'primary.main',
          color: 'white',
          boxShadow: 2,
          display: 'flex',
          alignItems: 'center',
          gap: 2
        }}>
          <Box
            component="img"
            src="/icon.svg"
            alt="Logo"
            sx={{ 
              height: 40, 
              width: 40,
              filter: 'brightness(0) invert(1)' // Makes icon white
            }}
          />
          <Box>
            <Typography variant="h5" fontWeight="bold">PDF Comparison Tool</Typography>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              {diffData.total_differences} differences found
            </Typography>
          </Box>
        </Box>
        <Box sx={{ flex: 1, overflow: 'hidden', width: '100%', display: 'flex' }}>
          <Box sx={{ flex: 1, overflow: 'hidden' }}>
            <PDFCompareView ref={pdfCompareRef} />
          </Box>
          <Box sx={{ width: 400, borderLeft: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
            <DiffList onDiffClick={handleDiffClick} />
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
