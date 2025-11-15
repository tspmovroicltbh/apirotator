// backend/server.js (Node.js/Express example)
const express = require('express');
const app = express();

// Store keys securely in environment variables
const API_KEYS = [
    process.env.OPENROUTER_KEY_1,
    process.env.OPENROUTER_KEY_2,
    process.env.OPENROUTER_KEY_3,
];

let currentKeyIndex = 0;

app.post('/api/analyze-trade', async (req, res) => {
    const { prompt } = req.body;
    
    const maxRetries = API_KEYS.length;
    
    for (let attempt = 0; attempt < maxRetries; attempt++) {
        const apiKey = API_KEYS[currentKeyIndex];
        
        try {
            const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${apiKey}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    model: "openai/gpt-oss-20b:free",
                    messages: [{ role: "user", content: prompt }]
                })
            });

            if (response.status === 429) {
                console.warn(`Key ${currentKeyIndex + 1} rate limited`);
                currentKeyIndex = (currentKeyIndex + 1) % API_KEYS.length;
                continue;
            }

            if (!response.ok) {
                const error = await response.text();
                return res.status(response.status).json({ error });
            }

            const data = await response.json();
            return res.json(data);
            
        } catch (error) {
            console.error(`Error with key ${currentKeyIndex + 1}:`, error);
        }
    }
    
    // All keys exhausted
    return res.status(429).json({ 
        error: "ALL_KEYS_RATE_LIMITED",
        message: "We have exhausted all available API limits from our provider. Please try again later."
    });
});

app.listen(3000, () => console.log('Server running on port 3000'));
