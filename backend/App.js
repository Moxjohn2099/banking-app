import React from 'react';
import { View, Text, StyleSheet, Button } from 'react-native';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export default function App() {
  const [message, setMessage] = React.useState('');

  const testAPI = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      setMessage(JSON.stringify(response.data, null, 2));
    } catch (error) {
      setMessage('Error connecting to API: ' + error.message);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🏦 Banking App</Text>
      <Text style={styles.subtitle}>React Native Frontend</Text>
      
      <Button title="Test API Connection" onPress={testAPI} />
      
      {message ? (
        <View style={styles.messageBox}>
          <Text style={styles.messageText}>{message}</Text>
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 30,
  },
  messageBox: {
    marginTop: 20,
    padding: 15,
    backgroundColor: 'white',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  messageText: {
    fontSize: 12,
    fontFamily: 'monospace',
  },
});