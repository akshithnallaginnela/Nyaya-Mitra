import React, { useState, useEffect } from 'react';
import { Box, VStack, HStack, Input, Button, Text, Spinner } from '@chakra-ui/react';
import api from '../api/axios';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: any[];
  confidence_score?: number;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userMessage: Message = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.post('/chat/query', { query: input });
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
        citations: response.data.citations,
        confidence_score: response.data.confidence_score,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={8} h="100vh" display="flex" flexDirection="column">
      <VStack flex={1} overflowY="auto" spacing={4} align="stretch" mb={4}>
        {messages.map((msg, idx) => (
          <Box
            key={idx}
            alignSelf={msg.role === 'user' ? 'flex-end' : 'flex-start'}
            bg={msg.role === 'user' ? 'blue.100' : 'gray.100'}
            p={4}
            borderRadius="lg"
            maxW="70%"
          >
            <Text>{msg.content}</Text>
            {msg.confidence_score && (
              <Text fontSize="sm" color="gray.600" mt={2}>
                Confidence: {(msg.confidence_score * 100).toFixed(0)}%
              </Text>
            )}
          </Box>
        ))}
        {loading && <Spinner />}
      </VStack>
      <HStack>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask a legal question..."
        />
        <Button onClick={sendMessage} colorScheme="blue" isLoading={loading}>
          Send
        </Button>
      </HStack>
    </Box>
  );
};

export default Chat;
