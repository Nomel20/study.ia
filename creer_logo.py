from PIL import Image, ImageDraw

K = 8
N = 256 * K


def p(*points):
    return [(x * K, y * K) for x, y in points]


# Fond dégradé violet -> cyan
petit = Image.new("RGB", (256, 256))
px = petit.load()
c1, c2 = (124, 58, 237), (6, 182, 212)
for y in range(256):
    for x in range(256):
        t = (x + y) / 510
        px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
fond = petit.resize((N, N), Image.BILINEAR).convert("RGBA")

# Carré aux coins arrondis
masque = Image.new("L", (N, N), 0)
ImageDraw.Draw(masque).rounded_rectangle((0, 0, N - 1, N - 1), radius=56 * K, fill=255)

logo = Image.new("RGBA", (N, N), (0, 0, 0, 0))
logo.paste(fond, (0, 0), masque)
d = ImageDraw.Draw(logo)

# Livre ouvert
d.polygon(p((128, 104), (96, 92), (44, 98), (44, 192), (96, 186), (128, 200)), fill=(255, 255, 255, 255))
d.polygon(p((128, 104), (160, 92), (212, 98), (212, 192), (160, 186), (128, 200)), fill=(224, 231, 255, 255))

# Lignes de texte sur les pages
for y in (122, 140, 158):
    d.line(p((60, y), (110, y - 4)), fill=(124, 58, 237, 255), width=5 * K)
    d.line(p((146, y - 4), (196, y)), fill=(124, 58, 237, 255), width=5 * K)

# Étincelle au-dessus du livre
d.polygon(
    p((128, 30), (138, 58), (166, 68), (138, 78), (128, 106), (118, 78), (90, 68), (118, 58)),
    fill=(253, 230, 138, 255),
)

# Enregistrement
logo.resize((512, 512), Image.LANCZOS).save("static/logo.png")
logo256 = logo.resize((256, 256), Image.LANCZOS)
logo256.save("static/logo.ico", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])

print("Logo créé : static/logo.png et static/logo.ico")