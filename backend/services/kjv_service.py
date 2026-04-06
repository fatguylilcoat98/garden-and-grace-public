"""
Garden & Grace — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq)
Truth · Safety · We Got Your Back
"""

import random

KJV_VERSES = {
    "garden": [
        {"verse": "The LORD God planted a garden eastward in Eden; and there he put the man whom he had formed.", "ref": "Genesis 2:8"},
        {"verse": "For the earth bringeth forth fruit of herself; first the blade, then the ear, after that the full corn in the ear.", "ref": "Mark 4:28"},
        {"verse": "Consider the lilies of the field, how they grow; they toil not, neither do they spin: And yet I say unto you, That even Solomon in all his glory was not arrayed like one of these.", "ref": "Matthew 6:28-29"},
        {"verse": "He that tilleth his land shall be satisfied with bread.", "ref": "Proverbs 12:11"},
        {"verse": "To every thing there is a season, and a time to every purpose under the heaven: A time to plant, and a time to pluck up that which is planted.", "ref": "Ecclesiastes 3:1-2"},
        {"verse": "And the LORD shall guide thee continually, and satisfy thy soul in drought, and thou shalt be like a watered garden.", "ref": "Isaiah 58:11"},
        {"verse": "I am the true vine, and my Father is the husbandman.", "ref": "John 15:1"},
        {"verse": "For as the earth bringeth forth her bud, and as the garden causeth the things that are sown in it to spring forth; so the Lord GOD will cause righteousness and praise to spring forth.", "ref": "Isaiah 61:11"},
    ],
    "birds": [
        {"verse": "Are not five sparrows sold for two farthings, and not one of them is forgotten before God?", "ref": "Luke 12:6"},
        {"verse": "But they that wait upon the LORD shall renew their strength; they shall mount up with wings as eagles; they shall run, and not be weary; and they shall walk, and not faint.", "ref": "Isaiah 40:31"},
        {"verse": "Doth the hawk fly by thy wisdom, and stretch her wings toward the south? Doth the eagle mount up at thy command?", "ref": "Job 39:26-27"},
        {"verse": "As an eagle stirreth up her nest, fluttereth over her young, spreadeth abroad her wings, taketh them, beareth them on her wings: So the LORD alone did lead him.", "ref": "Deuteronomy 32:11-12"},
        {"verse": "Yea, the sparrow hath found an house, and the swallow a nest for herself, where she may lay her young, even thine altars, O LORD of hosts.", "ref": "Psalm 84:3"},
        {"verse": "He giveth to the beast his food, and to the young ravens which cry.", "ref": "Psalm 147:9"},
        {"verse": "Look at the birds of the air; for they sow not, neither do they reap, nor gather into barns; yet your heavenly Father feedeth them.", "ref": "Matthew 6:26"},
        {"verse": "Out of the ground the LORD God formed every beast of the field, and every fowl of the air; and brought them unto Adam to see what he would call them.", "ref": "Genesis 2:19"},
    ],
    "fishing": [
        {"verse": "And he saith unto them, Follow me, and I will make you fishers of men.", "ref": "Matthew 4:19"},
        {"verse": "Simon Peter saith unto them, I go a fishing. They say unto him, We also go with thee.", "ref": "John 21:3"},
        {"verse": "Again, the kingdom of heaven is like unto a net, that was cast into the sea, and gathered of every kind.", "ref": "Matthew 13:47"},
        {"verse": "So is this great and wide sea, wherein are things creeping innumerable, both small and great beasts. There go the ships: there is that leviathan, whom thou hast made to play therein.", "ref": "Psalm 104:25-26"},
        {"verse": "Cast thy bread upon the waters: for thou shalt find it after many days.", "ref": "Ecclesiastes 11:1"},
        {"verse": "They that go down to the sea in ships, that do business in great waters; These see the works of the LORD, and his wonders in the deep.", "ref": "Psalm 107:23-24"},
    ],
    "recipe": [
        {"verse": "Whether therefore ye eat, or drink, or whatsoever ye do, do all to the glory of God.", "ref": "1 Corinthians 10:31"},
        {"verse": "O taste and see that the LORD is good: blessed is the man that trusteth in him.", "ref": "Psalm 34:8"},
        {"verse": "And God said, Behold, I have given you every herb bearing seed, which is upon the face of all the earth, and every tree, in the which is the fruit of a tree yielding seed; to you it shall be for meat.", "ref": "Genesis 1:29"},
        {"verse": "Better is a dinner of herbs where love is, than a stalled ox and hatred therewith.", "ref": "Proverbs 15:17"},
        {"verse": "And he took the five loaves and the two fishes, and looking up to heaven, he blessed them.", "ref": "Luke 9:16"},
        {"verse": "She is like the merchants' ships; she bringeth her food from afar. She riseth also while it is yet night, and giveth meat to her household.", "ref": "Proverbs 31:14-15"},
        {"verse": "Give us this day our daily bread.", "ref": "Matthew 6:11"},
    ],
    "build": [
        {"verse": "Except the LORD build the house, they labour in vain that build it.", "ref": "Psalm 127:1"},
        {"verse": "Every wise woman buildeth her house: but the foolish plucketh it down with her hands.", "ref": "Proverbs 14:1"},
        {"verse": "And he hath filled him with the spirit of God, in wisdom, in understanding, and in knowledge, and in all manner of workmanship.", "ref": "Exodus 35:31"},
        {"verse": "For we are labourers together with God: ye are God's husbandry, ye are God's building.", "ref": "1 Corinthians 3:9"},
        {"verse": "See, I have called by name Bezaleel the son of Uri... and I have filled him with the spirit of God, in wisdom, and in understanding, and in knowledge, and in all manner of workmanship.", "ref": "Exodus 31:2-3"},
        {"verse": "Therefore whosoever heareth these sayings of mine, and doeth them, I will liken him unto a wise man, which built his house upon a rock.", "ref": "Matthew 7:24"},
        {"verse": "She considereth a field, and buyeth it: with the fruit of her hands she planteth a vineyard.", "ref": "Proverbs 31:16"},
    ],
    "daily": [
        {"verse": "This is the day which the LORD hath made; we will rejoice and be glad in it.", "ref": "Psalm 118:24"},
        {"verse": "The LORD bless thee, and keep thee: The LORD make his face shine upon thee, and be gracious unto thee.", "ref": "Numbers 6:24-25"},
        {"verse": "I can do all things through Christ which strengtheneth me.", "ref": "Philippians 4:13"},
        {"verse": "Trust in the LORD with all thine heart; and lean not unto thine own understanding.", "ref": "Proverbs 3:5"},
        {"verse": "The LORD is my shepherd; I shall not want.", "ref": "Psalm 23:1"},
        {"verse": "For I know the thoughts that I think toward you, saith the LORD, thoughts of peace, and not of evil, to give you an expected end.", "ref": "Jeremiah 29:11"},
        {"verse": "Thy word is a lamp unto my feet, and a light unto my path.", "ref": "Psalm 119:105"},
        {"verse": "Be strong and of a good courage; be not afraid, neither be thou dismayed: for the LORD thy God is with thee whithersoever thou goest.", "ref": "Joshua 1:9"},
        {"verse": "But seek ye first the kingdom of God, and his righteousness; and all these things shall be added unto you.", "ref": "Matthew 6:33"},
        {"verse": "Come unto me, all ye that labour and are heavy laden, and I will give you rest.", "ref": "Matthew 11:28"},
        {"verse": "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.", "ref": "John 3:16"},
        {"verse": "And we know that all things work together for good to them that love God.", "ref": "Romans 8:28"},
        {"verse": "Rejoice in the Lord alway: and again I say, Rejoice.", "ref": "Philippians 4:4"},
        {"verse": "The fear of the LORD is the beginning of wisdom.", "ref": "Proverbs 9:10"},
    ]
}

def get_verse(category: str) -> dict:
    """Return a random KJV verse for the given feature category."""
    verses = KJV_VERSES.get(category, KJV_VERSES["daily"])
    return random.choice(verses)

def get_daily_verse() -> dict:
    """Return a daily verse based on day of year for consistency."""
    from datetime import datetime
    day_of_year = datetime.now().timetuple().tm_yday
    verses = KJV_VERSES["daily"]
    return verses[day_of_year % len(verses)]
