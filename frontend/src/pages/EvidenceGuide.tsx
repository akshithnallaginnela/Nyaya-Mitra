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
} from '@chakra-ui/react';
import { CheckCircleIcon } from '@chakra-ui/icons';
import api from '../api/axios';

const EvidenceGuide: React.FC = () => {
  const [caseType, setCaseType] = useState('');
  const [guide, setGuide] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const loadGuide = async () => {
    setLoading(true);
    try {
      const response = await api.get('/evidence/guide', {
        params: { case_type: caseType },
      });
      setGuide(response.data);
    } catch (error) {
      console.error('Failed to load guide:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={8} maxW="4xl" mx="auto">
      <Heading mb={6}>Evidence Documentation Guide</Heading>
      <VStack spacing={4} align="stretch">
        <Select
          value={caseType}
          onChange={(e) => setCaseType(e.target.value)}
          placeholder="Select case type"
        >
          <option value="harassment">Harassment</option>
          <option value="defamation">Defamation</option>
          <option value="assault">Assault</option>
          <option value="fraud">Fraud</option>
        </Select>
        <Button onClick={loadGuide} colorScheme="blue" isLoading={loading}>
          Get Guide
        </Button>

        {guide && (
          <Box mt={6} p={6} borderWidth={1} borderRadius="lg">
            <Heading size="md" mb={4}>Evidence Collection Steps</Heading>
            <List spacing={3}>
              {guide.steps?.map((step: string, idx: number) => (
                <ListItem key={idx}>
                  <ListIcon as={CheckCircleIcon} color="green.500" />
                  {step}
                </ListItem>
              ))}
            </List>
            <Text fontWeight="bold" mt={6} mb={2} color="red.600">
              Warning: Do not tamper with evidence
            </Text>
            <Text>{guide.warning}</Text>
          </Box>
        )}
      </VStack>
    </Box>
  );
};

export default EvidenceGuide;
