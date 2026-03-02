import React from 'react';
import {
  Box,
  Heading,
  SimpleGrid,
  Card,
  CardBody,
  Text,
  Button,
  VStack,
  HStack,
  Badge,
  Container,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { t } = useLanguage();

  const features = [
    {
      title: t('chat_title', 'Legal Chat'),
      path: '/chat',
      description: t('chat_placeholder', 'Get instant AI-powered answers to your legal questions with citations from Indian law.'),
      icon: '💬',
      color: 'blue',
      badge: 'AI',
    },
    {
      title: t('case_analysis', 'Case Analyzer'),
      path: '/case-analyzer',
      description: t('validity_score', 'Analyze the validity of a complaint or case with a detailed breakdown and score.'),
      icon: '🔍',
      color: 'purple',
      badge: t('case_analysis', 'Analysis'),
    },
    {
      title: t('document_generator', 'Document Generator'),
      path: '/documents',
      description: t('generate_document', 'Generate legal documents like counter-petitions and legal letters from templates.'),
      icon: '📄',
      color: 'green',
      badge: t('select_template', 'Templates'),
    },
    {
      title: t('legal_aid', 'Legal Aid'),
      path: '/legal-aid',
      description: t('find_legal_aid', 'Find free legal aid providers, NGOs, and legal clinics near you across India.'),
      icon: '⚖️',
      color: 'orange',
      badge: t('search', 'Directory'),
    },
    {
      title: t('evidence_guide', 'Evidence Guide'),
      path: '/evidence',
      description: t('collect_evidence', 'Learn how to properly collect, preserve, and document evidence for your case.'),
      icon: '📋',
      color: 'teal',
      badge: t('evidence_guide', 'Guide'),
    },
    {
      title: t('emergency', 'Emergency SOS'),
      path: '/emergency',
      description: t('emergency_contacts', 'Quick access to emergency helpline numbers, police, and women\'s helplines.'),
      icon: '🚨',
      color: 'red',
      badge: t('emergency', 'Urgent'),
    },
  ];

  return (
    <Box bg="gray.50" minH="calc(100vh - 60px)">
      {/* Hero Section */}
      <Box
        bgGradient="linear(to-br, brand.600, brand.800)"
        color="white"
        py={{ base: 8, md: 12 }}
        px={8}
      >
        <Container maxW="6xl">
          <VStack align="start" spacing={3}>
            <Heading size={{ base: 'lg', md: 'xl' }}>
              {t('welcome', 'Welcome to Nyaya Mitra')}, {user?.full_name || 'Student'} 👋
            </Heading>
            <Text fontSize={{ base: 'md', md: 'lg' }} opacity={0.9} maxW="2xl">
              Your AI-powered legal companion. Get guidance on legal rights, 
              analyze cases, generate documents, and find legal aid — all in one place.
            </Text>
            {user?.college_name && (
              <Badge colorScheme="whiteAlpha" fontSize="sm" px={3} py={1} borderRadius="full">
                🎓 {user.college_name}
              </Badge>
            )}
          </VStack>
        </Container>
      </Box>

      {/* Features Grid */}
      <Container maxW="6xl" py={8}>
        <Heading size="md" mb={6} color="gray.700">
          What would you like to do today?
        </Heading>
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
          {features.map((feature) => (
            <Card
              key={feature.path}
              cursor="pointer"
              onClick={() => navigate(feature.path)}
              bg="white"
              borderLeft="4px solid"
              borderLeftColor={`${feature.color}.400`}
              _hover={{
                transform: 'translateY(-4px)',
                boxShadow: 'xl',
                borderLeftColor: `${feature.color}.600`,
              }}
              transition="all 0.2s"
            >
              <CardBody>
                <HStack justify="space-between" mb={3}>
                  <Text fontSize="3xl">{feature.icon}</Text>
                  <Badge colorScheme={feature.color} fontSize="xs" px={2} py={0.5} borderRadius="full">
                    {feature.badge}
                  </Badge>
                </HStack>
                <Heading size="md" mb={2} color="gray.800">
                  {feature.title}
                </Heading>
                <Text color="gray.600" fontSize="sm" mb={4} lineHeight="tall">
                  {feature.description}
                </Text>
                <Button
                  size="sm"
                  colorScheme={feature.color}
                  variant="outline"
                  borderRadius="lg"
                >
                  Open →
                </Button>
              </CardBody>
            </Card>
          ))}
        </SimpleGrid>

        {/* Quick Info */}
        <Box mt={8} p={6} bg="white" borderRadius="xl" boxShadow="sm" borderWidth="1px">
          <HStack spacing={8} flexWrap="wrap" justify="center">
            <VStack>
              <Text fontSize="2xl">🔒</Text>
              <Text fontSize="sm" color="gray.600" fontWeight="600">End-to-End Encrypted</Text>
            </VStack>
            <VStack>
              <Text fontSize="2xl">🇮🇳</Text>
              <Text fontSize="sm" color="gray.600" fontWeight="600">Indian Law Focused</Text>
            </VStack>
            <VStack>
              <Text fontSize="2xl">🌐</Text>
              <Text fontSize="sm" color="gray.600" fontWeight="600">7 Languages Supported</Text>
            </VStack>
            <VStack>
              <Text fontSize="2xl">🤖</Text>
              <Text fontSize="sm" color="gray.600" fontWeight="600">AI-Powered Analysis</Text>
            </VStack>
          </HStack>
        </Box>
      </Container>
    </Box>
  );
};

export default Dashboard;
