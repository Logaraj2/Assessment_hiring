exports.handler = async function(event, context) {
  // Handle CORS preflight
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
      },
      body: ''
    };
  }

  // Only allow POST requests
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  try {
    // For Netlify functions, file upload is complex
    // We'll return a simple response asking user to paste text directly
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
      },
      body: JSON.stringify({
        text: "Please paste your resume text directly in the resume text area instead of uploading a file. File upload is not supported in this deployment.",
        message: "File upload not available - please paste resume text directly"
      })
    };

  } catch (error) {
    console.error('Error in upload-resume function:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        detail: 'Internal server error',
        message: error.message 
      })
    };
  }
};
