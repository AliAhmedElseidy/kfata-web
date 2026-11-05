# Local architectural concept preview

This original procedural scene is a review prototype, not a KFATA building or a final photoreal architectural film. It uses no reference-video frames, external models or external textures. The supplied 508810/508807 clips were unavailable in this execution session; the documented stage sequence was used. The construction sequence is an actual offline 3D render, not visitor-side 3D, a logo animation or CSS cubes.

The preview movie is 7s / 768×432 / 12fps / H.264 / 227,173 bytes. Final poster is 1280×720. It has foundations, columns, slabs, walls, glazing/mullions, timber fins, arrival steps, water, planting and linear lighting. It is a first art-direction review; materials, architectural detail and final-frame composition can be refined before a final-resolution render.

The local artifacts live in ignored `operations/scene-preview/`: original `.blend`, rendered PNG sequence, movie, poster, 8.5s actual browser recording (`homepage-browser-preview.mp4`), timing JSON and screenshots. No generated scene imagery/movie has been uploaded to GitHub or production pending owner review. Existing approved company photographs remain in the real portfolio.

Render source with a trusted Blender 4.5 installation (this session used official portable 4.5.9, outside the repository):

```powershell
blender -b -t 4 --python tools/scene/build_concept.py -- --output D:/kfata-web/operations/scene-preview
blender -b operations/scene-preview/kfata-concept.blend -t 4 -f 168
```

For a quick draft, open the saved scene with an offline Blender script setting `render.resolution_percentage=60`, `cycles.samples=6`, `frame_step=2`, `frame_end=167`, and the output prefix to `draft-frames/frame-`, then render animation. The optional local encoder uses imageio-ffmpeg; it is not a project/server dependency. Export the final frame as `poster.jpg`, then:

```powershell
python tools/scene/encode_preview.py operations/scene-preview
python manage.py runserver 127.0.0.1:8035 --noreload --settings=tools.scene.preview_settings
```

Visit `http://127.0.0.1:8035/scene-preview/ar/` or `/en/`; `?nojs=1` adds local script-blocking CSP. These routes are absent from production URL configuration. The template uses existing Wagtail home content and shared header/footer, on the local database. Do not reseed the live database. The local snapshot has no protected owner English tower revision; production still does.

The player is muted/inline, first-play once per session, pause/replay, completed-building skip/poster and no-JS/reduced-motion fallback. With actual OS reduced motion, the video src remains unset. This is preview-only integration: production CMS selection/activation and final mobile/desktop delivery formats must be completed after the scene direction is accepted. No production motion deployment is claimed.
