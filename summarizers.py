import streamlit as st
import mimetypes
import google.generativeai as genai



api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

def youtube_summarizer(link):
    model=genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(f"You are an expert summarizer. Watch the YouTube video at this link: {link} . Return only the core summary of the video in plain text, under 100 words. Do not include any introductions, disclaimers, or speaker names. Just the summary.")
    return response.text

def link_summarizer(link):
    model=genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(f"Search the web and summarize this article or webpage:\n{link} in 100 words. Provide only summary.")
    return response.text

def pdf_summarizer(link):
    model = genai.GenerativeModel('gemini-2.5-flash')

    with open(link, "rb") as f:
        pdf_bytes = f.read()

    parts = [
        {   
            "mime_type": "application/pdf",
            "data": pdf_bytes
        },
        "Summarize this PDF document in under 100 words. Focus on core concepts and provide only summary."
    ]

    response = model.generate_content(parts)
    return response.text

def image_summarizer(link):        
    model = genai.GenerativeModel('gemini-2.0-flash')
    mime_type, _ = mimetypes.guess_type(link)

    with open(link, "rb") as f:
        image_bytes = f.read()
    
    parts = [
        {
            "mime_type": mime_type,
            "data": image_bytes
        },
        "Summarize this image file in under 100 words. Focus on core concepts and provide summary only."
    ]

    response = model.generate_content(parts)
    return response.text

def txt_summarizer(link):
    with open(link, "r", encoding="utf-8'") as f:
        text_content = f.read()
    return text_summarizer(text_content)

def text_summarizer(content):
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(f"You are an expert summarizer. Summarize the given text under 100 words and return the summary only. \nText : {content}")
    return response.text