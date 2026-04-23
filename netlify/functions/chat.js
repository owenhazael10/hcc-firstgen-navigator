exports.handler = async function(event, context) {
  // Only allow POST requests
  if (event.httpMethod !== "POST") {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: "Method not allowed" })
    };
  }

  try {
    const body = JSON.parse(event.body);
    const userMessage = body.messages[body.messages.length - 1].content;

    // Search Supabase for relevant HC documents using keyword search
    let relevantDocs = "";
    try {
      const supabaseUrl = "https://cpgbvsfepbwfjplyxcdm.supabase.co";
      const supabaseKey = "sb_publishable_3D-u6yUcIsF0oH1MvID_Cg_lc_j8tVM";
      
      // Extract keywords from user message (simple approach)
      const keywords = userMessage.toLowerCase()
        .replace(/[^\w\s]/g, ' ')
        .split(/\s+/)
        .filter(word => word.length > 3)
        .slice(0, 5)
        .join('|');
      
      if (keywords) {
        const searchResponse = await fetch(
          `${supabaseUrl}/rest/v1/hc_documents?content=ilike.*${keywords}*&limit=3`,
          {
            headers: {
              "apikey": supabaseKey,
              "Authorization": `Bearer ${supabaseKey}`
            }
          }
        );
        
        if (searchResponse.ok) {
          const docs = await searchResponse.json();
          if (docs && docs.length > 0) {
            relevantDocs = "\n\nRELEVANT HC DOCUMENT EXCERPTS:\n" + 
              docs.map((doc, i) => `[${i+1}] ${doc.content}`).join("\n\n");
          }
        }
      }
    } catch (searchError) {
      console.log("Search error:", searchError);
      // Continue without RAG if search fails
    }

    // Call Anthropic API with enhanced system prompt
    const systemPrompt = body.system + relevantDocs;
    
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": process.env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
      },
      body: JSON.stringify({
        model: body.model,
        max_tokens: body.max_tokens,
        system: systemPrompt,
        messages: body.messages
      })
    });

    const data = await response.json();

    return {
      statusCode: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    };
  } catch (error) {
    console.error("Error:", error);
    return {
      statusCode: 500,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ 
        error: "Internal server error",
        message: error.message 
      })
    };
  }
};
