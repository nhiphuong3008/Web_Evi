import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

moon_official_syllabus = {
    # MOON 1
    "Moon 1": {
        "Unit 01": {
            "title": "MOON 1 UNIT TEST",
            "subtitle": "UNIT 1: CLASSROOM RULES & FRIENDS",
            "vocab": ["Be quiet", "Speak English", "No Fighting", "Sit nicely", "I can", "Mimi", "Dylan", "Mommy", "Daddy", "Boy", "Girl", "Red", "Ferris Wheel"],
            "phonics": ["Letter A - /a/(Apple, Ant, Annie Ant)", "Letter B - /b/(Bear, ball, Benny Bear)"],
            "struct": ["Hello! I'm.....", "Who is it? It's...."]
        },
        "Unit 02": {
            "title": "MOON 1 UNIT TEST",
            "subtitle": "UNIT 2: FAMILY",
            "vocab": ["Mommy", "Daddy", "Grandma", "Grandpa", "Brother", "Sister", "Round", "Wheel", "Red", "Yellow", "Orange", "Pink"],
            "phonics": ["Letter C - /k/(Cat, cut, Candy cat)", "Letter D - /d/(Dog, dig, Danny dog)"],
            "struct": ["What colour is it? It's...", "Where is mommy? Here! (point)"]
        },
        "Unit 03": {
            "title": "MOON 1 UNIT TEST",
            "subtitle": "UNIT 3: CLASSROOM",
            "vocab": ["Book", "Crayon", "Eraser", "Pencil", "Table", "Chair", "Blue", "Shelf", "Tray"],
            "phonics": ["Letter C - /c/(Cut, Candy, Candy Cat)", "Letter D - /d/(Dog, dig, Danny Dog)"],
            "struct": ["What's is this? It's a...."]
        },
        "Unit 04": {
            "title": "MOON 1 UNIT TEST",
            "subtitle": "UNIT 4: MY FACE",
            "vocab": ["Ear", "Eye", "Hair", "Mouth", "Nose", "Teeth", "Hear", "See"],
            "phonics": ["Letter E - /e/(Elephant, egg, Eddie elephant)"],
            "struct": ["I have (a nose).", "I have (two) (eyes)."]
        },
        "Unit 05": {
            "title": "MOON 1 UNIT TEST",
            "subtitle": "UNIT 5: CLOTHES",
            "vocab": ["Hat", "Shirt", "Pants", "Shoes", "Socks", "Dress", "Coat", "Blue", "Green", "Purple", "Clean", "Dirty"],
            "phonics": ["Letter I - /i/(Ink, Insect)", "Letter J - /dʒ/(Jam, Juice)"],
            "struct": ["Put on your.....", "Take off your....."]
        },
        "Midterm test": {
            "title": "MOON 1 MIDTERM TEST",
            "subtitle": "MOON 1 MIDTERM TEST REVIEW (UNITS 1 - 3)",
            "vocab": ["Book", "Crayon", "Eraser", "Pencil", "Table", "Chair", "Mommy", "Daddy", "Grandma", "Grandpa", "Brother", "Sister", "Ear", "Eye", "Nose", "Mouth", "Hat", "Shirt", "Pants", "Shoes"],
            "phonics": ["Letter A - /a/ (Apple)", "Letter B - /b/ (Bear)", "Letter C - /k/ (Cat)", "Letter D - /d/ (Dog)", "Letter E - /e/ (Elephant)"],
            "struct": ["What's this? It's a...", "Who is it? It's...", "What colour is it? It's...", "I have (two eyes)."]
        },
        "Final test": {
            "title": "MOON 1 FINAL TEST",
            "subtitle": "MOON 1 FINAL TEST REVIEW (UNITS 1 - 5)",
            "vocab": ["Book", "Pencil", "Mommy", "Daddy", "Ear", "Eye", "Hat", "Shirt", "Socks", "Red", "Yellow", "Blue", "Green"],
            "phonics": ["Review Letters A to J"],
            "struct": ["What's this? It's a...", "Put on your...", "I have..."]
        }
    },
    # MOON 2
    "Moon 2": {
        "Unit 06": {
            "title": "MOON 2 UNIT TEST",
            "subtitle": "UNIT 6: TOYS",
            "vocab": ["Ball", "Car", "Teddy", "Doll", "Scooter", "Train", "Classroom", "Playground", "Play", "Work"],
            "phonics": ["Letter I - /i/(Insect, ill, Ian insect)", "Letter J - /j/(Jellyfish, jump, Jane jellyfish)"],
            "struct": ["What toy is it? It's a….", "Where is the (car)? Here!"]
        },
        "Unit 07": {
            "title": "MOON 2 UNIT TEST",
            "subtitle": "UNIT 7: FOOD",
            "vocab": ["Apple", "Banana", "Cookie", "Juice", "Sandwich", "Water", "Drink", "Eat"],
            "phonics": ["Letter K - /k/(Kangaroo, kick, Kenny Kangaroo)", "Letter J - /j/(Jellyfish, jump, Jane jellyfish)"],
            "struct": ["What food is it? It's....", "Do you like (bananas)? I like (bananas)."]
        },
        "Unit 08": {
            "title": "MOON 2 UNIT TEST",
            "subtitle": "UNIT 8: PETS",
            "vocab": ["Bird", "Cat", "Dog", "Fish", "Mouse", "Rabbit", "Fly", "Swim"],
            "phonics": ["Letter L - /l/(Lion, leg, Larry lion)", "Letter K - /k/(Kangaroo, kick, Kenny Kangaroo)"],
            "struct": ["What animal is it? (It's)....", "Is it a (rabbit)? Yes, it is/ No, it isn't."]
        },
        "Unit 09": {
            "title": "MOON 2 UNIT TEST",
            "subtitle": "UNIT 9: BEACH",
            "vocab": ["Crab", "Ocean", "Sand", "Shell", "Bucket", "Shovel", "Land", "Water"],
            "phonics": ["Letter M - /m/(Money, mouth, Mickey monkey)", "Letter L - /l/(Lion, leg, Larry lion)"],
            "struct": ["What's it? (It's)...", "What can you see? (I can see) a shell."]
        },
        "Midterm test": {
            "title": "MOON 2 MIDTERM TEST",
            "subtitle": "MOON 2 MIDTERM TEST REVIEW (UNITS 6 - 7)",
            "vocab": ["Ball", "Car", "Teddy", "Doll", "Scooter", "Train", "Apple", "Banana", "Cookie", "Juice", "Sandwich", "Water"],
            "phonics": ["Letter I - /i/ (Insect)", "Letter J - /j/ (Jellyfish)", "Letter K - /k/ (Kangaroo)", "Letter L - /l/ (Lion)"],
            "struct": ["What toy is it? It's a...", "Do you like (bananas)? I like...", "Where is the (car)? Here!"]
        },
        "Final test": {
            "title": "MOON 2 FINAL TEST",
            "subtitle": "MOON 2 FINAL TEST REVIEW (UNITS 6 - 9)",
            "vocab": ["Ball", "Car", "Apple", "Cookie", "Bird", "Cat", "Dog", "Fish", "Crab", "Ocean", "Shell", "Bucket"],
            "phonics": ["Review Letters I to M"],
            "struct": ["Is it a (rabbit)? Yes, it is.", "What can you see? I can see a..."]
        }
    },
    # MOON 3
    "Moon 3": {
        "Unit 01": {
            "title": "MOON 3 UNIT TEST",
            "subtitle": "UNIT 1: HELLO",
            "vocab": ["We are quiet", "We speak English", "We don't fight", "We sit nicely", "We can", "Mommy", "Daddy", "Mimi", "Dylan", "Ferris Wheel", "Ball", "Car", "Doll", "Teddy", "Train", "Scooter"],
            "phonics": ["Letter N - /n/(Nose, Nurse, Nancy Nurse)", "Letter O - /o/(Octopus, on, Oscar Octopus)"],
            "struct": ["Who is this? (This is)....", "Where's the (ball)? Here's the (ball)!"]
        },
        "Unit 02": {
            "title": "MOON 3 UNIT TEST",
            "subtitle": "UNIT 2: CLASSROOM",
            "vocab": ["Backpack", "Crayons", "Glue", "Paints", "Paper", "Pencil", "Pencil case", "Scissors", "Cafeteria", "Classroom", "Library", "Playground"],
            "phonics": ["Letter P - /p/(Pen, panda, Penny Panda)", "Letter Q - /k/(Queen, quiet, Queenie Quick)"],
            "struct": ["What do you have? I have...", "Do you have a pencil? Yes/No"]
        },
        "Unit 03": {
            "title": "MOON 3 UNIT TEST",
            "subtitle": "UNIT 3: MY BODY",
            "vocab": ["Arms", "Feet", "Hands", "Leg", "Tummy", "fingers", "Toes", "Climb", "Hop", "Jump", "Run"],
            "phonics": ["Letter R - /r/(Rabbit, read, Ricky rabbit)", "Letter S - /s/(Sun, seal, Susie Seal)"],
            "struct": ["What can you do? I can move my (fingers)"]
        },
        "Unit 04": {
            "title": "MOON 3 UNIT TEST",
            "subtitle": "UNIT 4: CLOTHES",
            "vocab": ["Coat", "Dress", "Pants", "Shirt", "Shoes", "Skirt", "Socks", "Sweater", "Glove", "Sandals", "Scarf", "T-shirt"],
            "phonics": ["Letter T - /t/(Tiger, teeth, Teddy Tiger)", "Letter U - /u/(Uncle, under, Uncle Utter)"],
            "struct": ["What's this/are these? This is a (skirt). These are (shoes)", "What are you wearing? (I'm wearing) a ..."]
        },
        "Unit 05": {
            "title": "MOON 3 UNIT TEST",
            "subtitle": "UNIT 5: HOME",
            "vocab": ["Bathroom", "Bedroom", "Dining room", "Garage", "House", "Kitchen", "Living room", "Yard", "Box", "Closet", "Shelf", "Recycling bin"],
            "phonics": ["Letter V - /v/(Van, Violin)", "Letter W - /w/(Water, Watch)"],
            "struct": ["What room is it? It's....", "Where’s (the box)? In the...."]
        },
        "Midterm test": {
            "title": "MOON 3 MIDTERM TEST",
            "subtitle": "MOON 3 MIDTERM TEST REVIEW (UNITS 1 - 3)",
            "vocab": ["Backpack", "Crayons", "Glue", "Pencil", "Scissors", "Arms", "Feet", "Hands", "Leg", "Tummy", "fingers", "Toes"],
            "phonics": ["Letter N - /n/ (Nose)", "Letter O - /o/ (Octopus)", "Letter P - /p/ (Pen)", "Letter Q - /k/ (Queen)", "Letter R - /r/ (Rabbit)", "Letter S - /s/ (Sun)"],
            "struct": ["What do you have? I have...", "What can you do? I can move my...", "Do you have a pencil?"]
        },
        "Final test": {
            "title": "MOON 3 FINAL TEST",
            "subtitle": "MOON 3 FINAL TEST REVIEW (UNITS 1 - 5)",
            "vocab": ["Pencil", "Scissors", "Arms", "Leg", "Coat", "Dress", "Pants", "Kitchen", "Living room", "Bedroom", "Yard"],
            "phonics": ["Review Letters N to W"],
            "struct": ["What are you wearing? I'm wearing...", "Where's the (box)? In the..."]
        }
    },
    # MOON 4
    "Moon 4": {
        "Unit 06": {
            "title": "MOON 4 UNIT TEST",
            "subtitle": "UNIT 6: FOOD",
            "vocab": ["Apples", "Bananas", "Bread", "Carrots", "Cereal", "Eggs", "Ice cream", "Milk", "Pears", "Peas", "Potatoes", "Tomatoes"],
            "phonics": ["Letter V - /v/(Van, victory, Vicky Van)", "Letter W - /w/(Worm, wet, Wendy worm)"],
            "struct": ["What's this? It's…..", "Do you like…? I like/ don't like…."]
        },
        "Unit 07": {
            "title": "MOON 4 UNIT TEST",
            "subtitle": "UNIT 7: FARM ANIMALS",
            "vocab": ["Cow", "Duck", "Goat", "Hen", "Horse", "Rooster", "Sheep", "Calf", "Dog", "Puppy", "Foal", "Lamb"],
            "phonics": ["Letter X - /ks/(Fox, box, Felix fox)", "Letter V - /v/(Van, victory, Vicky Van)"],
            "struct": ["What animals is it? Its'….", "There is/are cow(s)."]
        },
        "Unit 08": {
            "title": "MOON 4 UNIT TEST",
            "subtitle": "UNIT 8: TRANSPORTATION",
            "vocab": ["Boat", "Bus", "Motorbike", "Plane", "Train", "Truck", "Air", "Road", "Track", "Water", "Bike", "Car"],
            "phonics": ["Letter Y - /y/(Yo-yo, yes, Yester Yo-yo)", "Letter W - /w/(Worm, wet, Wendy worm)"],
            "struct": ["What's it? It's a…..", "Do you want to go by (bus)? Yes/No"]
        },
        "Unit 09": {
            "title": "MOON 4 UNIT TEST",
            "subtitle": "UNIT 9: SPACE",
            "vocab": ["Astronaut", "Moon", "Planet", "Rocket", "Star", "Sun", "Day", "Night", "Clouds", "Rainbow", "Sky"],
            "phonics": ["Letter Z - /z/(Zebra, zip, Zeppy Zebra)"],
            "struct": ["What's it? It's a…..", "In the day/night, what can you see?"]
        },
        "Midterm test": {
            "title": "MOON 4 MIDTERM TEST",
            "subtitle": "MOON 4 MIDTERM TEST REVIEW (UNITS 6 - 7)",
            "vocab": ["Apples", "Bananas", "Bread", "Eggs", "Milk", "Cow", "Duck", "Goat", "Hen", "Horse", "Rooster", "Sheep"],
            "phonics": ["Letter V - /v/ (Van)", "Letter W - /w/ (Worm)", "Letter X - /ks/ (Fox)"],
            "struct": ["Do you like...? I like/don't like...", "What animal is it? It's...", "There is/are cow(s)."]
        },
        "Final test": {
            "title": "MOON 4 FINAL TEST",
            "subtitle": "MOON 4 FINAL TEST REVIEW (UNITS 6 - 9)",
            "vocab": ["Apples", "Cow", "Duck", "Boat", "Bus", "Motorbike", "Plane", "Astronaut", "Moon", "Planet", "Rocket", "Star"],
            "phonics": ["Review Letters V to Z"],
            "struct": ["Do you want to go by (bus)?", "In the day/night, what can you see?"]
        }
    },
    # MOON 5
    "Moon 5": {
        "Unit 02": {
            "title": "MOON 5 UNIT TEST",
            "subtitle": "UNIT 2: SCHOOL",
            "vocab": ["Colour", "Count", "Draw", "Paint", "Play", "Sing", "Dance", "Jump", "Run", "Think", "Swim", "Walk"],
            "phonics": ["Short vowel a: ham, ram, dam, jam", "Short vowel e: bed, red, leg, egg"],
            "struct": ["What do you do at school? I .... at school.", "Do you want to…? Yes, I do/No, I don't."]
        },
        "Unit 03": {
            "title": "MOON 5 UNIT TEST",
            "subtitle": "UNIT 3: THE PARK",
            "vocab": ["Bench", "Flowers", "Grass", "Merry-go-round", "Path", "Pond", "Seesaw", "Slide", "Swing", "Tree", "Leave", "Plants", "Root", "Seed", "Sun", "Water"],
            "phonics": ["Short vowel i: bib, nib, lid, kid", "Short vowel i: lip, rip, hit, sit"],
            "struct": ["There is a (pond).", "There are (trees)."]
        },
        "Unit 04": {
            "title": "MOON 5 UNIT TEST",
            "subtitle": "UNIT 4: WILD ANIMALS",
            "vocab": ["Elephant", "Giraffe", "Hippo", "Monkey", "Parrot", "Snake", "Tiger", "Zebra"],
            "phonics": ["Short vowel o: dog, jog, log", "Short vowel o: pot, hot, dot"],
            "struct": ["What's it? It's a…..", "What are those? They're....", "It has (big teeth/big ears/...)."]
        },
        "Midterm test": {
            "title": "MOON 5 MIDTERM TEST",
            "subtitle": "MOON 5 MIDTERM TEST REVIEW (UNITS 2 - 4)",
            "vocab": ["Bench", "Flowers", "Grass", "Elephant", "Giraffe", "Hippo", "Colour", "Count", "Draw"],
            "phonics": ["Short vowels Review"],
            "struct": ["There is a (pond).", "What do you do at school?"]
        },
        "Final test": {
            "title": "MOON 5 FINAL TEST",
            "subtitle": "MOON 5 FINAL TEST REVIEW (UNITS 2 - 5)",
            "vocab": ["Bench", "Flowers", "Elephant", "Giraffe", "Colour", "Count", "Draw", "Paint"],
            "phonics": ["Short vowels Review"],
            "struct": ["There is a (pond).", "What do you do at school?"]
        }
    }
}

with open("static/js/moon_syllabus_db.json", "w", encoding="utf-8") as out:
    json.dump(moon_official_syllabus, out, ensure_ascii=False, indent=2)

print("Updated official Moon syllabus map with Midterm & Final test definitions in static/js/moon_syllabus_db.json!")
