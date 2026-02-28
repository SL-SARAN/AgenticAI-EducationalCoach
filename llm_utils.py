import json
import ollama

def safe_json_chat(prompt, fallback, model='phi3', max_retries=2):
    """
    Safely executes an LLM chat expecting JSON output.
    Retries automatically if the LLM produces invalid JSON.
    """
    prompt_appended = prompt + "\n\nIMPORTANT: Ensure your output is perfectly valid JSON. Escape any double quotes inside string values using \\\"."
    
    for attempt in range(max_retries):
        try:
            # temperature 0.1 to reduce hallucinated syntax errors
            response = ollama.chat(model=model, messages=[
                {'role': 'user', 'content': prompt_appended}
            ], format='json', options={'temperature': 0.1})
            
            content = response['message']['content']
            if not content.strip():
                continue
                
            return json.loads(content, strict=False)
        except json.JSONDecodeError as e:
            error_msg = f"JSON Parse Error on attempt {attempt+1}: {e}"
            print(error_msg)
            prompt_appended += f"\n\nERROR: Your previous response caused a JSON parsing error: {e}. Please fix the syntax and return valid JSON."
        except Exception as e:
            print(f"LLM General Error: {e}")
            break
            
    print("Max retries exceeded or critical error. Falling back to default data.")
    return fallback
