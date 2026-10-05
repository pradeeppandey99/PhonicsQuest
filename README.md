# Phonics Quest

A free, single-page phonics game for young children learning to read English, with a short baseline check and a progress dashboard for the grown-up.

**Everything stays in the browser it is opened in.** There is no account, no server and no tracking. Progress and any recorded voices are stored in that browser only.

## Learn mode
A short lesson teaches new sounds before they are tested, two at a time: meet the letter and its picture, do a hand action, say the sound together, find it among other letters, then hear words that start with it. Detective Day marks sounds she already knows as learned, so lessons start from what she does not know yet. Games then use only learned sounds (a setting, on by default once four are learned).

## Games
- **Pop:** hear a sound, tap the letter.
- **Robot:** the robot says the sounds one at a time; the child blends them and taps the picture.
- **Build:** tap the sounds in order to build a word.
- **Magic:** change one letter to make a new word.
- **Silly:** read made-up words (a grown-up confirms).

## For the grown-up (behind a quick sum)
- **Detective Day:** seven short checks that give a baseline and can be repeated every two weeks.
- **Progress:** baseline against now, a letter map and recent activity.
- **Voices:** record the letter sounds, the game instructions and short **praise lines** (for example "Shabash!") in your own voice, in any language.
- **Settings:** name, level, backup and restore.

## Run it
Open `index.html` through a local server (the microphone and saved progress work best that way):

    python -m http.server 8765

then visit `http://localhost:8765/`. On Windows, `Open Phonics Quest.cmd` does this.

## Notes
- Sounds: until letter sounds are recorded, the computer voice is a weak substitute. Record them once for best results.
- The computer voice cannot be louder than the device volume. Recorded voices can be boosted in the in-app sound panel.

## If there is no sound on a phone
1. Open the page in Chrome (Android) or Safari (iPhone), not inside WhatsApp or another chat app.
2. Turn the media volume up; on an iPhone, switch the silent switch off.
3. Tap the 🔊 button at the top of any screen: it shows how many recorded voices are on this device and whether the computer voice was found. Tap Test.
4. Recordings made on a laptop do not exist on the phone. On the laptop: Grown-ups > Settings > Download backup (it includes the recorded voices). Send the file to the phone and use Restore backup there. On an iPhone, voices recorded in Chrome on a laptop may not play: record them on the phone itself.
