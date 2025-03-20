import { createClient } from '@supabase/supabase-js'

// Get Supabase URL and anon key from environment variables
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_KEY

console.log('Initializing Supabase client with:', {
  url: supabaseUrl,
  hasKey: !!supabaseAnonKey,
  // Show the actual URL and first few characters of the key for debugging
  actualUrl: supabaseUrl,
  keyPrefix: supabaseAnonKey ? supabaseAnonKey.substring(0, 5) + '...' : 'missing'
});

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Supabase URL or key is missing!');
}

// Create Supabase client with more robust options
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
});
console.log('Supabase client created successfully');

// Test the client with explicit network request logging
console.log('About to make network request to Supabase for session check');
const startTime = Date.now();
supabase.auth.getSession()
  .then(response => {
    const endTime = Date.now();
    console.log(`Supabase client test completed in ${endTime - startTime}ms:`, { 
      hasSession: !!response.data.session,
      responseData: response.data,
      responseError: response.error
    });
  })
  .catch(error => {
    console.error('Supabase client test failed:', error.message, error);
  });

// Skip the direct fetch test as it's causing issues
