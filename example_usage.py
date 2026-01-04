"""
Voorbeeld gebruik van de Music Analyzer
"""

from music_analyzer import analyze_track, batch_analyze

# Voorbeeld 1: Analyseer één track
# Vervang 'track1.mp3' met het pad naar jouw audio bestand
# analyze_track("track1.mp3")

# Voorbeeld 2: Analyseer één track zonder visualisatie
# analyze_track("track1.mp3", visualize=False)

# Voorbeeld 3: Analyseer één track met aangepaste drempel
# analyze_track("track1.mp3", energy_threshold=0.7)

# Voorbeeld 4: Batch analyse van alle tracks in een folder
# batch_analyze("tracks/")

# Voorbeeld 5: Batch analyse met aangepaste output naam
# batch_analyze("tracks/", output_file="mijn_analyses.json")

print("Dit is een voorbeeld bestand.")
print("Uncomment de regels hierboven om de analyzer te gebruiken.")
print("\nOf gebruik direct vanuit de command line:")
print("  python music_analyzer.py track1.mp3")
print("  python music_analyzer.py --batch tracks/")



