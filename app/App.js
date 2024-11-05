import React, { useState, useEffect } from 'react';
import { View, Text, Button, TextInput, StyleSheet } from 'react-native';
import SoundRecorder from 'react-native-sound-recorder';
import Camera from 'react-native-camera';
import Geolocation from '@react-native-community/geolocation';
import GeminiAPI from './GeminiAPI'; // Replace with your actual Gemini API wrapper

const App = () => {
 const [recording, setRecording] = useState(false);
 const [animals, setAnimals] = useState([]);
 const [userInput, setUserInput] = useState('');
 const [location, setLocation] = useState(null);

  useEffect(() => {
    Geolocation.getCurrentPosition(position => {
      setLocation(position.coords);
    });
  }, []);

 const startRecording = async () => {
    try {
      await SoundRecorder.start();
      setRecording(true);
    } catch (error) {
      console.error(error);
    }
  };

 const stopRecording = async () => {
    try {
      const result = await SoundRecorder.stop();
      const response = await GeminiAPI.translateNatureSounds(result.path, location);
      setAnimals(prevAnimals => [...prevAnimals, response]);
      setRecording(false);
    } catch (error) {
      console.error(error);
    }
  };

 const translateUserInput = async () => {
    try {
      const response = await GeminiAPI.translateUserInput(userInput, animals[animals.length - 1].species);
      setUserInput('');
      // Play the translated sound using a library like react-native-sound
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <View style={styles.container}>
      <Camera style={styles.camera} ref={cam => (this.camera = cam)}>
        <View style={styles.buttonContainer}>
          <Button
            title={recording ? 'Stop Recording' : 'Start Recording'}
            onPress={recording ? stopRecording : startRecording}
          />
        </View>
      </Camera>

      <View style={styles.animalsContainer}>
        {animals.map(animal => (
          <Text key={animal.id} style={styles.animalText}>
            {animal.species}: {animal.translation}
          </Text>
        ))}
      </View>

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={userInput}
          onChangeText={setUserInput}
          placeholder="Talk to the animals..."
        />
        <Button title="Translate" onPress={translateUserInput} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  // Add your styles here
});

export default App;
