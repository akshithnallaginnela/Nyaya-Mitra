import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Input,
  Button,
  Text,
  Spinner,
  Container,
  Heading,
  Flex,
  Avatar,
  Badge,
  IconButton,
  Tooltip,
  Divider,
  Card,
  CardBody,
} from '@chakra-ui/react';
import { ArrowForwardIcon } from '@chakra-ui/icons';
import api from '../api/axios';
import { useAuth } from '../contexts/AuthContext';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: any[];
  confidence_score?: number;
  timestamp?: Date;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input, timestamp: new Date() };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.post('/chat/query', { query: input });
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
        citations: response.data.citations,
        confidence_score: response.data.confidence_score,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      console.error('Chat error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Flex direction="column" h="calc(100vh - 60px)" bg="gray.50">
      {/* Header */}
      <Box bg="white" px={6} py={3} borderBottom="1px" borderColor="gray.200" boxShadow="sm">
        <HStack>
          <Text fontSize="xl">💬</Text>
          <Heading size="sm" color="gray.700">Legal Chat Assistant</Heading>
          <Badge colorScheme="green" ml={2}>AI Powered</Badge>
        </HStack>
      </Box>

      {/* Messages Area */}
      <Box flex={1} overflowY="auto" px={{ base: 4, md: 8 }} py={4}>
        <Container maxW="4xl">
          {messages.length === 0 && (
            <VStack spacing={6} py={12} textAlign="center">
              <Text fontSize="5xl">⚖️</Text>
              <Heading size="md" color="gray.600">
                How can I help you today?
              </Heading>
              <Text color="gray.500" maxW="md">
                Ask me about Indian legal rights, procedures, FIR filing, 
                constitutional rights, or any legal question you have.
              </Text>
              <HStack spacing={3} flexWrap="wrap" justify="center">
                {[
                  'What are my rights if falsely accused?',
                  'How to file an FIR?',
                  'What is Section 498A IPC?',
                ].map((suggestion) => (
                  <Button
                    key={suggestion}
                    size="sm"
                    variant="outline"
                    colorScheme="brand"
                    borderRadius="full"
                    onClick={() => {
                      setInput(suggestion);
                    }}
                  >
                    {suggestion}
                  </Button>
                ))}
              </HStack>
            </VStack>
          )}

          <VStack spacing={4} align="stretch">
            {messages.map((msg, idx) => (
              <Flex
                key={idx}
                justify={msg.role === 'user' ? 'flex-end' : 'flex-start'}
              >
                <HStack
                  align="start"
                  maxW="80%"
                  flexDir={msg.role === 'user' ? 'row-reverse' : 'row'}
                  spacing={3}
                >
                  <Avatar
                    size="sm"
                    name={msg.role === 'user' ? user?.full_name : 'Nyaya Mitra'}
                    bg={msg.role === 'user' ? 'brand.500' : 'green.500'}
                    color="white"
                    mt={1}
                  />
                  <Box
                    bg={msg.role === 'user' ? 'brand.500' : 'white'}
                    color={msg.role === 'user' ? 'white' : 'gray.800'}
                    px={4}
                    py={3}
                    borderRadius="xl"
                    borderTopRightRadius={msg.role === 'user' ? '4px' : 'xl'}
                    borderTopLeftRadius={msg.role === 'user' ? 'xl' : '4px'}
                    boxShadow="sm"
                    borderWidth={msg.role === 'assistant' ? '1px' : '0'}
                    borderColor="gray.200"
                  >
                    <Text whiteSpace="pre-wrap" lineHeight="tall" fontSize="sm">
                      {msg.content}
                    </Text>
                    {msg.confidence_score != null && (
                      <HStack mt={2} pt={2} borderTop="1px" borderColor="gray.100">
                        <Badge
                          colorScheme={msg.confidence_score > 0.7 ? 'green' : msg.confidence_score > 0.4 ? 'yellow' : 'red'}
                          fontSize="xs"
                          borderRadius="full"
                        >
                          Confidence: {(msg.confidence_score * 100).toFixed(0)}%
                        </Badge>
                      </HStack>
                    )}
                    {msg.citations && msg.citations.length > 0 && (
                      <Box mt={2} pt={2} borderTop="1px" borderColor="gray.100">
                        <Text fontSize="xs" fontWeight="600" color={msg.role === 'user' ? 'whiteAlpha.800' : 'gray.500'} mb={1}>
                          📚 Sources:
                        </Text>
                        {msg.citations.map((c: any, i: number) => (
                          <Text key={i} fontSize="xs" color={msg.role === 'user' ? 'whiteAlpha.700' : 'gray.500'}>
                            • {c.source || c.title || c}
                          </Text>
                        ))}
                      </Box>
                    )}
                  </Box>
                </HStack>
              </Flex>
            ))}
            {loading && (
              <Flex justify="flex-start">
                <HStack align="start" spacing={3}>
                  <Avatar size="sm" name="Nyaya Mitra" bg="green.500" color="white" mt={1} />
                  <Box bg="white" px={4} py={3} borderRadius="xl" boxShadow="sm" borderWidth="1px" borderColor="gray.200">
                    <HStack spacing={2}>
                      <Spinner size="sm" color="brand.500" />
                      <Text fontSize="sm" color="gray.500">Thinking...</Text>
                    </HStack>
                  </Box>
                </HStack>
              </Flex>
            )}
            <div ref={messagesEndRef} />
          </VStack>
        </Container>
      </Box>

      {/* Input Area */}
      <Box bg="white" px={{ base: 4, md: 8 }} py={4} borderTop="1px" borderColor="gray.200" boxShadow="0 -2px 10px rgba(0,0,0,0.05)">
        <Container maxW="4xl">
          <HStack spacing={3}>
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Type your legal question here..."
              size="lg"
              bg="gray.50"
              borderRadius="xl"
              borderColor="gray.300"
              _focus={{ borderColor: 'brand.500', bg: 'white' }}
              _hover={{ borderColor: 'brand.300' }}
            />
            <IconButton
              aria-label="Send message"
              icon={<ArrowForwardIcon />}
              onClick={sendMessage}
              colorScheme="brand"
              size="lg"
              borderRadius="xl"
              isLoading={loading}
            />
          </HStack>
          <Text fontSize="xs" color="gray.400" mt={2} textAlign="center">
            Nyaya Mitra provides general legal information, not legal advice. Consult a lawyer for specific cases.
          </Text>
        </Container>
      </Box>
    </Flex>
  );
};

export default Chat;
