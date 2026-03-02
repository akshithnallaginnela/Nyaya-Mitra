import React from 'react';
import { Select, HStack, Text } from '@chakra-ui/react';
import { useAuth } from '../contexts/AuthContext';
import api from '../api/axios';

const LanguageSelector: React.FC = () => {
  const { user } = useAuth();
  const [language, setLanguage] = React.useState(user?.preferred_language || 'en');

  const languages = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'hi', name: 'हिंदी (Hindi)', flag: '🇮🇳' },
    { code: 'ta', name: 'தமிழ் (Tamil)', flag: '🇮🇳' },
    { code: 'te', name: 'తెలుగు (Telugu)', flag: '🇮🇳' },
    { code: 'bn', name: 'বাংলা (Bengali)', flag: '🇮🇳' },
    { code: 'mr', name: 'मराठी (Marathi)', flag: '🇮🇳' },
    { code: 'gu', name: 'ગુજરાતી (Gujarati)', flag: '🇮🇳' },
  ];

  const handleLanguageChange = async (newLanguage: string) => {
    setLanguage(newLanguage);
    try {
      await api.post('/language/set', { language: newLanguage });
      window.location.reload();
    } catch (error) {
      console.error('Failed to change language:', error);
    }
  };

  return (
    <HStack spacing={1}>
      <Text fontSize="lg">🌐</Text>
      <Select
        value={language}
        onChange={(e) => handleLanguageChange(e.target.value)}
        width="160px"
        size="sm"
        bg="white"
        color="gray.800"
        borderColor="gray.300"
        borderRadius="lg"
        fontWeight="500"
        _hover={{ borderColor: 'brand.400' }}
        _focus={{ borderColor: 'brand.500', boxShadow: '0 0 0 1px var(--chakra-colors-brand-500)' }}
        sx={{
          '& option': {
            color: 'gray.800',
            bg: 'white',
          },
        }}
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </Select>
    </HStack>
  );
};

export default LanguageSelector;
