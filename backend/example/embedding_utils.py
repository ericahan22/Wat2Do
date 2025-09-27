import os
import sys
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from django.db import connection

from services.openai_service import generate_embedding


def generate_event_embedding(event_data: dict) -> List[float]:
    return generate_embedding(repr(event_data))


def find_similar_events(
    embedding: List[float], threshold: float = 0.985, limit: int = None
) -> List[dict]:
    with connection.cursor() as cursor:
        if limit is not None:
            cursor.execute(
                """
                SELECT id, 1 - (embedding <=> %s::vector) as similarity
                FROM events 
                WHERE embedding IS NOT NULL
                AND 1 - (embedding <=> %s::vector) > %s
                ORDER BY similarity DESC
                LIMIT %s
            """,
                [embedding, embedding, threshold, limit],
            )
        else:
            cursor.execute(
                """
                SELECT id, 1 - (embedding <=> %s::vector) as similarity
                FROM events 
                WHERE embedding IS NOT NULL
                AND 1 - (embedding <=> %s::vector) > %s
                ORDER BY similarity DESC
            """,
                [embedding, embedding, threshold],
            )

        return [
            {"id": row[0], "similarity": float(row[1])} for row in cursor.fetchall()
        ]


def is_duplicate_event(event_data: dict) -> bool:
    embedding = generate_event_embedding(event_data)
    similar_events = find_similar_events(embedding, limit=1)

    return len(similar_events) > 0
