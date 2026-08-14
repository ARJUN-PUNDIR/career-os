import os
from typing import Optional, Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from app.config.settings import settings

def get_llm(
    temperature: float = 0.0,
    model_name: Optional[str] = None,
    provider: Optional[str] = None
) -> BaseChatModel:
    """
    Centralized Model Factory.
    Dynamically returns configured ChatModel based on settings (NVIDIA, OpenAI, Ollama, Anthropic).
    
    Default Model: NVIDIA NIM (nvidia/nemotron-3-ultra-550b-a55b)
    """
    selected_provider = provider or settings.MODEL_PROVIDER
    selected_provider = selected_provider.lower()
    
    if selected_provider == "nvidia":
        target_model = model_name or settings.NVIDIA_MODEL
        print(f"🤖 [Model Factory] Initializing NVIDIA NIM Model: {target_model}")
        return ChatOpenAI(
            model=target_model,
            openai_api_key=settings.NVIDIA_API_KEY,
            openai_api_base=settings.NVIDIA_BASE_URL,
            temperature=temperature
        )
        
    elif selected_provider == "openai":
        target_model = model_name or settings.DEFAULT_MODEL
        print(f"🤖 [Model Factory] Initializing OpenAI Model: {target_model}")
        return ChatOpenAI(
            model=target_model,
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=temperature
        )
        
    elif selected_provider == "ollama":
        target_model = model_name or settings.OLLAMA_MODEL
        print(f"🤖 [Model Factory] Initializing Local Ollama Model: {target_model}")
        return ChatOllama(
            model=target_model,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=temperature
        )
        
    else:
        # Fallback to OpenAI
        print(f"⚠️ [Model Factory] Unknown provider '{selected_provider}', falling back to OpenAI.")
        return ChatOpenAI(
            model=settings.DEFAULT_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=temperature
        )
