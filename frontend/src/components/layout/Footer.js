import React from 'react';
import { Box, Container, Typography, Link, Divider } from '@mui/material';
import { useTheme } from '@mui/material/styles';

const Footer = () => {
  const theme = useTheme();
  const currentYear = new Date().getFullYear();

  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: theme.palette.mode === 'light' 
          ? theme.palette.grey[100] 
          : theme.palette.grey[900],
      }}
    >
      <Container maxWidth="lg">
        <Divider sx={{ mb: 3 }} />
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Typography variant="body2" color="text.secondary">
            © {currentYear} Reflectly. All rights reserved.
          </Typography>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              mt: { xs: 2, sm: 0 },
            }}
          >
            <Link href="#" color="inherit" sx={{ mx: 1 }}>
              Privacy
            </Link>
            <Link href="#" color="inherit" sx={{ mx: 1 }}>
              Terms
            </Link>
            <Link href="#" color="inherit" sx={{ mx: 1 }}>
              Contact
            </Link>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;
