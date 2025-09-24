import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraping.ai_client import client
from django.db import connection
from typing import List


def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    text = text.replace("\n", " ").strip()
    
    response = client.embeddings.create(
        input=[text],
        model=model
    )
    
    return response.data[0].embedding


def generate_event_embedding(event_data: dict) -> List[float]:
    return get_embedding(repr(event_data))


def find_similar_events(embedding: List[float], threshold: float = 0.985) -> List[dict]:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, name, location, date, start_time, end_time, 
                   price, food, club_handle, registration, image_url,
                   1 - (embedding <=> %s::vector) as similarity
            FROM events 
            WHERE embedding IS NOT NULL
            AND 1 - (embedding <=> %s::vector) > %s
            ORDER BY similarity DESC
            LIMIT 10
        """, [embedding, embedding, threshold])
        
        columns = [col[0] for col in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            event_dict = dict(zip(columns, row))
            results.append(event_dict)
        
        return results


def is_duplicate_event(event_data: dict) -> bool:
    embedding = generate_event_embedding(event_data)
    similar_events = find_similar_events(embedding)
    
    return len(similar_events) > 0
