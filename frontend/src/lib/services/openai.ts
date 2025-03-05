import OpenAI from 'openai';

// Nutrition information extracted from user messages
export interface NutritionInfo {
  mealName: string; // Added meal name to group items
  foodItems: {
    name: string;
    calories: number;
    protein?: number;
    carbs?: number;
    fat?: number;
    fiber?: number;
    vitaminD?: number;
    iron?: number;
    calcium?: number;
    potassium?: number;
    water?: number;
  }[];
}

// Initialize the OpenAI client
const openai = new OpenAI({
  apiKey: import.meta.env.VITE_OPENAI_API_KEY,
  dangerouslyAllowBrowser: true // Required for client-side usage
});

// Function to send a chat message to OpenAI
export async function sendChatMessage(messages: OpenAI.Chat.ChatCompletionMessageParam[]): Promise<string> {
  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo',
      messages: messages,
      temperature: 0.7,
      max_tokens: 500
    });

    return response.choices[0].message.content || '';
  } catch (error) {
    console.error('Error calling OpenAI API:', error);
    throw error;
  }
}

// Function to extract nutrition information from a message
export async function extractNutritionInfo(userMessage: string): Promise<NutritionInfo | null> {
  try {
    const systemPrompt = `You are a nutrition analysis assistant. Extract nutritional information from the user's food description.
    Return ONLY a JSON object with the following structure, and nothing else:
    {
      "mealName": "descriptive meal name based on the items (e.g. Breakfast, Lunch, Snack, etc.)",
      "foodItems": [
        {
          "name": "food name",
          "calories": number,
          "protein": number (in grams),
          "carbs": number (in grams),
          "fat": number (in grams),
          "fiber": number (in grams),
          "vitaminD": number (in micrograms, optional),
          "iron": number (in mg, optional),
          "calcium": number (in mg, optional),
          "potassium": number (in mg, optional),
          "water": number (in liters, optional)
        }
      ]
    }`;

    const response = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userMessage }
      ],
      temperature: 0.3,
      max_tokens: 500,
      response_format: { type: 'json_object' }
    });

    const content = response.choices[0].message.content || '{"mealName": "Unknown Meal", "foodItems": []}';
    
    try {
      // Parse the JSON response
      const nutritionData = JSON.parse(content) as NutritionInfo;
      return nutritionData;
    } catch (parseError) {
      console.error('Error parsing nutrition data:', parseError);
      return null;
    }
  } catch (error) {
    console.error('Error extracting nutrition info:', error);
    return null;
  }
}
