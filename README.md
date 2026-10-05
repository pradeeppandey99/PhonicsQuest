# Phonics Quest

A free, single-page phonics game for young children learning to read English, with a short baseline check and a progress dashboard for the grown-up.

**Everything stays in the browser it is opened in.** There is no account, no server and no tracking. Progress and any recorded voices are stored in that browser only.

## Games
- **Pop:** hear a sound, tap the letter.
- **Robot:** the robot says the sounds one at a time; the child blends them and taps the picture.
- **Build:** tap the sounds in order to build a word.
- **Magic:** change one letter to make a new word.
- **Silly:** read made-up words (a grown-up confirms).

## For the grown-up (behind a quick sum)
- **Detective Day:** seven short checks that give a baseline and can be repeated every two weeks.
- **Progress:** baseline against now, a letter map and recent activity.
- **Voices:** record the letter sounds and the game instructions in your own voice (any language).
- **Settings:** name, level, backup and restore.

## Run it
Open `index.html` through a local server (the microphone and saved progress work best that way):

    python -m http.server 8765

then visit `http://localhost:8765/`. On Windows, `Open Phonics Quest.cmd` does this.

## Notes
- Sounds: until letter sounds are recorded, the computer voice is a weak substitute. Record them once for best results.
- The computer voice cannot be louder than the device volume. Recorded voices can be boosted in the in-app sound panel.
