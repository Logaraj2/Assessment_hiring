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
    const { job_description, resume } = JSON.parse(event.body);
    
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

    const prompt = `Based on this job description and resume, provide a quick skill assessment:

JOB DESCRIPTION:
${job_description}

CANDIDATE RESUME:
${resume}

Please provide:
1. A list of key skills assessed with proficiency levels (Beginner, Intermediate, Advanced, Expert)
2. Evidence from the resume for each assessment
3. Recommended focus areas for development
4. Adjacent skills the candidate might have

Respond in JSON format with this structure:
{
  "skills_assessed": [
    {
      "skill": "Skill Name",
      "proficiency_level": "Level",
      "evidence": "Evidence from resume",
      "gap_analysis": "Any gaps identified"
    }
  ],
  "recommended_focus_areas": ["Area 1", "Area 2"],
  "adjacent_skills": ["Skill 1", "Skill 2"]
}`;

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
            content: prompt
          }
        ],
        max_tokens: 2000
      })
    });

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

    // Try to extract JSON from the response
    let assessmentData;
    try {
      const jsonMatch = aiMessage.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        assessmentData = JSON.parse(jsonMatch[0]);
      } else {
        // Fallback if no JSON found
        assessmentData = {
          skills_assessed: [
            { skill: 'General Skills', proficiency_level: 'Intermediate', evidence: 'Based on resume review' }
          ],
          recommended_focus_areas: ['Skill development'],
          adjacent_skills: ['Related competencies']
        };
      }
    } catch (parseError) {
      assessmentData = {
        skills_assessed: [
          { skill: 'General Skills', proficiency_level: 'Intermediate', evidence: 'Based on resume review' }
        ],
        recommended_focus_areas: ['Skill development'],
        adjacent_skills: ['Related competencies']
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
      body: JSON.stringify(assessmentData)
    };

  } catch (error) {
    console.error('Error in quick-assessment function:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        detail: 'Internal server error',
        message: error.message 
      })
    };
  }
};
