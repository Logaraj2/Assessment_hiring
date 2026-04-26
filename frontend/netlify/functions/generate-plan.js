const fetch = require('node-fetch');

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
    const { assessment_results, candidate_name } = JSON.parse(event.body);
    
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

    const prompt = `Based on this assessment results, create a personalized learning plan for ${candidate_name || 'the candidate'}:

ASSESSMENT RESULTS:
${JSON.stringify(assessment_results, null, 2)}

Please create a comprehensive learning plan with:
1. Multiple learning phases (2-4 phases)
2. Each phase should include:
   - Title and duration (in weeks)
   - Specific skills to learn
   - Recommended resources (courses, books, tutorials)
   - A practical project
3. Total duration estimate
4. Success metrics

Respond in JSON format with this structure:
{
  "learning_path": [
    {
      "title": "Phase Title",
      "duration_weeks": 4,
      "skills": ["Skill 1", "Skill 2"],
      "resources": [
        {
          "title": "Resource Title",
          "type": "course/book/tutorial",
          "estimated_hours": 20
        }
      ],
      "project": "Project description"
    }
  ],
  "total_duration_weeks": 12,
  "success_metrics": ["Metric 1", "Metric 2"]
}`;

    // Call OpenRouter API
    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://skill-assessment-agent.app',
        'X-Title': 'Learning Plan Generator'
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

    if (response.status === 429) {
      const waitSeconds = 10;
      return {
        statusCode: 429,
        body: JSON.stringify({
          detail: {
            message: `Rate limit exceeded (free API tier). Please wait ${waitSeconds} seconds.`,
            retry_after_seconds: waitSeconds
          }
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

    // Try to extract JSON from the response
    let learningPlan;
    try {
      const jsonMatch = aiMessage.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        learningPlan = JSON.parse(jsonMatch[0]);
      } else {
        // Fallback if no JSON found
        learningPlan = {
          learning_path: [
            {
              title: "Skill Development",
              duration_weeks: 8,
              skills: ["Core Skills"],
              resources: [
                {
                  title: "Online Course",
                  type: "course",
                  estimated_hours: 40
                }
              ],
              project: "Practice Project"
            }
          ],
          total_duration_weeks: 8,
          success_metrics: ["Complete course", "Build project"]
        };
      }
    } catch (parseError) {
      learningPlan = {
        learning_path: [
          {
            title: "Skill Development",
            duration_weeks: 8,
            skills: ["Core Skills"],
            resources: [
              {
                title: "Online Course",
                type: "course",
                estimated_hours: 40
              }
            ],
            project: "Practice Project"
          }
        ],
        total_duration_weeks: 8,
        success_metrics: ["Complete course", "Build project"]
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
        learning_plan: learningPlan
      })
    };

  } catch (error) {
    console.error('Error in generate-plan function:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        detail: 'Internal server error',
        message: error.message 
      })
    };
  }
};
