import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  Select,
  FormControl,
  FormLabel,
  Input,
  Button,
  Heading,
  useToast,
  Container,
  Card,
  CardBody,
  HStack,
  Text,
  Textarea,
  Badge,
  Divider,
} from '@chakra-ui/react';
import api from '../api/axios';

const DocumentGenerator: React.FC = () => {
  const [templates, setTemplates] = useState<string[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [inputs, setInputs] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [generatedDoc, setGeneratedDoc] = useState<string | null>(null);
  const toast = useToast();

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await api.get('/documents/templates');
      setTemplates(response.data.templates || []);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const generateDocument = async () => {
    if (!selectedTemplate) {
      toast({ title: 'Please select a document type', status: 'warning', duration: 3000 });
      return;
    }
    setLoading(true);
    try {
      const response = await api.post('/documents/generate', {
        template_type: selectedTemplate,
        inputs,
      });
      setGeneratedDoc(response.data.content || response.data.document || JSON.stringify(response.data, null, 2));
      toast({
        title: 'Document generated successfully!',
        description: 'Your document is ready below',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Generation failed',
        description: 'Please fill all required fields and try again',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const templateLabels: Record<string, string> = {
    legal_letter: '📧 Legal Notice / Letter',
    counter_petition: '📜 Counter Petition',
    complaint: '📝 Formal Complaint',
    affidavit: '📋 Affidavit',
  };

  return (
    <Box bg="gray.50" minH="calc(100vh - 60px)" py={8}>
      <Container maxW="4xl">
        <HStack mb={6}>
          <Text fontSize="3xl">📄</Text>
          <VStack align="start" spacing={0}>
            <Heading size="lg" color="gray.800">Document Generator</Heading>
            <Text color="gray.600" fontSize="sm">
              Generate legal documents from professional templates
            </Text>
          </VStack>
        </HStack>

        <Card borderRadius="xl" boxShadow="md" mb={6}>
          <CardBody p={6}>
            <VStack spacing={5} align="stretch">
              <FormControl>
                <FormLabel fontWeight="600" color="gray.700">📑 Document Type</FormLabel>
                <Select
                  value={selectedTemplate}
                  onChange={(e) => {
                    setSelectedTemplate(e.target.value);
                    setInputs({});
                    setGeneratedDoc(null);
                  }}
                  placeholder="Select document type"
                  size="lg"
                  bg="gray.50"
                  borderRadius="xl"
                  _focus={{ bg: 'white' }}
                >
                  {templates.map((template) => (
                    <option key={template} value={template}>
                      {templateLabels[template] || template}
                    </option>
                  ))}
                </Select>
              </FormControl>

              {selectedTemplate && (
                <>
                  <Divider />
                  <Text fontWeight="600" color="gray.700">Fill in the details:</Text>

                  <FormControl>
                    <FormLabel fontSize="sm" fontWeight="600" color="gray.600">Your Full Name</FormLabel>
                    <Input
                      value={inputs.name || ''}
                      onChange={(e) => setInputs({ ...inputs, name: e.target.value })}
                      placeholder="Enter your full name"
                      bg="gray.50"
                      borderRadius="xl"
                      _focus={{ bg: 'white' }}
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel fontSize="sm" fontWeight="600" color="gray.600">Recipient / Authority Name</FormLabel>
                    <Input
                      value={inputs.recipient || ''}
                      onChange={(e) => setInputs({ ...inputs, recipient: e.target.value })}
                      placeholder="Name of the person or authority"
                      bg="gray.50"
                      borderRadius="xl"
                      _focus={{ bg: 'white' }}
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel fontSize="sm" fontWeight="600" color="gray.600">Subject</FormLabel>
                    <Input
                      value={inputs.subject || ''}
                      onChange={(e) => setInputs({ ...inputs, subject: e.target.value })}
                      placeholder="Subject of the document"
                      bg="gray.50"
                      borderRadius="xl"
                      _focus={{ bg: 'white' }}
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel fontSize="sm" fontWeight="600" color="gray.600">Details / Content</FormLabel>
                    <Textarea
                      value={inputs.details || ''}
                      onChange={(e) => setInputs({ ...inputs, details: e.target.value })}
                      placeholder="Describe the details of your case or request..."
                      rows={4}
                      bg="gray.50"
                      borderRadius="xl"
                      _focus={{ bg: 'white' }}
                    />
                  </FormControl>

                  <Button
                    onClick={generateDocument}
                    colorScheme="brand"
                    isLoading={loading}
                    loadingText="Generating..."
                    size="lg"
                    borderRadius="xl"
                    fontWeight="700"
                  >
                    📄 Generate Document
                  </Button>
                </>
              )}
            </VStack>
          </CardBody>
        </Card>

        {generatedDoc && (
          <Card borderRadius="xl" boxShadow="lg" borderTop="4px solid" borderTopColor="green.400">
            <CardBody p={6}>
              <HStack justify="space-between" mb={4}>
                <Heading size="md" color="gray.800">Generated Document</Heading>
                <Badge colorScheme="green" fontSize="sm" px={3} py={1} borderRadius="full">
                  ✅ Ready
                </Badge>
              </HStack>
              <Box
                bg="gray.50"
                p={6}
                borderRadius="lg"
                whiteSpace="pre-wrap"
                fontFamily="mono"
                fontSize="sm"
                lineHeight="tall"
                borderWidth="1px"
                borderColor="gray.200"
              >
                {generatedDoc}
              </Box>
              <Button
                mt={4}
                size="sm"
                variant="outline"
                colorScheme="brand"
                onClick={() => {
                  navigator.clipboard.writeText(generatedDoc);
                  toast({ title: 'Copied to clipboard!', status: 'success', duration: 2000 });
                }}
              >
                📋 Copy to Clipboard
              </Button>
            </CardBody>
          </Card>
        )}
      </Container>
    </Box>
  );
};

export default DocumentGenerator;
