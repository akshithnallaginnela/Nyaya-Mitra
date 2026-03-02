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
  Container,
  Card,
  CardBody,
  HStack,
  Badge,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Divider,
} from '@chakra-ui/react';
import api from '../api/axios';
import { useLanguage } from '../contexts/LanguageContext';

const CaseAnalyzer: React.FC = () => {
  const [evidence, setEvidence] = useState('');
  const [allegations, setAllegations] = useState('');
  const [procedures, setProcedures] = useState('');
  const [timeline, setTimeline] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const toast = useToast();
  const { t, language } = useLanguage();

  const analyzeCase = async () => {
    if (!evidence.trim() && !allegations.trim()) {
      toast({
        title: 'Please provide details',
        description: 'At least evidence or allegations are required',
        status: 'warning',
        duration: 3000,
      });
      return;
    }
    setLoading(true);
    try {
      const response = await api.post('/case/analyze', {
        evidence,
        allegations,
        procedures,
        timeline,
        language,
      });
      setResult(response.data);
    } catch (error) {
      toast({
        title: 'Analysis failed',
        description: 'Please try again later',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'green';
    if (score >= 40) return 'yellow';
    return 'red';
  };

  return (
    <Box bg="gray.50" minH="calc(100vh - 60px)" py={8}>
      <Container maxW="4xl">
        <HStack mb={6}>
          <Text fontSize="3xl">🔍</Text>
          <VStack align="start" spacing={0}>
            <Heading size="lg" color="gray.800">{t('case_analysis', 'Case Validity Analyzer')}</Heading>
            <Text color="gray.600" fontSize="sm">
              Analyze the strength and validity of your case with AI
            </Text>
          </VStack>
        </HStack>

        <Card borderRadius="xl" boxShadow="md" mb={6}>
          <CardBody p={6}>
            <VStack spacing={5} align="stretch">
              <FormControl>
                <FormLabel fontWeight="600" color="gray.700">
                  📝 Evidence Details
                </FormLabel>
                <Textarea
                  value={evidence}
                  onChange={(e) => setEvidence(e.target.value)}
                  placeholder="Describe the evidence you have (documents, witnesses, digital records, etc.)..."
                  rows={4}
                  bg="gray.50"
                  borderRadius="xl"
                  _focus={{ bg: 'white' }}
                />
              </FormControl>

              <FormControl>
                <FormLabel fontWeight="600" color="gray.700">
                  ⚠️ Allegations
                </FormLabel>
                <Textarea
                  value={allegations}
                  onChange={(e) => setAllegations(e.target.value)}
                  placeholder="What are the allegations against you? Be as specific as possible..."
                  rows={4}
                  bg="gray.50"
                  borderRadius="xl"
                  _focus={{ bg: 'white' }}
                />
              </FormControl>

              <FormControl>
                <FormLabel fontWeight="600" color="gray.700">
                  📋 Procedures Followed
                </FormLabel>
                <Textarea
                  value={procedures}
                  onChange={(e) => setProcedures(e.target.value)}
                  placeholder="What procedures were followed by authorities? (FIR filing, investigation, etc.)"
                  rows={3}
                  bg="gray.50"
                  borderRadius="xl"
                  _focus={{ bg: 'white' }}
                />
              </FormControl>

              <FormControl>
                <FormLabel fontWeight="600" color="gray.700">
                  🕐 Timeline of Events
                </FormLabel>
                <Textarea
                  value={timeline}
                  onChange={(e) => setTimeline(e.target.value)}
                  placeholder="Describe the chronological sequence of events..."
                  rows={3}
                  bg="gray.50"
                  borderRadius="xl"
                  _focus={{ bg: 'white' }}
                />
              </FormControl>

              <Button
                onClick={analyzeCase}
                colorScheme="brand"
                isLoading={loading}
                loadingText="Analyzing..."
                size="lg"
                borderRadius="xl"
                fontWeight="700"
              >
              🔍 {t('case_analysis', 'Analyze Case')}
              </Button>
            </VStack>
          </CardBody>
        </Card>

        {result && (
          <Card borderRadius="xl" boxShadow="lg" borderTop="4px solid" borderTopColor={`${getScoreColor(result.validity_score)}.400`}>
            <CardBody p={6}>
              <VStack spacing={5} align="stretch">
                <HStack justify="space-between">
                  <Heading size="md" color="gray.800">Analysis Results</Heading>
                  <Badge
                    colorScheme={getScoreColor(result.validity_score)}
                    fontSize="md"
                    px={4}
                    py={1}
                    borderRadius="full"
                  >
                    Score: {result.validity_score}/100
                  </Badge>
                </HStack>

                <Progress
                  value={result.validity_score}
                  colorScheme={getScoreColor(result.validity_score)}
                  borderRadius="full"
                  size="lg"
                  hasStripe
                  isAnimated
                />

                <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
                  <Stat bg="blue.50" p={3} borderRadius="lg" textAlign="center">
                    <StatLabel fontSize="xs" color="gray.600">{t('evidence_strength', 'Evidence')}</StatLabel>
                    <StatNumber color="blue.600">{result.breakdown?.evidence || 0}</StatNumber>
                    <StatHelpText>/40</StatHelpText>
                  </Stat>
                  <Stat bg="purple.50" p={3} borderRadius="lg" textAlign="center">
                    <StatLabel fontSize="xs" color="gray.600">{t('legal_basis', 'Legal Basis')}</StatLabel>
                    <StatNumber color="purple.600">{result.breakdown?.legal_basis || 0}</StatNumber>
                    <StatHelpText>/30</StatHelpText>
                  </Stat>
                  <Stat bg="teal.50" p={3} borderRadius="lg" textAlign="center">
                    <StatLabel fontSize="xs" color="gray.600">{t('procedural_compliance', 'Procedural')}</StatLabel>
                    <StatNumber color="teal.600">{result.breakdown?.procedural || 0}</StatNumber>
                    <StatHelpText>/20</StatHelpText>
                  </Stat>
                  <Stat bg="orange.50" p={3} borderRadius="lg" textAlign="center">
                    <StatLabel fontSize="xs" color="gray.600">{t('timeline_analysis', 'Timeline')}</StatLabel>
                    <StatNumber color="orange.600">{result.breakdown?.timeline || 0}</StatNumber>
                    <StatHelpText>/10</StatHelpText>
                  </Stat>
                </SimpleGrid>

                {result.recommendations && (
                  <>
                    <Divider />
                    <Box>
                      <Text fontWeight="700" mb={2} color="gray.700">
                        💡 {t('recommendations', 'Recommendations')}
                      </Text>
                      <Text color="gray.600" lineHeight="tall" whiteSpace="pre-wrap">
                        {result.recommendations}
                      </Text>
                    </Box>
                  </>
                )}
              </VStack>
            </CardBody>
          </Card>
        )}
      </Container>
    </Box>
  );
};

export default CaseAnalyzer;
