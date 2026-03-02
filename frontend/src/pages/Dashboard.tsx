import React from 'react';
import { Box, Heading, SimpleGrid, Card, CardBody, Text, Button } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const features = [
    { title: 'Legal Chat', path: '/chat', description: 'Ask legal questions' },
    { title: 'Case Analyzer', path: '/case-analyzer', description: 'Analyze complaint validity' },
    { title: 'Document Generator', path: '/documents', description: 'Generate legal documents' },
    { title: 'Legal Aid Search', path: '/legal-aid', description: 'Find free legal help' },
    { title: 'Evidence Guide', path: '/evidence', description: 'Learn to collect evidence' },
    { title: 'Emergency SOS', path: '/emergency', description: 'Emergency contacts' },
  ];

  return (
    <Box p={8}>
      <Heading mb={6}>Welcome, {user?.full_name}</Heading>
      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
        {features.map((feature) => (
          <Card key={feature.path} cursor="pointer" onClick={() => navigate(feature.path)}>
            <CardBody>
              <Heading size="md" mb={2}>{feature.title}</Heading>
              <Text mb={4}>{feature.description}</Text>
              <Button colorScheme="blue" size="sm">Open</Button>
            </CardBody>
          </Card>
        ))}
      </SimpleGrid>
    </Box>
  );
};

export default Dashboard;
