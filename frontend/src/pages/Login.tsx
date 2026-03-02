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
  HStack,
  Divider,
  InputGroup,
  InputLeftElement,
} from '@chakra-ui/react';
import { EmailIcon, LockIcon } from '@chakra-ui/icons';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      toast({
        title: 'Login successful',
        status: 'success',
        duration: 3000,
      });
      navigate('/dashboard');
    } catch (error: any) {
      toast({
        title: 'Login failed',
        description: error.response?.data?.detail || 'Invalid credentials',
        status: 'error',
        duration: 5000,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Flex minH="calc(100vh - 60px)" bg="gray.50" align="center" justify="center" px={4}>
      <Container maxW="md">
        <VStack spacing={6} textAlign="center" mb={6}>
          <Text fontSize="5xl">⚖️</Text>
          <Heading size="lg" bgGradient="linear(to-r, brand.600, brand.400)" bgClip="text">
            Welcome to Nyaya Mitra
          </Heading>
          <Text color="gray.600">
            Your AI-powered legal companion for Indian college students
          </Text>
        </VStack>

        <Card borderRadius="2xl" boxShadow="lg" bg="white">
          <CardBody p={8}>
            <VStack spacing={5} as="form" onSubmit={handleSubmit}>
              <Heading size="md" color="gray.700">Sign In</Heading>

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
                    placeholder="Enter your password"
                    size="lg"
                    borderRadius="xl"
                  />
                </InputGroup>
              </FormControl>

              <Button
                type="submit"
                colorScheme="brand"
                width="full"
                size="lg"
                isLoading={loading}
                borderRadius="xl"
                fontWeight="700"
              >
                Sign In
              </Button>

              <Divider />

              <Text fontSize="sm" color="gray.600">
                Don't have an account?{' '}
                <Link color="brand.500" fontWeight="600" onClick={() => navigate('/register')}>
                  Register here
                </Link>
              </Text>
            </VStack>
          </CardBody>
        </Card>

        <HStack spacing={6} justify="center" mt={6}>
          <VStack spacing={0}>
            <Text fontSize="lg">🔒</Text>
            <Text fontSize="xs" color="gray.500">Encrypted</Text>
          </VStack>
          <VStack spacing={0}>
            <Text fontSize="lg">🇮🇳</Text>
            <Text fontSize="xs" color="gray.500">Indian Law</Text>
          </VStack>
          <VStack spacing={0}>
            <Text fontSize="lg">🤖</Text>
            <Text fontSize="xs" color="gray.500">AI Powered</Text>
          </VStack>
        </HStack>
      </Container>
    </Flex>
  );
};

export default Login;
