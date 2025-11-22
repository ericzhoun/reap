import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View, FlatList, TouchableOpacity, ActivityIndicator } from 'react-native';

const API_URL = 'http://localhost:8000';

export default function TopicScreen({ route, navigation }) {
  const { topicId, title } = route.params;
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    navigation.setOptions({ title: title });
    fetchLessons();
  }, []);

  const fetchLessons = async () => {
    try {
      const response = await fetch(`${API_URL}/topics/${topicId}/lessons`);
      const data = await response.json();
      setLessons(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const renderLesson = ({ item, index }) => {
    const isLocked = index > 0 && !lessons[index - 1].completed && !item.completed;
    // Simple logic: unlocked if previous is completed OR it's the first one.
    // Actually better logic: Find first uncompleted lesson. All after that are locked.
    // Let's just make it clickable for MVP.

    return (
      <TouchableOpacity
        style={[styles.card, item.completed && styles.completedCard]}
        onPress={() => navigation.navigate('Lesson', { lessonId: item.id, title: item.title })}
        disabled={false} // Enable all for testing
      >
        <View style={[styles.circle, item.completed ? styles.completedCircle : styles.activeCircle]}>
           <Text style={styles.circleText}>{index + 1}</Text>
        </View>
        <View style={styles.textContainer}>
          <Text style={styles.title}>{item.title}</Text>
          {item.completed && <Text style={styles.status}>Completed</Text>}
        </View>
      </TouchableOpacity>
    );
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#4CAF50" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={lessons}
        renderItem={renderLesson}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  list: {
    padding: 20,
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  completedCard: {
    backgroundColor: '#F1F8E9',
  },
  circle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  activeCircle: {
    backgroundColor: '#E0E0E0',
  },
  completedCircle: {
    backgroundColor: '#4CAF50',
  },
  circleText: {
    fontWeight: 'bold',
    color: '#555',
  },
  textContainer: {
    flex: 1,
  },
  title: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
  },
  status: {
    fontSize: 12,
    color: '#4CAF50',
    marginTop: 4,
  },
});
