Icons directory
===============

Place the following icon files here:

  app_icon.png        — 512x512 app launcher icon (RGBA PNG)
  splash_icon.png     — 256x256 splash screen icon
  ic_video.png        — 48x48 video file icon
  ic_audio.png        — 48x48 audio file icon
  ic_subtitle.png     — 48x48 subtitle icon
  ic_export.png       — 48x48 export icon
  ic_settings.png     — 48x48 settings icon
  ic_history.png      — 48x48 history icon

You can generate these using any image editor or Inkscape.
For the build to succeed you need at minimum app_icon.png (required by buildozer.spec).

A simple placeholder icon can be generated with:

    python -c "
    from PIL import Image, ImageDraw
    img = Image.new('RGBA', (512, 512), (18, 18, 26, 255))
    d = ImageDraw.Draw(img)
    d.ellipse([56, 56, 456, 456], fill=(64, 120, 240, 255))
    d.text((200, 220), 'ODS', fill=(255, 255, 255, 255))
    img.save('app_icon.png')
    "
