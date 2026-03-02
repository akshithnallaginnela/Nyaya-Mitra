import React from 'react';
import { Select } from '@chakra-ui/react';
import { useAuth } from '../contexts/AuthContext';
import api from '../api/axios';

const LanguageSelector: React.FC = () => {
  const { user } = useAuth();
  const [language, setLanguage] = React.useState(user?.preferred_language || 'en');

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'हिंदी (Hindi)' },
    { code: 'ta', name: 'தமிழ் (Tamil)' },
    { code: 'te', name: 'తెలుగు (Telugu)' },
    { code: 'bn', name: 'বাংলা (Bengali)' },
    { code: 'mr', name: 'मराठी (Marathi)' },
    { code: 'gu', name: 'ગુજરાતી (Gujarati)' },
  ];

  const handleLanguageChange = async (newLanguage: string) => {
    setLanguage(newLanguage);
    try {
      await api.post('/language/set', { language: newLanguage });
      // Reload page to apply language changes
      window.location.reload();
    } catch (error) {
      console.error('Failed to change language:', error);
    }
  };

  return (
    <Select
      value={language}
      onChange={(e) => handleLanguageChange(e.target.value)}
      width="200px"
      size="sm"
    >
      {languages.map((lang) => (
        <option key={lang.code} value={lang.code}>
          {lang.name}
        </option>
      ))}
    </Select>
  );
};

export default LanguageSelector;
