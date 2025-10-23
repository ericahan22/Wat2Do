import os
import sys
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from django.db import connection

from services.openai_service import generate_embedding


def find_similar_events(
    embedding: list[float],
    threshold: float = 0.50,
    limit: int = None,
    min_date: str = date.today().isoformat(),
) -> list[dict]:
    """
    Find similar events using vector cosine similarity search
    """

    with connection.cursor() as cursor:
        # Base query with proper cosine similarity calculation
        base_query = """
            SELECT 
                id, 
                title,
                description,
                location,
                dtstart,
                dtend,
                club_type,
                1 - (embedding <=> %s::vector) as similarity
            FROM events 
            WHERE embedding IS NOT NULL
        """

        params = [embedding]

        # Add date filter if provided
        if min_date:
            base_query += " AND dtstart >= %s"
            params.append(min_date)

        # Add similarity threshold
        base_query += " AND 1 - (embedding <=> %s::vector) > %s"
        params.extend([embedding, threshold])

        # Order and limit
        base_query += " ORDER BY similarity DESC"
        if limit:
            base_query += " LIMIT %s"
            params.append(limit)

        cursor.execute(base_query, params)

        return [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "location": row[3],
                "dtstart": row[4],
                "dtend": row[5],
                "club_type": row[6],
                "similarity": float(row[7]),
            }
            for row in cursor.fetchall()
        ]


def is_duplicate_event(event_data: dict) -> bool:
    embedding = generate_embedding(event_data["description"])
    similar_events = find_similar_events(embedding, limit=1)

    return len(similar_events) > 0
