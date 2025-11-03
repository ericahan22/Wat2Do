import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.openai_service import extract_events_from_caption


image_url = "https://cdn.discordapp.com/attachments/715319623637270638/1434992256691081277/6ebcb7f6-e9a3-4f92-81ee-694c55b039ce.png?ex=690a582e&is=690906ae&hm=dae3dda56c30ee2da72fb70133a32a6cd8ff8423ca27712925db43322399405b"
post_caption="""It’s time to spread some ✨Jewish Joy✨ across campus!
Join us all week long for food, fun, and community — here’s what’s coming up:
🍔 Monday: BBQ with @standwithuscanada
📱 Tuesday: Instagram Challenges (join the fun on our stories!)
🥯 Wednesday: Bagel Brunch sponsored by FJMC
💛 Thursday: Boothing at Laurier
🕯️ Friday: Shabbat Dinner with @aepiwaterloo + @tailormadebirthright
Let’s make it a week full of connection, pride, and joy 💫
Check out our full lineup on our story — and don’t forget to bring your friends!"""

# Test AI client
result = extract_events_from_caption(post_caption, image_url)
print(result)