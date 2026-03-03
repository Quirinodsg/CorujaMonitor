#!/usr/bin/env python3
"""Test Ollama status endpoint"""
import asyncio
import httpx
import os

async def test_ollama():
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    print(f"Testing Ollama at: {ollama_url}")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            print("Attempting connection...")
            response = await client.get(f"{ollama_url}/api/tags")
            
            print(f"✅ Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                print(f"✅ Models found: {len(models)}")
                
                for model in models:
                    print(f"   - {model.get('name')} ({model.get('size')} bytes)")
                
                # Check if llama2 is installed
                model_installed = any(m.get("name", "").startswith("llama2") for m in models)
                print(f"✅ llama2 installed: {model_installed}")
                
                return True
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return False
    
    except httpx.ConnectError as e:
        print(f"❌ Connection Error: {e}")
        print("   Ollama container might not be running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_ollama())
    exit(0 if result else 1)
