import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Heading,
  Text,
  useToast,
  Link,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [collegeName, setCollegeName] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register({
        email,
        password,
        full_name: fullName,
        college_name: collegeName || undefined,
      });
      toast({
        title: 'Registration successful',
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
    <Box maxW="md" mx="auto" mt={8} p={6} borderWidth={1} borderRadius="lg">
      <VStack spacing={4} as="form" onSubmit={handleSubmit}>
        <Heading>Register for Nyaya Mitra</Heading>
        <FormControl isRequired>
          <FormLabel>Full Name</FormLabel>
          <Input
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Your full name"
          />
        </FormControl>
        <FormControl isRequired>
          <FormLabel>Email</FormLabel>
          <Input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="student@example.com"
          />
        </FormControl>
        <FormControl isRequired>
          <FormLabel>Password</FormLabel>
          <Input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Create a password"
          />
        </FormControl>
        <FormControl>
          <FormLabel>College Name (Optional)</FormLabel>
          <Input
            value={collegeName}
            onChange={(e) => setCollegeName(e.target.value)}
            placeholder="Your college"
          />
        </FormControl>
        <Button type="submit" colorScheme="blue" width="full" isLoading={loading}>
          Register
        </Button>
        <Text>
          Already have an account?{' '}
          <Link color="blue.500" onClick={() => navigate('/login')}>
            Login here
          </Link>
        </Text>
      </VStack>
    </Box>
  );
};

export default Register;
