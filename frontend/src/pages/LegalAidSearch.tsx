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
  Container,
  Badge,
  Select,
  Divider,
  Tag,
  TagLabel,
  Wrap,
  WrapItem,
} from '@chakra-ui/react';
import { SearchIcon } from '@chakra-ui/icons';
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
  const [searched, setSearched] = useState(false);

  const searchProviders = async () => {
    setLoading(true);
    setSearched(true);
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

  const orgTypeColors: Record<string, string> = {
    'NGO': 'green',
    'Legal Aid Clinic': 'blue',
    'Government': 'purple',
    'Pro Bono': 'orange',
    'Law School Clinic': 'teal',
  };

  return (
    <Box bg="gray.50" minH="calc(100vh - 60px)" py={8}>
      <Container maxW="6xl">
        <HStack mb={6}>
          <Text fontSize="3xl">⚖️</Text>
          <VStack align="start" spacing={0}>
            <Heading size="lg" color="gray.800">Legal Aid Search</Heading>
            <Text color="gray.600" fontSize="sm">
              Find free legal aid providers, NGOs, and legal clinics near you
            </Text>
          </VStack>
        </HStack>

        <Card borderRadius="xl" boxShadow="md" mb={6}>
          <CardBody p={6}>
            <HStack spacing={4} flexWrap={{ base: 'wrap', md: 'nowrap' }}>
              <Input
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="🏙️ Enter city or state..."
                size="lg"
                bg="gray.50"
                borderRadius="xl"
                flex={1}
                _focus={{ bg: 'white' }}
              />
              <Select
                value={caseType}
                onChange={(e) => setCaseType(e.target.value)}
                placeholder="📂 Case type..."
                size="lg"
                bg="gray.50"
                borderRadius="xl"
                flex={1}
                _focus={{ bg: 'white' }}
              >
                <option value="harassment">Harassment</option>
                <option value="defamation">Defamation</option>
                <option value="false_accusation">False Accusation</option>
                <option value="domestic_violence">Domestic Violence</option>
                <option value="property">Property Dispute</option>
                <option value="criminal">Criminal</option>
                <option value="civil">Civil</option>
              </Select>
              <Button
                onClick={searchProviders}
                colorScheme="brand"
                isLoading={loading}
                size="lg"
                borderRadius="xl"
                leftIcon={<SearchIcon />}
                px={8}
              >
                Search
              </Button>
            </HStack>
          </CardBody>
        </Card>

        {searched && providers.length === 0 && !loading && (
          <Card borderRadius="xl" textAlign="center" py={12}>
            <CardBody>
              <Text fontSize="4xl" mb={4}>🔍</Text>
              <Heading size="md" color="gray.600" mb={2}>No providers found</Heading>
              <Text color="gray.500">Try a different location or case type</Text>
            </CardBody>
          </Card>
        )}

        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
          {providers.map((provider) => (
            <Card key={provider.id} borderRadius="xl" boxShadow="sm" _hover={{ boxShadow: 'lg' }} transition="all 0.2s">
              <CardBody p={5}>
                <HStack justify="space-between" mb={2}>
                  <Heading size="sm" color="gray.800">{provider.name}</Heading>
                  <Badge
                    colorScheme={orgTypeColors[provider.organization_type] || 'gray'}
                    fontSize="xs"
                    px={2}
                    borderRadius="full"
                  >
                    {provider.organization_type}
                  </Badge>
                </HStack>

                <Text fontSize="sm" color="gray.600" mb={3}>
                  📍 {provider.city}, {provider.state}
                </Text>

                {provider.contact_phone && (
                  <Text fontSize="sm" mb={1}>
                    📞 <Text as="span" color="brand.600" fontWeight="600">{provider.contact_phone}</Text>
                  </Text>
                )}
                {provider.contact_email && (
                  <Text fontSize="sm" mb={3}>
                    📧 <Text as="span" color="brand.600" fontWeight="600">{provider.contact_email}</Text>
                  </Text>
                )}

                {provider.specializations.length > 0 && (
                  <Wrap mt={2}>
                    {provider.specializations.map((spec, idx) => (
                      <WrapItem key={idx}>
                        <Tag size="sm" colorScheme="gray" borderRadius="full">
                          <TagLabel fontSize="xs">{spec}</TagLabel>
                        </Tag>
                      </WrapItem>
                    ))}
                  </Wrap>
                )}
              </CardBody>
            </Card>
          ))}
        </SimpleGrid>
      </Container>
    </Box>
  );
};

export default LegalAidSearch;
