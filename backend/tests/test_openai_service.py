import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.openai_service import extract_events_from_caption


image_url = "https://media.discordapp.net/attachments/715319623637270638/1434995045269897277/Screenshot_2025-11-03_at_2.57.51_PM.png?ex=690a5ac7&is=69090947&hm=28813841083723f2071222b18790c8ac6bb2777382b66c11c9db2478abb46cc6&=&format=webp&quality=lossless&width=1064&height=1344"
post_caption="""Correction"""

# Test AI client
result = extract_events_from_caption(post_caption, image_url)
print(result)