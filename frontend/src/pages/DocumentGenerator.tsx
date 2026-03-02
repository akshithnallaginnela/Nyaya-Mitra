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
} from '@chakra-ui/react';
import api from '../api/axios';

const DocumentGenerator: React.FC = () => {
  const [templates, setTemplates] = useState<string[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [inputs, setInputs] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
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
    setLoading(true);
    try {
      const response = await api.post('/documents/generate', {
        template_type: selectedTemplate,
        inputs,
      });
      toast({
        title: 'Document generated',
        description: 'Your document is ready for download',
        status: 'success',
        duration: 3000,
      });
      // Download logic here
    } catch (error) {
      toast({
        title: 'Generation failed',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={8} maxW="4xl" mx="auto">
      <Heading mb={6}>Document Generator</Heading>
      <VStack spacing={4} align="stretch">
        <FormControl>
          <FormLabel>Document Type</FormLabel>
          <Select
            value={selectedTemplate}
            onChange={(e) => setSelectedTemplate(e.target.value)}
            placeholder="Select document type"
          >
            {templates.map((template) => (
              <option key={template} value={template}>
                {template}
              </option>
            ))}
          </Select>
        </FormControl>

        {selectedTemplate && (
          <>
            <FormControl>
              <FormLabel>Your Name</FormLabel>
              <Input
                value={inputs.name || ''}
                onChange={(e) => setInputs({ ...inputs, name: e.target.value })}
              />
            </FormControl>
            <FormControl>
              <FormLabel>Recipient Name</FormLabel>
              <Input
                value={inputs.recipient || ''}
                onChange={(e) => setInputs({ ...inputs, recipient: e.target.value })}
              />
            </FormControl>
            <FormControl>
              <FormLabel>Subject</FormLabel>
              <Input
                value={inputs.subject || ''}
                onChange={(e) => setInputs({ ...inputs, subject: e.target.value })}
              />
            </FormControl>
            <Button onClick={generateDocument} colorScheme="blue" isLoading={loading}>
              Generate Document
            </Button>
          </>
        )}
      </VStack>
    </Box>
  );
};

export default DocumentGenerator;
