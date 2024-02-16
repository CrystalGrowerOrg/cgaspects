mkdir CGAspects.iconset
sips -z 16 16     CGAspects.png --out CGAspects.iconset/icon_16x16.png
sips -z 32 32     CGAspects.png --out CGAspects.iconset/icon_16x16@2x.png
sips -z 32 32     CGAspects.png --out CGAspects.iconset/icon_32x32.png
sips -z 64 64     CGAspects.png --out CGAspects.iconset/icon_32x32@2x.png
sips -z 128 128   CGAspects.png --out CGAspects.iconset/icon_128x128.png
sips -z 256 256   CGAspects.png --out CGAspects.iconset/icon_128x128@2x.png
sips -z 256 256   CGAspects.png --out CGAspects.iconset/icon_256x256.png
sips -z 512 512   CGAspects.png --out CGAspects.iconset/icon_256x256@2x.png
sips -z 512 512   CGAspects.png --out CGAspects.iconset/icon_512x512.png
sips -z 1024 1024 CGAspects.png --out CGAspects.iconset/icon_512x512@2x.png
iconutil -c icns CGAspects.iconset
rm -rf CGAspects.iconset
