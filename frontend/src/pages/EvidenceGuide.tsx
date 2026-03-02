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
  Divider,
  SimpleGrid,
  Tag,
  TagLabel,
  Wrap,
  WrapItem,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  UnorderedList,
} from '@chakra-ui/react';
import { CheckCircleIcon, WarningIcon } from '@chakra-ui/icons';
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
              <Box>
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
              </Box>

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
            {/* Title and Description */}
            {guide.title && (
              <Card borderRadius="xl" boxShadow="md" bg="teal.50">
                <CardBody p={5}>
                  <Heading size="md" color="teal.800" mb={2}>{guide.title}</Heading>
                  {guide.description && <Text color="teal.700" fontSize="sm">{guide.description}</Text>}
                </CardBody>
              </Card>
            )}

            {/* Tampering Warning */}
            {guide.tampering_warning && (
              <Alert
                status="error"
                borderRadius="xl"
                flexDirection="column"
                alignItems="flex-start"
                p={5}
              >
                <HStack mb={2}>
                  <AlertIcon />
                  <AlertTitle fontWeight="700">{guide.tampering_warning.title || 'Evidence Tampering Warning'}</AlertTitle>
                </HStack>
                {guide.tampering_warning.content && guide.tampering_warning.content.map((item: string, idx: number) => (
                  <AlertDescription key={idx} color="gray.700" lineHeight="tall" display="block" mb={1}>
                    • {item}
                  </AlertDescription>
                ))}
                {guide.tampering_warning.legal_consequences && (
                  <Text mt={2} fontWeight="600" color="red.700" fontSize="sm">
                    ⚖️ {guide.tampering_warning.legal_consequences}
                  </Text>
                )}
              </Alert>
            )}

            {/* Case-Specific Guidance */}
            {guide.case_specific_guidance && (
              <Card borderRadius="xl" boxShadow="md" borderTop="4px solid" borderTopColor="purple.400">
                <CardBody p={6}>
                  <Heading size="md" color="gray.800" mb={4}>🎯 Case-Specific Guidance</Heading>
                  
                  {guide.case_specific_guidance.key_evidence_types?.length > 0 && (
                    <Box mb={4}>
                      <Text fontWeight="600" color="purple.700" mb={2}>Key Evidence Types</Text>
                      <Wrap>
                        {guide.case_specific_guidance.key_evidence_types.map((type: string, idx: number) => (
                          <WrapItem key={idx}>
                            <Tag size="md" colorScheme="purple" borderRadius="full">
                              <TagLabel>{type}</TagLabel>
                            </Tag>
                          </WrapItem>
                        ))}
                      </Wrap>
                    </Box>
                  )}

                  {guide.case_specific_guidance.specific_instructions?.length > 0 && (
                    <Box mb={4}>
                      <Text fontWeight="600" color="blue.700" mb={2}>Specific Instructions</Text>
                      <List spacing={2}>
                        {guide.case_specific_guidance.specific_instructions.map((inst: string, idx: number) => (
                          <ListItem key={idx} display="flex" alignItems="flex-start">
                            <ListIcon as={CheckCircleIcon} color="blue.500" mt={1} />
                            <Text fontSize="sm" color="gray.700">{inst}</Text>
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  {guide.case_specific_guidance.relevant_laws?.length > 0 && (
                    <Box>
                      <Text fontWeight="600" color="green.700" mb={2}>📚 Relevant Laws</Text>
                      <Wrap>
                        {guide.case_specific_guidance.relevant_laws.map((law: string, idx: number) => (
                          <WrapItem key={idx}>
                            <Tag size="sm" colorScheme="green" borderRadius="full">
                              <TagLabel>{law}</TagLabel>
                            </Tag>
                          </WrapItem>
                        ))}
                      </Wrap>
                    </Box>
                  )}
                </CardBody>
              </Card>
            )}

            {/* Step-by-Step Instructions */}
            {guide.step_by_step_instructions?.length > 0 && (
              <Card borderRadius="xl" boxShadow="lg" borderTop="4px solid" borderTopColor="teal.400">
                <CardBody p={6}>
                  <HStack justify="space-between" mb={4}>
                    <Heading size="md" color="gray.800">
                      {t('collect_evidence', 'Evidence Collection Steps')}
                    </Heading>
                    <Badge colorScheme="teal" fontSize="sm" px={3} py={1} borderRadius="full">
                      {guide.step_by_step_instructions.length} Steps
                    </Badge>
                  </HStack>

                  <Accordion allowMultiple defaultIndex={[0]}>
                    {guide.step_by_step_instructions.map((step: any, idx: number) => (
                      <AccordionItem key={idx} border="none" mb={2}>
                        <AccordionButton
                          bg="gray.50"
                          borderRadius="lg"
                          _expanded={{ bg: 'teal.50' }}
                          _hover={{ bg: 'gray.100' }}
                          p={4}
                        >
                          <HStack flex={1} textAlign="left" spacing={3}>
                            <Badge colorScheme="teal" borderRadius="full" px={3} py={1} fontSize="sm">
                              {step.step_number}
                            </Badge>
                            <Text fontWeight="600" color="gray.800">{step.title}</Text>
                          </HStack>
                          <AccordionIcon />
                        </AccordionButton>
                        <AccordionPanel pb={4} px={4}>
                          <Text color="gray.700" mb={3} lineHeight="tall">{step.instruction}</Text>
                          {step.details?.length > 0 && (
                            <List spacing={2}>
                              {step.details.map((detail: string, dIdx: number) => (
                                <ListItem key={dIdx} display="flex" alignItems="flex-start" fontSize="sm">
                                  <ListIcon as={CheckCircleIcon} color="green.500" mt={1} />
                                  <Text color="gray.600">{detail}</Text>
                                </ListItem>
                              ))}
                            </List>
                          )}
                        </AccordionPanel>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </CardBody>
              </Card>
            )}

            {/* Digital Preservation */}
            {guide.digital_preservation && (
              <Card borderRadius="xl" boxShadow="md">
                <CardBody p={5}>
                  <Text fontWeight="700" mb={3} color="blue.700">💾 {guide.digital_preservation.title || 'Digital Preservation'}</Text>
                  {guide.digital_preservation.instructions?.map((inst: string, idx: number) => (
                    <Text key={idx} fontSize="sm" color="gray.700" mb={1}>• {inst}</Text>
                  ))}
                  {guide.digital_preservation.best_practices?.length > 0 && (
                    <Box mt={3}>
                      <Text fontWeight="600" fontSize="sm" color="gray.600" mb={1}>Best Practices:</Text>
                      {guide.digital_preservation.best_practices.map((bp: string, idx: number) => (
                        <Text key={idx} fontSize="sm" color="gray.600" mb={1}>✔ {bp}</Text>
                      ))}
                    </Box>
                  )}
                </CardBody>
              </Card>
            )}

            {/* Admissibility Requirements */}
            {guide.admissibility_requirements && (
              <Card borderRadius="xl" boxShadow="md" bg="yellow.50">
                <CardBody p={5}>
                  <Text fontWeight="700" mb={3} color="orange.700">📜 {guide.admissibility_requirements.title || 'Admissibility Requirements'}</Text>
                  {guide.admissibility_requirements.content?.map((c: string, idx: number) => (
                    <Text key={idx} fontSize="sm" color="gray.700" mb={1}>• {c}</Text>
                  ))}
                  {guide.admissibility_requirements.key_laws?.length > 0 && (
                    <Box mt={2}>
                      <Wrap>
                        {guide.admissibility_requirements.key_laws.map((law: string, idx: number) => (
                          <WrapItem key={idx}>
                            <Tag size="sm" colorScheme="orange" borderRadius="full"><TagLabel>{law}</TagLabel></Tag>
                          </WrapItem>
                        ))}
                      </Wrap>
                    </Box>
                  )}
                </CardBody>
              </Card>
            )}
          </VStack>
        )}
      </Container>
    </Box>
  );
};

export default EvidenceGuide;
