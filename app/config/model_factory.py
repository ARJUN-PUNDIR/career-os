import os
from typing import Optional, Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from app.config.settings import settings

def get_llm(
    temperature: float = 0.0,
    model_name: Optional[str] = None,
    provider: Optional[str] = None
) -> BaseChatModel:
    """
    Centralized Model Factory.
    Dynamically returns configured ChatModel based on settings (NVIDIA NIM, OpenAI, Ollama).
    
    Default Model: NVIDIA NIM (nvidia/nemotron-3-ultra-550b-a55b)
    """
    selected_provider = provider or settings.MODEL_PROVIDER
    selected_provider = selected_provider.lower()
    
    if selected_provider == "nvidia":
        target_model = model_name or settings.NVIDIA_MODEL
        print(f"🤖 [Model Factory] Initializing NVIDIA NIM Model: {target_model}")
        return ChatOpenAI(
            model=target_model,
            api_key=settings.NVIDIA_API_KEY,
            base_url=settings.NVIDIA_BASE_URL,
            temperature=temperature
        )
        
    elif selected_provider == "openai":
        target_model = model_name or settings.DEFAULT_MODEL
        print(f"🤖 [Model Factory] Initializing OpenAI Model: {target_model}")
        return ChatOpenAI(
            model=target_model,
            api_key=settings.OPENAI_API_KEY,
            temperature=temperature
        )
        
    elif selected_provider == "ollama":
        try:
            from langchain_ollama import ChatOllama
            target_model = model_name or settings.OLLAMA_MODEL
            print(f"🤖 [Model Factory] Initializing Local Ollama Model: {target_model}")
            return ChatOllama(
                model=target_model,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=temperature
            )
        except ImportError:
            raise ImportError("Ollama provider requires 'langchain-ollama' package installed.")
            
    else:
        print(f"⚠️ [Model Factory] Unknown provider '{selected_provider}', falling back to NVIDIA NIM.")
        return ChatOpenAI(
            model=settings.NVIDIA_MODEL,
            api_key=settings.NVIDIA_API_KEY,
            base_url=settings.NVIDIA_BASE_URL,
            temperature=temperature
        )
