MasterCut Structure

- src
  - __init__.py
  - MasterCut.py    (main)

  - - - Configuration/ - - -

  - Configuration/
    > Type definitions and settings management
    - DataTypes/
      > Data storage objects that will contain information
      - AudioDevice.py
        > Abstract for audio recording settings
        - AudioOutput.py
          > Object to store settings strings for recording an audio output. I.E. game audio or desktop audio
        - AudioInput.py
          > Object to store settings strings for recording an audio input. I.E. mic audio
      - Window.py
        > A configuration object containing an method for identifying a window, and the strings used to do so
    - Config/
      > Control and manage settings
      - Config.py
        > App Settings management
      - ReadWrite.py
        > disk settings management with Pydantic

  - - - Background Detection/ - - -

  - Background Detection/
    > Detection of applications and widow focus
    - Window.py   (abstract)
      > Contains extendable code stubs for finding a widow based on a Window object strings 
    - Detection.py   (abstract)
      > Provides an extendable stub object that has methods to allow window detection and trigger recordings

  - - - UI/ - - -

  - UI/
    > User Interface
    - Common/
      > CSS Themes and reusable objects
      - Widgets.css.py
        > Qt CSS strings for common widgets. I.E. widget, scroll bars, etc
      - Buttons.css.py
        > Qt CSS strings for buttons and other menus
      - Containers.css.py
        > Qt CSS strings for container like objects
    - Editor/
      > Video editor Widgets
      - VideoTrack.py
        > Widget that is a slider bar with playback head, start slider, end slider
      - VideoPlayer.py
        > Widget that plays a video
      - AudioTrack.py
        > An audio track widget placed in-line with the video track.
    - Settings/
      - Settings.py
        > Main settings widow
      - Recording.py
        > Recording Settings
      - Storage.py
        > Storage settings. 
    - Library/
      > Library of videos for selection of clips. 
      - Library.py
        > Scroll grid that stores clickable video previews. Clicking opens that video in editor 
      - VideoPreview.py
        > Video thumbnail for use in library
    - Resources/
      - Icons/
        > Icons  TODO
    - SystemTray.py
      > System tray object that cotains actions and the options to open or exit.

  - - - Recorder/ - - -

  - Recorder/
    > Handles recording a frame and concatenating chunks into a clip
    - WindowProvider.py  (abstract)
      > Handles gathering the needed information to record a window and provideds it to OBS.py
    - OBS.py
      > Handles recording video and audio
    - Buffer.py
      > Manages the rolling buffer, maintaining a set length
    - Clipper.py  
      > Handles gathering chunks from rolling buffer and combining them into a clip.  

  - - - Platforms - - -

  - Platforms/
    > Platform specific modules that inherit functionality from abstracts located somewhere else
    - Windows/
      - Recorder/
        - WindowProvider.py
          > Converts window detection strings in Window objects into windows to be recorded with libobs
        - Recorder.py
          > Records a window from the WindowProvider using libobs
      - Detection/
        - Detection.py
          > Window detection based on the rules settings using a windows API
    - Linux X11/
      - Recorder/
        - WindowProvider.py
          > Converts window detection strings in Window objects into windows to be recorded with libobs
        - Recorder.py
          > Records a window from the WindowProvider using libobs
      - Detection/
        - Detection.py
          > Window detection based on the rules settings using X11 module

- - - Video File Structure - - -

# Video File Structure

- Buffer/
  > Stores a rolling buffer of 1-5sec long segments that can be appended to make a clip.
  - buf0.mkv
  - buf1.mkv
  - buf2.mkv 
  - buf3.mkv
  - buf4.mkv
- Clips/
  - Exported/
    > Stores Clips exported by the user, format Clip_<name>_<ID:3>.<format>
    - Clip_MyGameClip1_KRY.mp4
    - Clip_MyGameClip2_KRY.mp4
    - Clip_EpicClip26_KRY.mp4
  - Apps/
    > Stores Clips captured. Organized by game, stored with a Clip<ID:6>.mkv
    - GameA/
      - ClipAKUV7D.mkv
      - ClipLI5HR4.mkv
    - GameB/
      - ClipPJ6HV3.mkv
