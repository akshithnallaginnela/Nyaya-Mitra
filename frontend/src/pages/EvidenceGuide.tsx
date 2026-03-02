import React, { useState } from 'react';
import {
  Box,
  VStack,
  Select,
  Button,
  Heading,
  Text,
  List,
  ListItem,
  ListIcon,
  Container,
  Card,
  CardBody,
  HStack,
  Badge,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';
import { CheckCircleIcon } from '@chakra-ui/icons';
import api from '../api/axios';
import { useLanguage } from '../contexts/LanguageContext';

const EvidenceGuide: React.FC = () => {
  const [caseType, setCaseType] = useState('');
  const [guide, setGuide] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const { t, language } = useLanguage();

  const loadGuide = async () => {
    if (!caseType) return;
    setLoading(true);
    try {
      const response = await api.get('/evidence/guide', {
        params: { case_type: caseType, language },
      });
      setGuide(response.data);
    } catch (error) {
      console.error('Failed to load guide:', error);
    } finally {
      setLoading(false);
    }
  };

  const caseTypeLabels: Record<string, { label: string; icon: string }> = {
    harassment: { label: 'Harassment', icon: '🚫' },
    defamation: { label: 'Defamation', icon: '📰' },
    assault: { label: 'Assault', icon: '⚠️' },
    fraud: { label: 'Fraud', icon: '💰' },
  };

  return (
    <Box bg="gray.50" minH="calc(100vh - 60px)" py={8}>
      <Container maxW="4xl">
        <HStack mb={6}>
          <Text fontSize="3xl">📋</Text>
          <VStack align="start" spacing={0}>
            <Heading size="lg" color="gray.800">{t('evidence_guide', 'Evidence Documentation Guide')}</Heading>
            <Text color="gray.600" fontSize="sm">
              Learn how to properly collect and preserve evidence for your case
            </Text>
          </VStack>
        </HStack>

        <Card borderRadius="xl" boxShadow="md" mb={6}>
          <CardBody p={6}>
            <VStack spacing={4} align="stretch">
              <FormControlLabel>
                <Text fontWeight="600" color="gray.700" mb={2}>📂 Select Case Type</Text>
                <Select
                  value={caseType}
                  onChange={(e) => {
                    setCaseType(e.target.value);
                    setGuide(null);
                  }}
                  placeholder="Choose your case type..."
                  size="lg"
                  bg="gray.50"
                  borderRadius="xl"
                  _focus={{ bg: 'white' }}
                >
                  {Object.entries(caseTypeLabels).map(([value, { label, icon }]) => (
                    <option key={value} value={value}>
                      {icon} {label}
                    </option>
                  ))}
                </Select>
              </FormControlLabel>

              <Button
                onClick={loadGuide}
                colorScheme="brand"
                isLoading={loading}
                loadingText="Loading guide..."
                size="lg"
                borderRadius="xl"
                fontWeight="700"
                isDisabled={!caseType}
              >
                📋 {t('collect_evidence', 'Get Evidence Guide')}
              </Button>
            </VStack>
          </CardBody>
        </Card>

        {guide && (
          <VStack spacing={4} align="stretch">
            <Card borderRadius="xl" boxShadow="lg" borderTop="4px solid" borderTopColor="teal.400">
              <CardBody p={6}>
                <HStack justify="space-between" mb={4}>
                  <Heading size="md" color="gray.800">
                    {t('collect_evidence', 'Evidence Collection Steps')}
                  </Heading>
                  <Badge colorScheme="teal" fontSize="sm" px={3} py={1} borderRadius="full">
                    {guide.steps?.length || 0} Steps
                  </Badge>
                </HStack>

                <List spacing={4}>
                  {guide.steps?.map((step: string, idx: number) => (
                    <ListItem
                      key={idx}
                      display="flex"
                      alignItems="flex-start"
                      bg="gray.50"
                      p={3}
                      borderRadius="lg"
                    >
                      <ListIcon as={CheckCircleIcon} color="green.500" mt={1} />
                      <Text color="gray.700" lineHeight="tall">{step}</Text>
                    </ListItem>
                  ))}
                </List>
              </CardBody>
            </Card>

            {guide.warning && (
              <Alert
                status="warning"
                borderRadius="xl"
                flexDirection="column"
                alignItems="flex-start"
                p={5}
              >
                <HStack mb={2}>
                  <AlertIcon />
                  <AlertTitle fontWeight="700">Important Warning</AlertTitle>
                </HStack>
                <AlertDescription color="gray.700" lineHeight="tall">
                  {guide.warning}
                </AlertDescription>
              </Alert>
            )}

            <Alert status="error" borderRadius="xl" p={4}>
              <AlertIcon />
              <Box>
                <AlertTitle fontWeight="700" fontSize="sm">Do NOT tamper with evidence</AlertTitle>
                <AlertDescription fontSize="sm">
                  Tampering with evidence is a criminal offense under Indian law (Section 204 IPC).
                </AlertDescription>
              </Box>
            </Alert>
          </VStack>
        )}
      </Container>
    </Box>
  );
};

// Simple wrapper component since we're not using FormControl here
const FormControlLabel: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <Box>{children}</Box>
);

export default EvidenceGuide;
