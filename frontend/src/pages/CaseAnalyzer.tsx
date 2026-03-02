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
  List,
  ListItem,
  ListIcon,
} from '@chakra-ui/react';
import { CheckCircleIcon, WarningIcon, InfoIcon } from '@chakra-ui/icons';
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
      // Backend expects: evidence: List[str], procedures_followed: List[str], timeline: dict
      const evidenceList = evidence.trim() ? evidence.split('\n').map(s => s.trim()).filter(Boolean) : [];
      const proceduresList = procedures.trim() ? procedures.split('\n').map(s => s.trim()).filter(Boolean) : [];
      const timelineObj = timeline.trim() ? { events: timeline } : {};

      const response = await api.post('/case/analyze', {
        evidence: evidenceList,
        allegations,
        procedures_followed: proceduresList,
        timeline: timelineObj,
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
                <Text fontSize="xs" color="gray.500" mb={1}>
                  List each piece of PROOF you have — one per line (screenshots, photos, documents, messages, receipts, CCTV footage, etc.)
                </Text>
                <Textarea
                  value={evidence}
                  onChange={(e) => setEvidence(e.target.value)}
                  placeholder={"Screenshot of threatening WhatsApp messages\nCCTV footage from college campus (requested from security)\nRent agreement signed by both parties\nBank transfer receipt of Rs 50000 deposit\nPhotos of flat condition at move-out"}
                  rows={5}
                  bg="gray.50"
                  borderRadius="xl"
                  _focus={{ bg: 'white' }}
                />
              </FormControl>

              <FormControl>
                <FormLabel fontWeight="600" color="gray.700">
                  ⚠️ Allegations / What Happened
                </FormLabel>
                <Text fontSize="xs" color="gray.500" mb={1}>
                  Describe your situation in detail — what happened, who is responsible, and what harm was caused. Mention any law sections if you know them.
                </Text>
                <Textarea
                  value={allegations}
                  onChange={(e) => setAllegations(e.target.value)}
                  placeholder="My landlord is refusing to return my security deposit of Rs 50000 despite vacating the flat on time with no damage. This is a violation of the rent agreement clause 7 and Section 420 IPC (cheating). The landlord verbally threatened me when I demanded my deposit back..."
                  rows={5}
                  bg="gray.50"
                  borderRadius="xl"
                  _focus={{ bg: 'white' }}
                />
              </FormControl>

              <FormControl>
                <FormLabel fontWeight="600" color="gray.700">
                  📋 Steps You've Already Taken
                </FormLabel>
                <Text fontSize="xs" color="gray.500" mb={1}>
                  List each action you've taken — one per line (complaints filed, notices sent, FIR, college grievance cell, etc.)
                </Text>
                <Textarea
                  value={procedures}
                  onChange={(e) => setProcedures(e.target.value)}
                  placeholder={"Sent written demand notice to landlord via registered post\nFiled complaint with college grievance cell on 10-Feb-2025\nFiled FIR at local police station\nComplained to consumer forum online"}
                  rows={4}
                  bg="gray.50"
                  borderRadius="xl"
                  _focus={{ bg: 'white' }}
                />
              </FormControl>

              <FormControl>
                <FormLabel fontWeight="600" color="gray.700">
                  🕐 Timeline of Events
                </FormLabel>
                <Text fontSize="xs" color="gray.500" mb={1}>
                  List events in order with dates: "Date — What happened". Start from the first incident.
                </Text>
                <Textarea
                  value={timeline}
                  onChange={(e) => setTimeline(e.target.value)}
                  placeholder={"15-Jan-2025 — Incident happened at college campus\n16-Jan-2025 — Reported to college administration\n20-Jan-2025 — Sent written complaint via email\n01-Feb-2025 — Filed FIR at police station\n15-Feb-2025 — Received response from college"}
                  rows={5}
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
          <VStack spacing={4} align="stretch">
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
                      <StatNumber color="blue.600">{result.score_breakdown?.evidence_strength || 0}</StatNumber>
                      <StatHelpText>/40</StatHelpText>
                    </Stat>
                    <Stat bg="purple.50" p={3} borderRadius="lg" textAlign="center">
                      <StatLabel fontSize="xs" color="gray.600">{t('legal_basis', 'Legal Basis')}</StatLabel>
                      <StatNumber color="purple.600">{result.score_breakdown?.legal_basis || 0}</StatNumber>
                      <StatHelpText>/30</StatHelpText>
                    </Stat>
                    <Stat bg="teal.50" p={3} borderRadius="lg" textAlign="center">
                      <StatLabel fontSize="xs" color="gray.600">{t('procedural_compliance', 'Procedural')}</StatLabel>
                      <StatNumber color="teal.600">{result.score_breakdown?.procedural_compliance || 0}</StatNumber>
                      <StatHelpText>/20</StatHelpText>
                    </Stat>
                    <Stat bg="orange.50" p={3} borderRadius="lg" textAlign="center">
                      <StatLabel fontSize="xs" color="gray.600">{t('timeline_analysis', 'Timeline')}</StatLabel>
                      <StatNumber color="orange.600">{result.score_breakdown?.timeline_reasonableness || 0}</StatNumber>
                      <StatHelpText>/10</StatHelpText>
                    </Stat>
                  </SimpleGrid>
                </VStack>
              </CardBody>
            </Card>

            {result.strengths && result.strengths.length > 0 && (
              <Card borderRadius="xl" boxShadow="md">
                <CardBody p={5}>
                  <Text fontWeight="700" mb={3} color="green.700">✅ Strengths</Text>
                  <List spacing={2}>
                    {result.strengths.map((s: string, i: number) => (
                      <ListItem key={i} display="flex" alignItems="flex-start">
                        <ListIcon as={CheckCircleIcon} color="green.500" mt={1} />
                        <Text fontSize="sm" color="gray.700">{s}</Text>
                      </ListItem>
                    ))}
                  </List>
                </CardBody>
              </Card>
            )}

            {result.weaknesses && result.weaknesses.length > 0 && (
              <Card borderRadius="xl" boxShadow="md" borderLeft="4px solid" borderLeftColor="red.400">
                <CardBody p={5}>
                  <Text fontWeight="700" mb={3} color="red.700">⚠️ Areas to Improve</Text>
                  <Text fontSize="xs" color="gray.500" mb={3}>Each item tells you what's weak AND exactly how to fix it</Text>
                  <List spacing={4}>
                    {result.weaknesses.map((w: string, i: number) => {
                      const parts = w.split('HOW TO FIX:');
                      return (
                        <ListItem key={i} bg="red.50" p={3} borderRadius="lg">
                          <HStack align="flex-start" spacing={2}>
                            <WarningIcon color="red.500" mt={1} flexShrink={0} />
                            <VStack align="start" spacing={1} w="full">
                              <Text fontSize="sm" fontWeight="600" color="red.800">{parts[0].trim()}</Text>
                              {parts[1] && (
                                <Box bg="white" p={2} borderRadius="md" w="full" borderLeft="3px solid" borderLeftColor="green.400">
                                  <Text fontSize="xs" fontWeight="600" color="green.700" mb={1}>💡 How to fix:</Text>
                                  <Text fontSize="xs" color="gray.700">{parts[1].trim()}</Text>
                                </Box>
                              )}
                            </VStack>
                          </HStack>
                        </ListItem>
                      );
                    })}
                  </List>
                </CardBody>
              </Card>
            )}

            {result.missing_elements && result.missing_elements.length > 0 && (
              <Card borderRadius="xl" boxShadow="md" borderLeft="4px solid" borderLeftColor="orange.400">
                <CardBody p={5}>
                  <Text fontWeight="700" mb={3} color="orange.700">📋 What You Still Need</Text>
                  <Text fontSize="xs" color="gray.500" mb={3}>These items will boost your score significantly when added</Text>
                  <List spacing={3}>
                    {result.missing_elements.map((m: string, i: number) => (
                      <ListItem key={i} bg="orange.50" p={3} borderRadius="lg">
                        <HStack align="flex-start" spacing={2}>
                          <InfoIcon color="orange.500" mt={1} flexShrink={0} />
                          <Text fontSize="sm" color="gray.700">{m}</Text>
                        </HStack>
                      </ListItem>
                    ))}
                  </List>
                </CardBody>
              </Card>
            )}

            {result.recommendations && result.recommendations.length > 0 && (
              <Card borderRadius="xl" boxShadow="md" borderLeft="4px solid" borderLeftColor="blue.400">
                <CardBody p={5}>
                  <Text fontWeight="700" mb={3} color="blue.700">🎯 {t('recommendations', 'Your Next Steps')}</Text>
                  <Text fontSize="xs" color="gray.500" mb={3}>Follow these steps in order to strengthen your case</Text>
                  <List spacing={3}>
                    {result.recommendations.map((r: string, i: number) => (
                      <ListItem key={i} bg="blue.50" p={3} borderRadius="lg">
                        <HStack align="flex-start" spacing={2}>
                          <Text fontWeight="700" color="blue.600" fontSize="sm" flexShrink={0}>Step {i + 1}:</Text>
                          <Text fontSize="sm" color="gray.700">{r}</Text>
                        </HStack>
                      </ListItem>
                    ))}
                  </List>
                </CardBody>
              </Card>
            )}

            {result.requires_legal_consultation && (
              <Card borderRadius="xl" boxShadow="md" bg="red.50" borderLeft="4px solid" borderLeftColor="red.400">
                <CardBody p={5}>
                  <Text fontWeight="700" color="red.700">
                    ⚖️ Legal Consultation Recommended
                  </Text>
                  <Text fontSize="sm" color="red.600" mt={1}>
                    Based on the analysis, it is strongly recommended to consult with a qualified lawyer for this case.
                  </Text>
                </CardBody>
              </Card>
            )}
          </VStack>
        )}
      </Container>
    </Box>
  );
};


export default CaseAnalyzer;
