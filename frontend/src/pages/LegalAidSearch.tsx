import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Input,
  Button,
  Heading,
  Card,
  CardBody,
  Text,
  SimpleGrid,
} from '@chakra-ui/react';
import api from '../api/axios';

interface Provider {
  id: string;
  name: string;
  organization_type: string;
  specializations: string[];
  contact_phone?: string;
  contact_email?: string;
  city: string;
  state: string;
}

const LegalAidSearch: React.FC = () => {
  const [location, setLocation] = useState('');
  const [caseType, setCaseType] = useState('');
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(false);

  const searchProviders = async () => {
    setLoading(true);
    try {
      const response = await api.get('/legal-aid/search', {
        params: { location, case_type: caseType },
      });
      setProviders(response.data.providers || []);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={8}>
      <Heading mb={6}>Legal Aid Search</Heading>
      <VStack spacing={4} align="stretch" mb={6}>
        <HStack>
          <Input
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Enter city or state"
          />
          <Input
            value={caseType}
            onChange={(e) => setCaseType(e.target.value)}
            placeholder="Case type"
          />
          <Button onClick={searchProviders} colorScheme="blue" isLoading={loading}>
            Search
          </Button>
        </HStack>
      </VStack>

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
        {providers.map((provider) => (
          <Card key={provider.id}>
            <CardBody>
              <Heading size="md" mb={2}>{provider.name}</Heading>
              <Text mb={1}>{provider.organization_type}</Text>
              <Text mb={1}>{provider.city}, {provider.state}</Text>
              {provider.contact_phone && <Text>Phone: {provider.contact_phone}</Text>}
              {provider.contact_email && <Text>Email: {provider.contact_email}</Text>}
              <Text mt={2} fontSize="sm">
                Specializations: {provider.specializations.join(', ')}
              </Text>
            </CardBody>
          </Card>
        ))}
      </SimpleGrid>
    </Box>
  );
};

export default LegalAidSearch;
