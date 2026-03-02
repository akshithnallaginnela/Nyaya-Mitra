import React, { useState } from 'react';
import {
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Heading,
  Text,
  useToast,
  Link,
  Container,
  Card,
  CardBody,
  Flex,
  Divider,
  InputGroup,
  InputLeftElement,
  Select,
} from '@chakra-ui/react';
import { EmailIcon, LockIcon } from '@chakra-ui/icons';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';

const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [collegeName, setCollegeName] = useState('');
  const [preferredLanguage, setPreferredLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const { t } = useLanguage();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register({
        email,
        password,
        full_name: fullName,
        college_name: collegeName || undefined,
        preferred_language: preferredLanguage,
      });
      toast({
        title: 'Registration successful!',
        description: 'Welcome to Nyaya Mitra',
        status: 'success',
        duration: 3000,
      });
      navigate('/dashboard');
    } catch (error: any) {
      toast({
        title: 'Registration failed',
        description: error.response?.data?.detail || 'Please try again',
        status: 'error',
        duration: 5000,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Flex minH="calc(100vh - 60px)" bg="gray.50" align="center" justify="center" px={4} py={8}>
      <Container maxW="md">
        <VStack spacing={4} textAlign="center" mb={6}>
          <Text fontSize="5xl">⚖️</Text>
          <Heading size="lg" bgGradient="linear(to-r, brand.600, brand.400)" bgClip="text">
            {t('register', 'Join Nyaya Mitra')}
          </Heading>
          <Text color="gray.600">Create your account to get started</Text>
        </VStack>

        <Card borderRadius="2xl" boxShadow="lg" bg="white">
          <CardBody p={8}>
            <VStack spacing={4} as="form" onSubmit={handleSubmit}>
              <Heading size="md" color="gray.700">{t('register', 'Create Account')}</Heading>

              <FormControl isRequired>
                <FormLabel fontSize="sm" fontWeight="600" color="gray.600">{t('full_name', 'Full Name')}</FormLabel>
                <InputGroup>
                  <InputLeftElement pointerEvents="none">
                    <Text color="gray.400">👤</Text>
                  </InputLeftElement>
                  <Input
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Your full name"
                    size="lg"
                    borderRadius="xl"
                  />
                </InputGroup>
              </FormControl>

              <FormControl isRequired>
                <FormLabel fontSize="sm" fontWeight="600" color="gray.600">Email</FormLabel>
                <InputGroup>
                  <InputLeftElement pointerEvents="none">
                    <EmailIcon color="gray.400" />
                  </InputLeftElement>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="student@example.com"
                    size="lg"
                    borderRadius="xl"
                  />
                </InputGroup>
              </FormControl>

              <FormControl isRequired>
                <FormLabel fontSize="sm" fontWeight="600" color="gray.600">Password</FormLabel>
                <InputGroup>
                  <InputLeftElement pointerEvents="none">
                    <LockIcon color="gray.400" />
                  </InputLeftElement>
                  <Input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Create a strong password"
                    size="lg"
                    borderRadius="xl"
                  />
                </InputGroup>
              </FormControl>

              <FormControl>
                <FormLabel fontSize="sm" fontWeight="600" color="gray.600">{t('college_name', 'College Name')} (Optional)</FormLabel>
                <InputGroup>
                  <InputLeftElement pointerEvents="none">
                    <Text color="gray.400">🎓</Text>
                  </InputLeftElement>
                  <Input
                    value={collegeName}
                    onChange={(e) => setCollegeName(e.target.value)}
                    placeholder="Your college"
                    size="lg"
                    borderRadius="xl"
                  />
                </InputGroup>
              </FormControl>

              <FormControl>
                <FormLabel fontSize="sm" fontWeight="600" color="gray.600">{t('language', 'Preferred Language')}</FormLabel>
                <Select
                  value={preferredLanguage}
                  onChange={(e) => setPreferredLanguage(e.target.value)}
                  size="lg"
                  borderRadius="xl"
                >
                  <option value="en">🇬🇧 English</option>
                  <option value="hi">🇮🇳 हिंदी (Hindi)</option>
                  <option value="ta">🇮🇳 தமிழ் (Tamil)</option>
                  <option value="te">🇮🇳 తెలుగు (Telugu)</option>
                  <option value="bn">🇮🇳 বাংলা (Bengali)</option>
                  <option value="mr">🇮🇳 मराठी (Marathi)</option>
                  <option value="gu">🇮🇳 ગુજરાતી (Gujarati)</option>
                </Select>
              </FormControl>

              <Button
                type="submit"
                colorScheme="brand"
                width="full"
                size="lg"
                isLoading={loading}
                borderRadius="xl"
                fontWeight="700"
                mt={2}
              >
                {t('register', 'Create Account')}
              </Button>

              <Divider />

              <Text fontSize="sm" color="gray.600">
                Already have an account?{' '}
                <Link color="brand.500" fontWeight="600" onClick={() => navigate('/login')}>
                  {t('login', 'Sign in here')}
                </Link>
              </Text>
            </VStack>
          </CardBody>
        </Card>
      </Container>
    </Flex>
  );
};

export default Register;
