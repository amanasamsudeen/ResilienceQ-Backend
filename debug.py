import google.generativeai as genai
import os

genai.configure(api_key="AIzaSyDPmTNFzP0DWO6qDobxLdQ0pdTiSfrhBcI")

for m in genai.list_models():
    if 'embedContent' in m.supported_generation_methods:
        print(m.name)