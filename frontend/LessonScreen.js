import React, { useEffect, useState, useRef } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, FlatList, KeyboardAvoidingView, Platform } from 'react-native';
import { Video, ResizeMode } from 'expo-av';
import { SafeAreaView } from 'react-native-safe-area-context';

const API_URL = 'http://localhost:8000';

export default function LessonScreen({ route, navigation }) {
  const { lessonId, title } = route.params;
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const flatListRef = useRef(null);

  useEffect(() => {
    navigation.setOptions({ title: title });
    startLesson();
  }, []);

  const startLesson = async () => {
    // Initial trigger to the AI
    // We don't have an explicit "start" endpoint that returns a message in the new plan,
    // but we can simulate it by sending an empty history or a specific "start" signal if we wanted.
    // However, our backend logic expects a history list.
    // Let's act as if the user just opened it. Ideally the AI should greet first.
    // We can handle this by sending a dummy user message "Start lesson" invisible to the user?
    // Or better, we just call the chat endpoint with empty history, but our backend expects a "last user message"
    // inside the history or separate.

    // Let's manually add a "system/initial" trigger.
    // Actually, the user usually says "Hi" or "I'm ready".
    // Let's auto-send "Hi, I'm ready to learn about this."

    const initialMsg = { role: 'user', text: "I'm ready to start this lesson." };
    setMessages([initialMsg]);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lesson_id: lessonId,
          history: [initialMsg]
        })
      });
      const data = await response.json();
      setMessages(prev => [...prev, data]);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputText.trim()) return;

    const userMsg = { role: 'user', text: inputText };
    setMessages(prev => [...prev, userMsg]);
    setInputText('');
    setLoading(true);

    try {
      // We send the FULL history including the new message
      const newHistory = [...messages, userMsg];

      const response = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lesson_id: lessonId,
          history: newHistory
        })
      });
      const data = await response.json();
      setMessages(prev => [...prev, data]);

      // Check if lesson is complete (simple heuristic: AI says "congratulations" or similar)
      // For now, let's just mark it complete if the user has exchanged > 5 messages or manually?
      // Or maybe the backend should signal it.
      // Let's just auto-mark progress after every interaction for MVP simplicity, or add a "Finish" button.
      // We'll add a "Complete Lesson" button in the header or at the bottom.

    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const markComplete = async () => {
      try {
        await fetch(`${API_URL}/progress`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: "user_1",
                lesson_id: lessonId,
                completed: true
            })
        });
        navigation.goBack();
      } catch (error) {
          console.error(error);
      }
  };

  const renderItem = ({ item }) => {
    const isUser = item.role === 'user';
    return (
      <View style={[styles.bubble, isUser ? styles.userBubble : styles.aiBubble]}>
        <Text style={[styles.text, isUser ? styles.userText : styles.aiText]}>{item.text}</Text>
        {item.video_url && (
          <Video
            style={styles.video}
            source={{ uri: item.video_url }}
            useNativeControls
            resizeMode={ResizeMode.CONTAIN}
            isLooping
          />
        )}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderItem}
        keyExtractor={(item, index) => index.toString()}
        contentContainerStyle={styles.list}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />

      {loading && <Text style={styles.typing}>AI is typing...</Text>}

      <View style={styles.inputContainer}>
        <TextInput
            style={styles.input}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Ask a question..."
            onSubmitEditing={sendMessage}
        />
        <TouchableOpacity onPress={sendMessage} style={styles.sendButton}>
            <Text style={styles.sendText}>Send</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.completeButton} onPress={markComplete}>
          <Text style={styles.completeText}>Mark Complete & Finish</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  list: {
    padding: 16,
  },
  bubble: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 16,
    marginBottom: 12,
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: '#4CAF50',
    borderBottomRightRadius: 4,
  },
  aiBubble: {
    alignSelf: 'flex-start',
    backgroundColor: 'white',
    borderBottomLeftRadius: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  text: {
    fontSize: 16,
    lineHeight: 22,
  },
  userText: {
    color: 'white',
  },
  aiText: {
    color: '#333',
  },
  video: {
    width: '100%',
    height: 150,
    marginTop: 8,
    borderRadius: 8,
    backgroundColor: 'black',
  },
  typing: {
    marginLeft: 20,
    marginBottom: 8,
    color: '#888',
    fontStyle: 'italic',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 12,
    backgroundColor: 'white',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#EEE',
  },
  input: {
    flex: 1,
    backgroundColor: '#F0F0F0',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginRight: 12,
    fontSize: 16,
  },
  sendButton: {
    paddingHorizontal: 12,
  },
  sendText: {
    color: '#4CAF50',
    fontWeight: 'bold',
    fontSize: 16,
  },
  completeButton: {
      backgroundColor: '#E8F5E9',
      padding: 12,
      alignItems: 'center',
      borderTopWidth: 1,
      borderTopColor: '#DDD'
  },
  completeText: {
      color: '#2E7D32',
      fontWeight: '600'
  }
});
