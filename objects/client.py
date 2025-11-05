# Databricks notebook source
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

def create_client():
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    return Anthropic(api_key=api_key)

# Create a single instance to be used across files
client = create_client()