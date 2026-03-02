import React from 'react';
import { Box, Flex, Heading, Button, HStack, Spacer } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LanguageSelector from './LanguageSelector';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const { logout, user } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Box bg="blue.600" px={8} py={4} color="white">
      <Flex align="center">
        <Heading size="md" cursor="pointer" onClick={() => navigate('/dashboard')}>
          Nyaya Mitra
        </Heading>
        <Spacer />
        <HStack spacing={4}>
          {user && <LanguageSelector />}
          <Button
            size="sm"
            colorScheme="red"
            variant="solid"
            onClick={() => navigate('/emergency')}
          >
            Emergency SOS
          </Button>
          {user && (
            <Button size="sm" variant="outline" onClick={handleLogout}>
              Logout
            </Button>
          )}
        </HStack>
      </Flex>
    </Box>
  );
};

export default Navbar;
