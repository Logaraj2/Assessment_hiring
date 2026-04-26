const fetch = require('node-fetch');

// System prompt for assessment
const ASSESSMENT_SYSTEM_PROMPT = `You are an expert technical interviewer conducting a skill assessment. Your task is to:

1. Assess the candidate's proficiency level for each required skill based on their resume
2. Ask targeted questions to verify their real proficiency level
3. Keep conversations focused and efficient (maximum 5-6 total exchanges)
4. Provide evidence-based assessments
5. Identify skill gaps and adjacent skills

For each skill, assess proficiency as: Beginner, Intermediate, Advanced, or Expert
Always provide specific evidence from their responses to justify your assessment.

Be conversational but professional. Ask one question at a time and wait for the candidate's response before proceeding.`;

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
    const { job_description, resume, conversation_history } = JSON.parse(event.body);
    
    // Get OpenRouter API key from environment variables
    const apiKey = process.env.OPENROUTER_API_KEY;
    if (!apiKey) {
      return {
        statusCode: 500,
        body: JSON.stringify({ 
          detail: 'OpenRouter API key not configured',
          message: 'Please set OPENROUTER_API_KEY environment variable'
        })
      };
    }

    // Build messages for AI
    let messages = [];
    
    if (conversation_history && conversation_history.length > 0) {
      // Continue existing conversation
      messages = conversation_history;
    } else {
      // Start new assessment
      messages = [
        {
          role: 'user',
          content: `CANDIDATE RESUME:\n${resume}\n\nPlease assess the candidate's proficiency in the required skills based on their resume.\nAsk targeted questions to verify their real proficiency level.\n\nStart the skill assessment by introducing yourself and explaining the process. Then ask about the first relevant skill.`
        }
      ];
    }

    // Call OpenRouter API
    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://skill-assessment-agent.app',
        'X-Title': 'Skill Assessment Agent'
      },
      body: JSON.stringify({
        model: 'google/gemma-3-12b-it:free',
        messages: [
          {
            role: 'user',
            content: `[Instructions: ${ASSESSMENT_SYSTEM_PROMPT}]\n\n${messages[messages.length - 1].content}`
          }
        ],
        max_tokens: 2000
      })
    });

    if (response.status === 429) {
      const errorText = await response.text();
      return {
        statusCode: 429,
        body: JSON.stringify({ 
          detail: 'Rate limit exceeded',
          message: errorText
        })
      };
    }

    if (!response.ok) {
      const errorText = await response.text();
      return {
        statusCode: response.status,
        body: JSON.stringify({ 
          detail: 'AI service error',
          message: errorText
        })
      };
    }

    const data = await response.json();
    const aiMessage = data.choices[0].message.content;

    // Check if assessment is complete (simple heuristic)
    const isComplete = messages.length >= 8 || aiMessage.toLowerCase().includes('assessment complete');

    let assessmentData = null;
    if (isComplete) {
      // Generate basic assessment summary
      assessmentData = {
        skills_assessed: [
          { skill: 'Communication', proficiency_level: 'Intermediate', evidence: 'Clear responses during assessment' },
          { skill: 'Technical Knowledge', proficiency_level: 'Advanced', evidence: 'Demonstrated understanding of concepts' }
        ],
        recommended_focus_areas: ['Continue skill development'],
        adjacent_skills: ['Problem solving', 'Team collaboration']
      };
    }

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
      },
      body: JSON.stringify({
        message: aiMessage,
        is_complete: isComplete,
        assessment_data: assessmentData
      })
    };

  } catch (error) {
    console.error('Error in assess function:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        detail: 'Internal server error',
        message: error.message 
      })
    };
  }
};
