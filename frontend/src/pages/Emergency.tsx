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
} from '@chakra-ui/react';
import api from '../api/axios';

interface Contact {
  name: string;
  category: string;
  phone: string;
  description?: string;
}

const Emergency: React.FC = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadContacts();
  }, []);

  const loadContacts = async () => {
    setLoading(true);
    try {
      const response = await api.get('/emergency/contacts');
      setContacts(response.data.contacts || []);
    } catch (error) {
      console.error('Failed to load contacts:', error);
    } finally {
      setLoading(false);
    }
  };

  const callNumber = (phone: string) => {
    window.location.href = `tel:${phone}`;
  };

  return (
    <Box p={8} bg="red.50" minH="100vh">
      <VStack spacing={6} align="stretch">
        <Box textAlign="center">
          <Heading color="red.600" mb={2}>Emergency SOS</Heading>
          <Text>Quick access to emergency contacts</Text>
        </Box>

        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
          {contacts.map((contact, idx) => (
            <Card key={idx} bg="white">
              <CardBody>
                <Badge colorScheme="red" mb={2}>{contact.category}</Badge>
                <Heading size="md" mb={2}>{contact.name}</Heading>
                {contact.description && <Text mb={3}>{contact.description}</Text>}
                <Button
                  colorScheme="red"
                  onClick={() => callNumber(contact.phone)}
                  width="full"
                >
                  Call {contact.phone}
                </Button>
              </CardBody>
            </Card>
          ))}
        </SimpleGrid>
      </VStack>
    </Box>
  );
};

export default Emergency;
