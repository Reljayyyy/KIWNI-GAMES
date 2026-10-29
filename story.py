"""All story text: the 8 levels, prologue, final boss, victory and ending.

{hero} is replaced by the name of the hero the player chose.
Cutscene panels are (speaker, text, mood):  speaker = "hero", "boss" or "narrator";
mood (boss only) = angry, hurt, defeated, sad, happy.

Every level now has its own helper character:
  npc   = the character's name
  intro = the story shown when the level starts
  talk  = the conversation (each line starts with who is speaking)
  topic = what kind of questions this level should ask (see LEVEL_QUESTIONS)
  win   = the story shown when the level is completed
"""
from sprites import HERO


def tell(s):
    return s.replace("{hero}", HERO["name"])


STORY = {
    1: dict(
        npc="Hop the Frog",
        topic="shapes",
        intro="A Muddle Storm jumbled Shape Road! Hop the Frog cannot cross the river because "
              "his stepping stones lost their shapes. Help {hero} and Hop fix them to win the first Rainbow Gem.",
        talk=["Hop: Ribbit! Oh no, my stepping stones are all mixed up!",
              "{hero}: Don't worry, Hop. What is wrong with them?",
              "Hop: A stone only shines when you pick the right shape. Circle, square, triangle...",
              "{hero}: Easy! Let's find every shape together!"],
        win="Splash! The stones shine and Hop jumps across. \"Thank you, friend!\" The Shape Gem is back. One gem found, six to go!"),
    2: dict(
        npc="Grandma Rose and Mittens",
        topic="colors",
        intro="The storm blew Grandma Rose's cat, Mittens, away and washed the color out of her flowers! "
              "Mittens always naps near a special color.",
        talk=["Grandma Rose: Oh dear, my cat is missing and my flowers turned gray!",
              "{hero}: We will find Mittens, Grandma!",
              "Grandma Rose: Mittens loves bright colors. Show me red, then blue, then yellow, and the colors will come back.",
              "{hero}: Let's paint the garden with the right colors!"],
        win="Meow! Mittens was napping in the flowers. Grandma Rose cries happy tears and gives you the Color Gem!"),
    3: dict(
        npc="Luna the Firefly",
        topic="counting and numbers",
        intro="In Number Forest the fireflies lost their numbers! Little Luna the Firefly "
              "cannot light up because she forgot how to count.",
        talk=["Luna: Bzzz... I used to glow with every number, but now I'm dark.",
              "{hero}: Can we help you count, Luna?",
              "Luna: Yes! Count the things you see, and follow the number trail. Each right number makes me glow brighter!",
              "{hero}: One, two, three... here we go!"],
        win="Luna glows brighter than the moon, and all the fireflies shine in perfect order. The Number Gem is yours!"),
    4: dict(
        npc="Farmer Joe",
        topic="sorting",
        intro="Oh dear! Farmer Joe's harvest got blown everywhere. Apples, pumpkins and carrots are mixed up "
              "and the market opens soon!",
        talk=["Farmer Joe: Howdy, {hero}! My harvest is a big mess!",
              "{hero}: What should we do, Farmer Joe?",
              "Farmer Joe: Put each thing in the right basket. We can sort by color, by size, or by kind.",
              "{hero}: Sorting is my favorite. Let's tidy the farm!"],
        win="The baskets are full and the farm is tidy. Farmer Joe tips his hat and gives you the Sorting Gem to say thank you."),
    5: dict(
        npc="Bruno the Bridge Troll",
        topic="directions (left, right, up, down)",
        intro="Bruno the Bridge Troll got turned around in the storm! Now he only lets travelers cross "
              "if they know their directions.",
        talk=["Bruno: Halt! Nobody crosses my bridge unless they know left from right!",
              "{hero}: We know! Please let us try, Bruno.",
              "Bruno: Hmm. Then tell me which way to go: left, right, up or down. Every right turn gets you closer.",
              "{hero}: Ready! Let's follow the arrows."],
        win="Bruno smiles his biggest smile. \"You know your way!\" The bridge glows and the Direction Gem is yours!"),
    6: dict(
        npc="Daisy the Bee",
        topic="patterns",
        intro="The flowers in Pattern Garden bloomed in the wrong order, and Daisy the Bee "
              "cannot make honey until the rows are fixed.",
        talk=["Daisy: Buzz buzz! My garden used to follow a pattern, but the storm broke it!",
              "{hero}: What is a pattern, Daisy?",
              "Daisy: It is something that repeats again and again, like red, yellow, red, yellow... What comes next?",
              "{hero}: Let's find the missing flowers!"],
        win="Buzz buzz hooray! The garden blooms in perfect order and the Pattern Gem sparkles in your hands!"),
    7: dict(
        npc="Tick the Clock Mouse",
        topic="time and order",
        intro="The great Clock Tower stopped at midnight, so the day can never begin! Tick the Clock Mouse "
              "needs someone who knows time and order to fix it.",
        talk=["Tick: Squeak! The clock has stopped and the sun will not come up!",
              "{hero}: Can we fix it, Tick?",
              "Tick: We must read the time and put the day in order: wake up, eat lunch, go to bed.",
              "{hero}: Tick tock, let's go!"],
        win="Tick tock, tick tock! The clock chimes and the Time Gem shines. All seven gems are found. The castle gate is opening..."),
    8: dict(
        npc="The Muddle King",
        topic="everything (final boss)",
        intro="Seven Rainbow Gems glow in {hero}'s bag. At the top of Muddle Castle, the Muddle King waits on his throne. "
              "This is the FINAL BOSS!",
        talk=[],
        win="The Muddle King is defeated!"),
}

# What each level should ask. No two levels share the same kind of question.
# Use this list in your quiz file so every level has different questions.
LEVEL_QUESTIONS = {
    1: ["Which one is a circle?", "Which shape has 3 sides?", "Find the square.", "Which shape has 4 equal sides?", "What shape is a ball?"],
    2: ["Touch the red flower.", "Which color is the sky?", "What color do blue and yellow make?", "Find the color that matches the banana.", "Which color is the odd one out?"],
    3: ["How many fireflies are there?", "What number comes after 4?", "Which number is bigger, 3 or 7?", "What is 2 + 1?", "Count the trees."],
    4: ["Put the apples in the red basket.", "Which one is the biggest pumpkin?", "Which one is not a vegetable?", "Sort by size: small, medium, big.", "Which basket has too many carrots?"],
    5: ["Which way is left?", "Walk the guardian to the right.", "Is the bridge up or down?", "Follow the arrows to the castle.", "Which way is the opposite of left?"],
    6: ["Red, yellow, red, yellow, what comes next?", "Circle, square, circle, ... ?", "Complete the pattern: big, small, big, ...", "Which flower is missing?", "Which pattern repeats ABC ABC?"],
    7: ["What time does the clock show?", "What do we do first in the morning?", "Which comes after lunch?", "Put the day in order.", "Is it day or night?"],
}

PROLOGUE = [
    ("narrator", "Once upon a time there was a peaceful valley. Shapes, colors and numbers all stayed in order, kept safe by seven Rainbow Gems."),
    ("narrator", "Then the grumpy Muddle King, who lives in a castle far away, sent a giant storm. Everything got mixed up, and the gems vanished!"),
    ("narrator", "In seven corners of the valley, seven friends are waiting for help: Hop the Frog, Grandma Rose, Luna the Firefly, Farmer Joe, Bruno the Troll, Daisy the Bee and Tick the Clock Mouse."),
    ("hero", "I'm {hero}, and I'm going to fix it! Walk with me, and we will win back every gem."),
    ("hero", "Walk to a glowing number to start a world. Use the arrow keys or WASD, and press SPACE. Let's go!"),
]

BOSS_INTRO = [
    ("narrator", "The castle doors swing open. Seven gems glow bright, and a giant golden crown wobbles on a giant throne..."),
    ("boss", "WHO DARES enter my Muddle Castle? I mixed up your shapes, I scrambled your numbers, and nobody can ever fix them!", "angry"),
    ("hero", "We found all seven Rainbow Gems! Hop, Grandma Rose, Luna, Joe, Bruno, Daisy and Tick all helped us. Please, Muddle King, put our world back together."),
    ("boss", "NEVER! Nobody ever plays with me, so I made everything a MUDDLE! Answer my riddles if you can!", "angry"),
    ("hero", "Easy! Shapes, colors, numbers, directions, patterns and time. My friends taught me them all. Let's go!"),
    ("narrator", "Every right answer breaks the Muddle King's spell. A wrong answer costs a heart, so think carefully, adventurer!"),
]

VICTORY = [
    ("boss", "Oof! My muddle spell... it's breaking apart!", "defeated"),
    ("narrator", "The seven Rainbow Gems blaze with light. Shapes, colors and numbers swirl back to where they belong."),
    ("boss", "Everybody always said I was too grumpy to play with. So I mixed up the world, and then nobody could leave me alone...", "sad"),
    ("hero", "You didn't need a storm, Muddle King. You just needed a friend! Do you want to learn with us?"),
    ("boss", "Really? Me? ...Then I'm sorry. I will put it all back. And I would love to learn my shapes!", "happy"),
]

ENDING = [
    ("narrator", "The Muddle King gave back every shape, every color and every number. The valley was bright again."),
    ("narrator", "Hop crossed the river with a splash. Grandma Rose hugged Mittens. Luna and the fireflies counted to ten. Farmer Joe's baskets were full."),
    ("narrator", "Bruno waved from his bridge, Daisy's garden bloomed in a perfect pattern, and Tick rang the Clock Tower for a happy good morning."),
    ("boss", "I am the Muddle King no more! Call me the Learning King, and I'll help everyone practice.", "happy"),
    ("hero", "Shapes, colors, numbers, sorting, directions, patterns and time. Together we can learn anything!"),
    ("end", ""),
]

BOSS_PHASES = [
    ("Shapes and Colors", "Hah! My jumbled shapes and colors will trick you!"),
    ("Numbers", "Ouch! But can you count my muddled numbers?"),
    ("Directions and Patterns", "Impossible! Try my twisty directions and patterns!"),
    ("Time", "My last riddle... the stopped clock! You can never win!"),
]