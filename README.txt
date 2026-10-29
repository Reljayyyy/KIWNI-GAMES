KWIN'S GREAT ADVENTURE
Run:  pip install pygame
      python main.py        (run it from inside this folder)

Controls: arrows / WASD walk, SPACE talk + enter, mouse or 1-4 to answer, ESC menu/skip, F11 full screen.

STORY: the Muddle King mixed up the world and hid 7 Rainbow Gems. Win a gem in each of the first 7 worlds,
then beat the Muddle King in the final boss battle (level 8) to bring everything back.

main.py       start here
game.py       Game class: menus, hero choice, walking, level flow, result screen
story.py      ALL story text (levels, prologue, boss intro, victory, ending). Edit this to change the story.
settings.py   constants, colours, level list (NODES), gem names, CREATOR name (change this to your name)
menu_ui.py    title-screen look: animated backdrop, buttons, outlined text
sprites.py    the 4 playable heroes (Kwin, Kai, Mira, Leo) + assets/player.png loader
bossart.py    the Muddle King drawn in code (5 moods)
cutscene.py   story scenes with portraits + the animated THE END screen
boss.py       final boss battle (health bar, hearts, 4 phases)
world.py      village map, collision, buildings
questions.py  question generators for the multiple-choice levels
quiz.py       multiple-choice scene
sorting.py    drag-and-drop scene (level 4)
helpers.py    drawing and text helpers
audio.py      generated sound effects + looping background music (menu, quiz, boss)
storage.py    save.json (progress, chosen hero, settings)

TURN IT INTO AN APP (Windows)
  1. Open this folder in VS Code, open the terminal (Ctrl + `)
  2. Type:   .\build.bat
  3. Your app appears at:  dist\KwinsGreatAdventure.exe   (it already has the Kwin icon)
  Share that file (zip it first if you email it). Friends do NOT need Python installed.
  Optional: installer.iss makes a "Setup" installer with Inno Setup (free).
  Progress is saved in your AppData folder, so it is kept between plays.
  If the app closes instantly, rebuild without --windowed (edit build.bat) to see the error message.
  macOS / Linux: run  sh build.sh  on that computer (an app must be built on the system it will run on).

new files: build.bat, build.sh, installer.iss, requirements.txt, assets/icon.png, assets/icon.ico
