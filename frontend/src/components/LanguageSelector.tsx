import React from 'react';
import { Select, HStack, Text } from '@chakra-ui/react';
import { useLanguage } from '../contexts/LanguageContext';

const LanguageSelector: React.FC = () => {
  const { language, setLanguage } = useLanguage();

  const languages = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'hi', name: 'हिंदी (Hindi)', flag: '🇮🇳' },
    { code: 'ta', name: 'தமிழ் (Tamil)', flag: '🇮🇳' },
    { code: 'te', name: 'తెలుగు (Telugu)', flag: '🇮🇳' },
    { code: 'bn', name: 'বাংলা (Bengali)', flag: '🇮🇳' },
    { code: 'mr', name: 'मराठी (Marathi)', flag: '🇮🇳' },
    { code: 'gu', name: 'ગુજરાતી (Gujarati)', flag: '🇮🇳' },
  ];

  return (
    <HStack spacing={1}>
      <Text fontSize="lg">🌐</Text>
      <Select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
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
