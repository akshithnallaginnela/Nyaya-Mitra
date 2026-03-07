import React from 'react';
import {
  Box,
  Flex,
  Heading,
  Button,
  HStack,
  Spacer,
  IconButton,
  useDisclosure,
  Drawer,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  DrawerBody,
  VStack,
  Text,
  Divider,
  Show,
  Hide,
} from '@chakra-ui/react';
import { HamburgerIcon } from '@chakra-ui/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import LanguageSelector from './LanguageSelector';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, user } = useAuth();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { t } = useLanguage();

  const navLinks = [
    { label: t('welcome', 'Dashboard'), path: '/dashboard', icon: '🏠', tKey: 'dashboard' },
    { label: t('chat_title', 'Legal Chat'), path: '/chat', icon: '💬' },
    { label: t('case_analysis', 'Case Analyzer'), path: '/case-analyzer', icon: '🔍' },
    { label: t('document_generator', 'Documents'), path: '/documents', icon: '📄' },
    { label: t('legal_aid', 'Legal Aid'), path: '/legal-aid', icon: '⚖️' },
    { label: t('evidence_guide', 'Evidence Guide'), path: '/evidence', icon: '📋' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <Box
      bg="white"
      px={{ base: 4, md: 8 }}
      py={3}
      borderBottom="2px solid"
      borderColor="brand.500"
      position="sticky"
      top={0}
      zIndex={100}
      boxShadow="sm"
    >
      <Flex align="center">
        {/* Logo */}
        <HStack spacing={2} cursor="pointer" onClick={() => navigate('/dashboard')}>
          <Text fontSize="2xl">⚖️</Text>
          <Heading
            size="md"
            bgGradient="linear(to-r, brand.600, brand.400)"
            bgClip="text"
            fontWeight="800"
          >
            Nyaya Mitra
          </Heading>
        </HStack>

        <Spacer />

        {/* Desktop Nav Links */}
        {user && (
          <Show above="lg">
            <HStack spacing={1} mr={4}>
              {navLinks.map((link) => (
                <Button
                  key={link.path}
                  size="sm"
                  variant={isActive(link.path) ? 'solid' : 'ghost'}
                  colorScheme={isActive(link.path) ? 'brand' : 'gray'}
                  onClick={() => navigate(link.path)}
                  fontWeight={isActive(link.path) ? '700' : '500'}
                  leftIcon={<Text fontSize="sm">{link.icon}</Text>}
                  borderRadius="lg"
                >
                  {link.label}
                </Button>
              ))}
            </HStack>
          </Show>
        )}

        <HStack spacing={3}>
          {user && <LanguageSelector />}

          <Button
            size="sm"
            colorScheme="red"
            variant="solid"
            onClick={() => navigate('/emergency')}
            leftIcon={<Text>🚨</Text>}
            borderRadius="lg"
            fontWeight="700"
          >
            <Hide below="md">Emergency SOS</Hide>
            <Show below="md">SOS</Show>
          </Button>

          {user ? (
            <>
              <Hide below="lg">
                <Button
                  size="sm"
                  variant="outline"
                  colorScheme="gray"
                  onClick={handleLogout}
                  borderRadius="lg"
                >
                  {t('logout', 'Logout')}
                </Button>
              </Hide>

              {/* Mobile hamburger menu */}
              <Show below="lg">
                <IconButton
                  aria-label="Open menu"
                  icon={<HamburgerIcon />}
                  variant="outline"
                  onClick={onOpen}
                  size="sm"
                />
              </Show>
            </>
          ) : (
            <Button
              size="sm"
              colorScheme="brand"
              variant="outline"
              onClick={() => navigate('/login')}
              borderRadius="lg"
            >
              {t('login', 'Sign In')}
            </Button>
          )}
        </HStack>
      </Flex>

      {/* Mobile Drawer */}
      <Drawer isOpen={isOpen} placement="right" onClose={onClose}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerBody pt={12}>
            <VStack spacing={2} align="stretch">
              {navLinks.map((link) => (
                <Button
                  key={link.path}
                  variant={isActive(link.path) ? 'solid' : 'ghost'}
                  colorScheme={isActive(link.path) ? 'brand' : 'gray'}
                  justifyContent="flex-start"
                  onClick={() => {
                    navigate(link.path);
                    onClose();
                  }}
                  leftIcon={<Text>{link.icon}</Text>}
                  size="lg"
                >
                  {link.label}
                </Button>
              ))}
              <Divider my={2} />
              <Button
                variant="outline"
                colorScheme="red"
                onClick={handleLogout}
                size="lg"
              >
                {t('logout', 'Logout')}
              </Button>
            </VStack>
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </Box>
  );
};

export default Navbar;
