import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from django.db import connection

from services.openai_service import generate_embedding


def find_similar_events(
    embedding: list[float],
    threshold: float = 0.985,
    limit: int = None,
    min_date: str = None,
) -> list[dict]:
    with connection.cursor() as cursor:
        # Base query with date filtering first for performance
        base_query = """
            SELECT id, 1 - (embedding <=> %s::vector) as similarity
            FROM events 
            WHERE embedding IS NOT NULL
        """

        params = [embedding]

        # Add date filter if provided to reduce search space
        if min_date:
            base_query += " AND date >= %s"
            params.append(min_date)

        # Add similarity threshold
        base_query += " AND 1 - (embedding <=> %s::vector) > %s"
        params.extend([embedding, threshold])

        # Order and limit
        base_query += " ORDER BY similarity DESC"

        if limit is not None:
            base_query += " LIMIT %s"
            params.append(limit)

        cursor.execute(base_query, params)

        return [
            {"id": row[0], "similarity": float(row[1])} for row in cursor.fetchall()
        ]


def is_duplicate_event(event_data: dict) -> bool:
    embedding = generate_embedding(event_data["description"])
    similar_events = find_similar_events(embedding, limit=1)

    return len(similar_events) > 0
