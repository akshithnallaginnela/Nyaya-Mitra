import React, { useState } from 'react';
import {
  Box,
  VStack,
  FormControl,
  FormLabel,
  Textarea,
  Button,
  Heading,
  Text,
  Progress,
  useToast,
} from '@chakra-ui/react';
import api from '../api/axios';

const CaseAnalyzer: React.FC = () => {
  const [evidence, setEvidence] = useState('');
  const [allegations, setAllegations] = useState('');
  const [procedures, setProcedures] = useState('');
  const [timeline, setTimeline] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const analyzeCase = async () => {
    setLoading(true);
    try {
      const response = await api.post('/case/analyze', {
        evidence,
        allegations,
        procedures,
        timeline,
      });
      setResult(response.data);
    } catch (error) {
      toast({
        title: 'Analysis failed',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={8} maxW="4xl" mx="auto">
      <Heading mb={6}>Case Validity Analyzer</Heading>
      <VStack spacing={4} align="stretch">
        <FormControl>
          <FormLabel>Evidence Details</FormLabel>
          <Textarea
            value={evidence}
            onChange={(e) => setEvidence(e.target.value)}
            placeholder="Describe the evidence you have..."
          />
        </FormControl>
        <FormControl>
          <FormLabel>Allegations</FormLabel>
          <Textarea
            value={allegations}
            onChange={(e) => setAllegations(e.target.value)}
            placeholder="What are the allegations against you?"
          />
        </FormControl>
        <FormControl>
          <FormLabel>Procedures Followed</FormLabel>
          <Textarea
            value={procedures}
            onChange={(e) => setProcedures(e.target.value)}
            placeholder="What procedures were followed?"
          />
        </FormControl>
        <FormControl>
          <FormLabel>Timeline</FormLabel>
          <Textarea
            value={timeline}
            onChange={(e) => setTimeline(e.target.value)}
            placeholder="Timeline of events..."
          />
        </FormControl>
        <Button onClick={analyzeCase} colorScheme="blue" isLoading={loading}>
          Analyze Case
        </Button>

        {result && (
          <Box mt={6} p={6} borderWidth={1} borderRadius="lg">
            <Heading size="md" mb={4}>Validity Score: {result.validity_score}/100</Heading>
            <Progress value={result.validity_score} colorScheme="blue" mb={4} />
            <Text fontWeight="bold" mb={2}>Breakdown:</Text>
            <Text>Evidence: {result.breakdown?.evidence || 0}/40</Text>
            <Text>Legal Basis: {result.breakdown?.legal_basis || 0}/30</Text>
            <Text>Procedural: {result.breakdown?.procedural || 0}/20</Text>
            <Text>Timeline: {result.breakdown?.timeline || 0}/10</Text>
            {result.recommendations && (
              <>
                <Text fontWeight="bold" mt={4} mb={2}>Recommendations:</Text>
                <Text>{result.recommendations}</Text>
              </>
            )}
          </Box>
        )}
      </VStack>
    </Box>
  );
};

export default CaseAnalyzer;
