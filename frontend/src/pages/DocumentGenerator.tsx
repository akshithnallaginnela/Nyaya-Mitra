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
import { useLanguage } from '../contexts/LanguageContext';

interface TemplateField {
  name: string;
  label: string;
  field_type: string;
  required: boolean;
  description: string;
  placeholder: string;
}

interface Template {
  document_type: string;
  name: string;
  description: string;
  category: string;
  fields: TemplateField[];
  attachment_summary: any;
}

const DocumentGenerator: React.FC = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [inputs, setInputs] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [generatedDoc, setGeneratedDoc] = useState<string | null>(null);
  const toast = useToast();
  const { t, language } = useLanguage();

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await api.get('/documents/templates');
      // Backend returns List[TemplateResponse] directly (not wrapped in { templates: [] })
      const data = Array.isArray(response.data) ? response.data : response.data.templates || [];
      setTemplates(data);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const getSelectedTemplateConfig = (): Template | undefined => {
    return templates.find(t => t.document_type === selectedTemplate);
  };

  const generateDocument = async () => {
    if (!selectedTemplate) {
      toast({ title: 'Please select a document type', status: 'warning', duration: 3000 });
      return;
    }
    setLoading(true);
    try {
      const response = await api.post('/documents/generate', {
        document_type: selectedTemplate,
        inputs,
      });
      setGeneratedDoc(response.data.text_content || response.data.content || JSON.stringify(response.data, null, 2));
      toast({
        title: 'Document generated successfully!',
        description: 'Your document is ready below',
        status: 'success',
        duration: 3000,
      });
    } catch (error: any) {
      const detail = error?.response?.data?.detail || 'Please fill all required fields and try again';
      toast({
        title: 'Generation failed',
        description: detail,
        status: 'error',
        duration: 5000,
      });
    } finally {
      setLoading(false);
    }
  };

  const selectedConfig = getSelectedTemplateConfig();

  return (
    <Box bg="gray.50" minH="calc(100vh - 60px)" py={8}>
      <Container maxW="4xl">
        <HStack mb={6}>
          <Text fontSize="3xl">📄</Text>
          <VStack align="start" spacing={0}>
            <Heading size="lg" color="gray.800">{t('document_generator', 'Document Generator')}</Heading>
            <Text color="gray.600" fontSize="sm">
              Generate legal documents from professional templates
            </Text>
          </VStack>
        </HStack>

        <Card borderRadius="xl" boxShadow="md" mb={6}>
          <CardBody p={6}>
            <VStack spacing={5} align="stretch">
              <FormControl>
                <FormLabel fontWeight="600" color="gray.700">📑 {t('select_template', 'Document Type')}</FormLabel>
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
                  {templates.map((tmpl) => (
                    <option key={tmpl.document_type} value={tmpl.document_type}>
                      {tmpl.name}
                    </option>
                  ))}
                </Select>
              </FormControl>

              {selectedConfig && (
                <>
                  <Box bg="blue.50" p={3} borderRadius="lg">
                    <Text fontSize="sm" color="blue.700">{selectedConfig.description}</Text>
                  </Box>
                  <Divider />
                  <Text fontWeight="600" color="gray.700">Fill in the details:</Text>

                  {selectedConfig.fields.map((field) => (
                    <FormControl key={field.name} isRequired={field.required}>
                      <FormLabel fontSize="sm" fontWeight="600" color="gray.600">
                        {field.label} {field.required && <Text as="span" color="red.400">*</Text>}
                      </FormLabel>
                      {field.field_type === 'textarea' ? (
                        <Textarea
                          value={inputs[field.name] || ''}
                          onChange={(e) => setInputs({ ...inputs, [field.name]: e.target.value })}
                          placeholder={field.placeholder || field.description}
                          rows={4}
                          bg="gray.50"
                          borderRadius="xl"
                          _focus={{ bg: 'white' }}
                        />
                      ) : field.field_type === 'date' ? (
                        <Input
                          type="date"
                          value={inputs[field.name] || ''}
                          onChange={(e) => setInputs({ ...inputs, [field.name]: e.target.value })}
                          bg="gray.50"
                          borderRadius="xl"
                          _focus={{ bg: 'white' }}
                        />
                      ) : (
                        <Input
                          value={inputs[field.name] || ''}
                          onChange={(e) => setInputs({ ...inputs, [field.name]: e.target.value })}
                          placeholder={field.placeholder || field.description}
                          bg="gray.50"
                          borderRadius="xl"
                          _focus={{ bg: 'white' }}
                        />
                      )}
                      {field.description && field.description !== field.placeholder && (
                        <Text fontSize="xs" color="gray.500" mt={1}>{field.description}</Text>
                      )}
                    </FormControl>
                  ))}

                  <Button
                    onClick={generateDocument}
                    colorScheme="brand"
                    isLoading={loading}
                    loadingText="Generating..."
                    size="lg"
                    borderRadius="xl"
                    fontWeight="700"
                  >
                    📄 {t('generate_document', 'Generate Document')}
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
