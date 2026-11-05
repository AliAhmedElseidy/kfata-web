# Original architectural construction scene

The owner approved the existing direction and requested final activation on 2026-11-05. Approved media and decoded properties are in assets/construction-scene/. This is an illustrative concept, not a KFATA project. The unavailable reference clips were not copied or used as source frames.

The original running render completed 168 full-resolution frames. It was inspected and awaited after the interruption; no second render was launched. Final output is 7s/24fps, desktop 1280x720 and mobile 960x540, H.264 fast-start with no audio. Mobile is downsampled from the same original frames, keeping the complete building visible.

Production code: home/templates/home/scene_hero.html, config/static/js/construction-scene.js and home/scene.py. Every fresh document starts once on every load, without session/cookie/storage gates. autoplay/muted/playsinline is present; script selects one appropriate video after reduced-motion/master-animation checks. End holds the completed poster; a small native button provides pause/resume/replay. Rejected playback, disabled scripting and reduced motion keep the poster and working HTML links. The old once/session preview code was removed.

Brand settings provide activation, desktop/mobile documents, desktop/mobile posters and bilingual disclosure. Upload public MP4/H.264 fast-start files up to 6MB. Restricted collections are rejected and never exposed by the scene route. Selected videos support bounded HTTP ranges and HEAD. Public image serving/private enquiry storage remain unchanged.

install_construction_scene is read-only by default. --apply --enable imports approved media once and activates both home languages, without saving home revisions or resetting old brand/SMTP settings. A marker and existing-configuration guard preserve later owner edits, including cleared fields. Subsequent changes belong in the panel.

Optional future reproduction: first confirm no Blender render is running. Build the model with build_concept.py, then load that .blend in Blender and run render_final.py -- --output ABS_FRAME_DIRECTORY. Encode using python tools/scene/encode_final.py FRAME_DIRECTORY assets/construction-scene. Blender and optional local imageio-ffmpeg/Pillow are offline authoring dependencies; no renderer/transcoder is installed on the VPS or visitor path. The encoder verifies all 168 original frames, dimensions, 24fps, 7s and zero audio. Browser recordings are captured separately from the actual site.

Local review: python manage.py runserver 127.0.0.1:8035 --noreload --settings=tools.scene.preview_settings. The /scene-preview/ar/ and /en/ routes now share the actual homepage implementation; those review routes are absent from production. Do not rerun legacy seed commands. See docs/CONSTRUCTION_DELIVERY.md for final deployment/browser evidence.
