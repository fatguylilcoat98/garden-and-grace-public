"""
Garden & Grace — Public Edition
The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq)
Truth · Safety · We Got Your Back

Closing words: Scripture, uplifting sayings, or lighthearted jokes.
User picks their preference.
"""

import random

# ── SCRIPTURE (KJV) ──────────────────────────────────────────────────────────

KJV_VERSES = {
    "garden": [
        {"verse": "The LORD God planted a garden eastward in Eden; and there he put the man whom he had formed.", "ref": "Genesis 2:8"},
        {"verse": "For the earth bringeth forth fruit of herself; first the blade, then the ear, after that the full corn in the ear.", "ref": "Mark 4:28"},
        {"verse": "Consider the lilies of the field, how they grow; they toil not, neither do they spin.", "ref": "Matthew 6:28"},
        {"verse": "He that tilleth his land shall be satisfied with bread.", "ref": "Proverbs 12:11"},
        {"verse": "To every thing there is a season, and a time to every purpose under the heaven.", "ref": "Ecclesiastes 3:1"},
        {"verse": "And the LORD shall guide thee continually, and thou shalt be like a watered garden.", "ref": "Isaiah 58:11"},
    ],
    "birds": [
        {"verse": "Are not five sparrows sold for two farthings, and not one of them is forgotten before God?", "ref": "Luke 12:6"},
        {"verse": "They that wait upon the LORD shall renew their strength; they shall mount up with wings as eagles.", "ref": "Isaiah 40:31"},
        {"verse": "Look at the birds of the air; for they sow not, neither do they reap; yet your heavenly Father feedeth them.", "ref": "Matthew 6:26"},
        {"verse": "Yea, the sparrow hath found an house, and the swallow a nest for herself.", "ref": "Psalm 84:3"},
    ],
    "fishing": [
        {"verse": "Follow me, and I will make you fishers of men.", "ref": "Matthew 4:19"},
        {"verse": "Simon Peter saith unto them, I go a fishing. They say unto him, We also go with thee.", "ref": "John 21:3"},
        {"verse": "Cast thy bread upon the waters: for thou shalt find it after many days.", "ref": "Ecclesiastes 11:1"},
        {"verse": "They that go down to the sea in ships; these see the works of the LORD, and his wonders in the deep.", "ref": "Psalm 107:23-24"},
    ],
    "recipe": [
        {"verse": "Whether therefore ye eat, or drink, or whatsoever ye do, do all to the glory of God.", "ref": "1 Corinthians 10:31"},
        {"verse": "O taste and see that the LORD is good.", "ref": "Psalm 34:8"},
        {"verse": "Better is a dinner of herbs where love is, than a stalled ox and hatred therewith.", "ref": "Proverbs 15:17"},
        {"verse": "Give us this day our daily bread.", "ref": "Matthew 6:11"},
    ],
    "build": [
        {"verse": "Except the LORD build the house, they labour in vain that build it.", "ref": "Psalm 127:1"},
        {"verse": "He hath filled him with the spirit of God, in wisdom, in understanding, and in all manner of workmanship.", "ref": "Exodus 35:31"},
        {"verse": "Therefore whosoever heareth these sayings of mine, and doeth them, I will liken him unto a wise man, which built his house upon a rock.", "ref": "Matthew 7:24"},
    ],
    "daily": [
        {"verse": "This is the day which the LORD hath made; we will rejoice and be glad in it.", "ref": "Psalm 118:24"},
        {"verse": "The LORD bless thee, and keep thee.", "ref": "Numbers 6:24"},
        {"verse": "I can do all things through Christ which strengtheneth me.", "ref": "Philippians 4:13"},
        {"verse": "Trust in the LORD with all thine heart; and lean not unto thine own understanding.", "ref": "Proverbs 3:5"},
        {"verse": "The LORD is my shepherd; I shall not want.", "ref": "Psalm 23:1"},
        {"verse": "Be strong and of a good courage; be not afraid.", "ref": "Joshua 1:9"},
        {"verse": "Come unto me, all ye that labour and are heavy laden, and I will give you rest.", "ref": "Matthew 11:28"},
        {"verse": "Rejoice in the Lord alway: and again I say, Rejoice.", "ref": "Philippians 4:4"},
    ]
}

# ── UPLIFTING SAYINGS ────────────────────────────────────────────────────────

SAYINGS = {
    "garden": [
        {"verse": "A garden is a friend you can visit any time.", "ref": "—"},
        {"verse": "To plant a garden is to believe in tomorrow.", "ref": "— Audrey Hepburn"},
        {"verse": "The earth laughs in flowers.", "ref": "— Ralph Waldo Emerson"},
        {"verse": "Where flowers bloom, so does hope.", "ref": "— Lady Bird Johnson"},
        {"verse": "Gardening adds years to your life and life to your years.", "ref": "—"},
        {"verse": "In every walk with nature one receives far more than one seeks.", "ref": "— John Muir"},
    ],
    "birds": [
        {"verse": "A bird does not sing because it has an answer. It sings because it has a song.", "ref": "— Maya Angelou"},
        {"verse": "Use the talents you possess, for the woods would be very silent if no birds sang except the best.", "ref": "— Henry Van Dyke"},
        {"verse": "Faith is the bird that feels the light when the dawn is still dark.", "ref": "— Rabindranath Tagore"},
        {"verse": "The reason birds can fly and we can't is simply because they have perfect faith.", "ref": "— J.M. Barrie"},
    ],
    "fishing": [
        {"verse": "Many go fishing all their lives without knowing that it is not fish they are after.", "ref": "— Henry David Thoreau"},
        {"verse": "Time is but the stream I go a-fishing in.", "ref": "— Henry David Thoreau"},
        {"verse": "The best time to go fishing is when you can get away.", "ref": "—"},
        {"verse": "A bad day of fishing is still better than a good day at work.", "ref": "—"},
        {"verse": "Give a man a fish and he eats for a day. Teach a man to fish and you get the whole weekend to yourself.", "ref": "—"},
    ],
    "recipe": [
        {"verse": "People who love to eat are always the best people.", "ref": "— Julia Child"},
        {"verse": "Cooking is love made visible.", "ref": "—"},
        {"verse": "The secret ingredient is always love.", "ref": "—"},
        {"verse": "Good food is the foundation of genuine happiness.", "ref": "— Auguste Escoffier"},
    ],
    "build": [
        {"verse": "The best time to plant a tree was twenty years ago. The second best time is now.", "ref": "— Chinese Proverb"},
        {"verse": "Build something that matters. Something that lasts.", "ref": "—"},
        {"verse": "The only way to do great work is to love what you do.", "ref": "— Steve Jobs"},
        {"verse": "Start where you are. Use what you have. Do what you can.", "ref": "— Arthur Ashe"},
    ],
    "daily": [
        {"verse": "Today is a good day to have a good day.", "ref": "—"},
        {"verse": "You are braver than you believe, stronger than you seem, and smarter than you think.", "ref": "— A.A. Milne"},
        {"verse": "Be the reason someone smiles today.", "ref": "—"},
        {"verse": "Every day may not be good, but there is something good in every day.", "ref": "—"},
        {"verse": "Kindness is free. Sprinkle that stuff everywhere.", "ref": "—"},
        {"verse": "You don't have to be perfect to be wonderful.", "ref": "—"},
        {"verse": "Difficult roads often lead to beautiful destinations.", "ref": "—"},
        {"verse": "The sun is new each day.", "ref": "— Heraclitus"},
    ]
}

# ── FUN & INNOCENT JOKES ─────────────────────────────────────────────────────

JOKES = {
    "garden": [
        {"verse": "Why did the gardener plant light bulbs? Because he wanted to grow a power plant.", "ref": "🌱"},
        {"verse": "What did the big flower say to the little flower? Hey there, bud!", "ref": "🌸"},
        {"verse": "How do trees get on the internet? They log in.", "ref": "🌳"},
        {"verse": "What do you call a cheerful gardener? A jolly rancher.", "ref": "🌿"},
        {"verse": "Why do potatoes make good detectives? Because they keep their eyes peeled.", "ref": "🥔"},
    ],
    "birds": [
        {"verse": "What do you call a bird that's afraid to fly? A chicken.", "ref": "🐔"},
        {"verse": "Why do hummingbirds hum? Because they forgot the words.", "ref": "🐦"},
        {"verse": "What kind of bird works at a construction site? A crane.", "ref": "🏗️"},
        {"verse": "What do you get when you cross a parrot with a centipede? A walkie-talkie.", "ref": "🦜"},
    ],
    "fishing": [
        {"verse": "What do fish say when they hit a concrete wall? Dam.", "ref": "🐟"},
        {"verse": "Why don't fish play tennis? They're afraid of the net.", "ref": "🎾"},
        {"verse": "What did the fish say when he swam into a wall? Dam.", "ref": "🐠"},
        {"verse": "Why are fish so smart? Because they live in schools.", "ref": "🎓"},
        {"verse": "What's the best way to catch a fish? Have someone throw it to you.", "ref": "🎣"},
    ],
    "recipe": [
        {"verse": "What did the lettuce say to the celery? Quit stalking me!", "ref": "🥬"},
        {"verse": "Why did the tomato turn red? Because it saw the salad dressing.", "ref": "🍅"},
        {"verse": "What do you call cheese that isn't yours? Nacho cheese.", "ref": "🧀"},
        {"verse": "Why did the cookie go to the doctor? Because it felt crummy.", "ref": "🍪"},
    ],
    "build": [
        {"verse": "I used to hate building fences. But then I got over it.", "ref": "🔨"},
        {"verse": "Why did the hammer go to school? To get nailed in every subject.", "ref": "📚"},
        {"verse": "What did one wall say to the other? I'll meet you at the corner.", "ref": "🧱"},
        {"verse": "Why was the screwdriver always invited to parties? It was a real turn.", "ref": "🔧"},
    ],
    "daily": [
        {"verse": "What did the ocean say to the beach? Nothing, it just waved.", "ref": "🌊"},
        {"verse": "Why don't scientists trust atoms? Because they make up everything.", "ref": "⚛️"},
        {"verse": "I told my wife she was drawing her eyebrows too high. She looked surprised.", "ref": "😄"},
        {"verse": "What do you call a bear with no teeth? A gummy bear.", "ref": "🐻"},
        {"verse": "Why don't eggs tell jokes? They'd crack each other up.", "ref": "🥚"},
        {"verse": "What do you call a lazy kangaroo? A pouch potato.", "ref": "🦘"},
        {"verse": "Parallel lines have so much in common. It's a shame they'll never meet.", "ref": "📐"},
        {"verse": "I'm reading a book about anti-gravity. It's impossible to put down.", "ref": "📖"},
    ]
}

SOURCES = {
    "scripture": KJV_VERSES,
    "sayings": SAYINGS,
    "jokes": JOKES,
}


def get_verse(category: str, mode: str = "scripture") -> dict:
    """Return a random closing word for the given feature and mode."""
    source = SOURCES.get(mode, KJV_VERSES)
    pool = source.get(category, source.get("daily", []))
    if not pool:
        pool = KJV_VERSES.get(category, KJV_VERSES["daily"])
    return random.choice(pool)


def get_daily_verse(mode: str = "scripture") -> dict:
    """Return a daily closing word based on day of year for consistency."""
    from datetime import datetime
    day_of_year = datetime.now().timetuple().tm_yday
    source = SOURCES.get(mode, KJV_VERSES)
    pool = source.get("daily", KJV_VERSES["daily"])
    return pool[day_of_year % len(pool)]
