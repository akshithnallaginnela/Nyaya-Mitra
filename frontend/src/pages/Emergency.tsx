import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  Button,
  SimpleGrid,
  Card,
  CardBody,
  Badge,
  Container,
  HStack,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Divider,
  Spinner,
  Center,
} from '@chakra-ui/react';
import { PhoneIcon } from '@chakra-ui/icons';
import api from '../api/axios';
import { useLanguage } from '../contexts/LanguageContext';

interface Contact {
  name: string;
  category: string;
  phone: string;
  description?: string;
}

const defaultContacts: Contact[] = [
  { name: 'Police', category: 'Law Enforcement', phone: '100', description: 'For immediate police assistance' },
  { name: 'Women Helpline', category: 'Women Safety', phone: '181', description: 'National Commission for Women' },
  { name: 'Ambulance', category: 'Medical', phone: '102', description: 'Emergency medical services' },
  { name: 'Emergency Number', category: 'General', phone: '112', description: 'Unified emergency number (like 911)' },
  { name: 'Child Helpline', category: 'Child Safety', phone: '1098', description: 'CHILDLINE India Foundation' },
  { name: 'Cyber Crime', category: 'Cyber', phone: '1930', description: 'National Cyber Crime Helpline' },
];

const Emergency: React.FC = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const { t } = useLanguage();

  useEffect(() => {
    loadContacts();
  }, []);

  const loadContacts = async () => {
    setLoading(true);
    try {
      const response = await api.get('/emergency/contacts');
      const fetched = response.data.contacts || [];
      setContacts(fetched.length > 0 ? fetched : defaultContacts);
    } catch (error) {
      console.error('Failed to load contacts:', error);
      setContacts(defaultContacts);
    } finally {
      setLoading(false);
    }
  };

  const callNumber = (phone: string) => {
    window.location.href = `tel:${phone}`;
  };

  const categoryColors: Record<string, string> = {
    'Law Enforcement': 'blue',
    'Women Safety': 'pink',
    'Medical': 'green',
    'General': 'purple',
    'Child Safety': 'orange',
    'Cyber': 'teal',
    'Legal': 'cyan',
  };

  return (
    <Box
      bgGradient="linear(to-b, red.50, white)"
      minH="calc(100vh - 60px)"
      py={8}
    >
      <Container maxW="6xl">
        {/* Header */}
        <VStack spacing={4} textAlign="center" mb={8}>
          <HStack>
            <Text fontSize="4xl">🚨</Text>
            <Heading size="xl" color="red.600">{t('emergency', 'Emergency SOS')}</Heading>
          </HStack>
          <Text color="gray.600" maxW="lg">
            Quick access to emergency helpline numbers. If you are in immediate danger, call 112 now.
          </Text>
        </VStack>

        {/* Main Emergency Button */}
        <Card
          borderRadius="2xl"
          boxShadow="xl"
          bg="red.600"
          color="white"
          mb={8}
          cursor="pointer"
          onClick={() => callNumber('112')}
          _hover={{ bg: 'red.700', transform: 'scale(1.02)' }}
          transition="all 0.2s"
        >
          <CardBody py={8} textAlign="center">
            <VStack spacing={3}>
              <Text fontSize="5xl">📞</Text>
              <Heading size="lg">Call 112 — Emergency</Heading>
              <Text opacity={0.9}>Unified Emergency Number (Police, Fire, Ambulance)</Text>
              <Button
                size="lg"
                colorScheme="whiteAlpha"
                variant="solid"
                leftIcon={<PhoneIcon />}
                borderRadius="full"
                px={8}
                fontWeight="800"
              >
                CALL NOW
              </Button>
            </VStack>
          </CardBody>
        </Card>

        <Alert status="warning" borderRadius="xl" mb={6}>
          <AlertIcon />
          <Box>
            <AlertTitle fontWeight="700">Stay Calm</AlertTitle>
            <AlertDescription>
              If you are in immediate physical danger, leave the area first and then call for help.
              Note down details while they are fresh in your memory.
            </AlertDescription>
          </Box>
        </Alert>

        {/* Contact Cards */}
        <Heading size="md" color="gray.700" mb={4}>{t('emergency_contacts', 'All Emergency Contacts')}</Heading>

        {loading ? (
          <Center py={12}>
            <Spinner size="xl" color="red.500" />
          </Center>
        ) : (
          <SimpleGrid columns={{ base: 1, sm: 2, lg: 3 }} spacing={4}>
            {contacts.map((contact, idx) => (
              <Card
                key={idx}
                borderRadius="xl"
                boxShadow="sm"
                _hover={{ boxShadow: 'lg', transform: 'translateY(-2px)' }}
                transition="all 0.2s"
                borderLeft="4px solid"
                borderLeftColor={`${categoryColors[contact.category] || 'gray'}.400`}
              >
                <CardBody p={5}>
                  <HStack justify="space-between" mb={2}>
                    <Badge
                      colorScheme={categoryColors[contact.category] || 'gray'}
                      fontSize="xs"
                      px={2}
                      borderRadius="full"
                    >
                      {contact.category}
                    </Badge>
                  </HStack>

                  <Heading size="sm" mb={2} color="gray.800">{contact.name}</Heading>
                  {contact.description && (
                    <Text fontSize="sm" color="gray.600" mb={3}>{contact.description}</Text>
                  )}

                  <Button
                    colorScheme="red"
                    onClick={() => callNumber(contact.phone)}
                    width="full"
                    borderRadius="lg"
                    leftIcon={<PhoneIcon />}
                    fontWeight="700"
                    size="md"
                  >
                    Call {contact.phone}
                  </Button>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        )}

        <Divider my={8} />

        <Card borderRadius="xl" boxShadow="sm" bg="blue.50" p={5}>
          <VStack spacing={2} textAlign="center">
            <Text fontWeight="700" color="blue.700">Need Legal Help?</Text>
            <Text fontSize="sm" color="blue.600">
              Use the Legal Aid Search feature to find free legal aid providers near you, 
              or chat with our AI assistant for immediate legal guidance.
            </Text>
          </VStack>
        </Card>
      </Container>
    </Box>
  );
};

export default Emergency;
