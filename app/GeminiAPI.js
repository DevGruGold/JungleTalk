import axios from 'axios';

const API_KEY = 'AIzaSyD5JXbN1K8hvGFrI0-aNaM54uoEtoHeNh0';
const BASE_URL = 'https://your-gemini-api.com'; // Replace with the actual Gemini API base URL

const GeminiAPI = {
 translateNatureSounds: async (audioPath, location) => {
    try {
      const formData = new FormData();
      formData.append('audio', {
        uri: audioPath,
        name: 'nature-sound.wav',
        type: 'audio/wav',
      });
      formData.append('location', JSON.stringify(location));

      const response = await axios.post(
        `${BASE_URL}/translate-nature-sounds?key=${API_KEY}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      return response.data;
    } catch (error) {
      console.error(error);
      throw error;
    }
  },

 translateUserInput: async (userInput, species) => {
    try {
      const response = await axios.post(
        `${BASE_URL}/translate-user-input?key=${API_KEY}`,
        {
          userInput,
          species,
        }
      );

      return response.data;
    } catch (error) {
      console.error(error);
      throw error;
    }
  },
};

export default GeminiAPI;
