import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../api/axios';

// Translation keys type — matches the backend translation JSON structure
export interface Translations {
  [key: string]: string;
}

interface LanguageContextType {
  language: string;
  translations: Translations;
  setLanguage: (lang: string) => void;
  t: (key: string, fallback?: string) => string;
  loading: boolean;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Default English translations (fallback if backend is unavailable)
const defaultTranslations: Translations = {
  app_name: 'Nyaya Mitra',
  welcome: 'Welcome to Nyaya Mitra',
  login: 'Login',
  register: 'Register',
  logout: 'Logout',
  email: 'Email',
  password: 'Password',
  full_name: 'Full Name',
  college_name: 'College Name',
  submit: 'Submit',
  cancel: 'Cancel',
  save: 'Save',
  delete: 'Delete',
  edit: 'Edit',
  back: 'Back',
  next: 'Next',
  previous: 'Previous',
  search: 'Search',
  filter: 'Filter',
  clear: 'Clear',
  loading: 'Loading...',
  error: 'Error',
  success: 'Success',
  chat_title: 'Legal Chat Assistant',
  chat_placeholder: 'Ask your legal question...',
  send_message: 'Send',
  new_conversation: 'New Conversation',
  conversation_history: 'Conversation History',
  case_analysis: 'Case Analysis',
  validity_score: 'Validity Score',
  evidence_strength: 'Evidence Strength',
  legal_basis: 'Legal Basis',
  procedural_compliance: 'Procedural Compliance',
  timeline_analysis: 'Timeline Analysis',
  weaknesses: 'Weaknesses',
  recommendations: 'Recommendations',
  document_generator: 'Document Generator',
  select_template: 'Select Template',
  legal_letter: 'Legal Letter',
  rti_application: 'RTI Application',
  counter_petition: 'Counter Petition',
  generate_document: 'Generate Document',
  download_pdf: 'Download PDF',
  download_text: 'Download Text',
  legal_aid: 'Legal Aid',
  find_legal_aid: 'Find Legal Aid',
  location: 'Location',
  specialization: 'Specialization',
  contact_info: 'Contact Information',
  phone: 'Phone',
  address: 'Address',
  emergency: 'Emergency',
  emergency_contacts: 'Emergency Contacts',
  police: 'Police',
  legal_helpline: 'Legal Helpline',
  mental_health: 'Mental Health Support',
  student_services: 'Student Services',
  evidence_guide: 'Evidence Guide',
  collect_evidence: 'Collect Evidence',
  digital_evidence: 'Digital Evidence',
  physical_evidence: 'Physical Evidence',
  settings: 'Settings',
  language: 'Language',
  change_language: 'Change Language',
  profile: 'Profile',
  account: 'Account',
};

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<string>(
    () => localStorage.getItem('preferred_language') || 'en'
  );
  const [translations, setTranslations] = useState<Translations>(defaultTranslations);
  const [loading, setLoading] = useState(false);

  const fetchTranslations = useCallback(async (lang: string) => {
    setLoading(true);
    try {
      const response = await api.get(`/language/translations/${lang}`);
      if (response.data && response.data.translations) {
        setTranslations(response.data.translations);
      }
    } catch (error) {
      console.error('Failed to fetch translations:', error);
      // Keep default/current translations on error
      if (lang === 'en') {
        setTranslations(defaultTranslations);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch translations when language changes
  useEffect(() => {
    fetchTranslations(language);
  }, [language, fetchTranslations]);

  const setLanguage = useCallback(async (lang: string) => {
    localStorage.setItem('preferred_language', lang);
    setLanguageState(lang);

    // Try to update server-side preference (non-blocking)
    try {
      await api.put('/language/preference', { language: lang });
    } catch (error) {
      // Silently fail — language still works client-side
      console.warn('Failed to update language preference on server:', error);
    }
  }, []);

  // Translation function: returns translated string or fallback
  const t = useCallback(
    (key: string, fallback?: string): string => {
      return translations[key] || fallback || defaultTranslations[key] || key;
    },
    [translations]
  );

  return (
    <LanguageContext.Provider value={{ language, translations, setLanguage, t, loading }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
};
