#!/usr/bin/env python3
"""
Build script for hp_checkers web release.
Run from the project root with the venv active:
    source ~/venv/bin/activate && python build_web.py
"""
import subprocess
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent

GOOGLE_FONTS = """\
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=Cinzel:wght@400;600&display=swap" rel="stylesheet">"""

CUSTOM_CSS = """\
        #status { display: none; }
        #progress { display: none; }

        #infobox {
            position: fixed;
            bottom: 44px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(5, 5, 18, 0.85);
            color: #c8a84b;
            font-family: 'Cinzel', Georgia, serif;
            font-size: 0.82em;
            letter-spacing: 2px;
            padding: 9px 26px;
            border: 1px solid rgba(200, 168, 75, 0.35);
            white-space: nowrap;
            z-index: 1000001;
        }

        #loading-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: radial-gradient(ellipse at center, #0d0d24 0%, #050510 70%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 1000000;
            overflow: hidden;
        }

        .lo-star {
            position: absolute;
            width: 2px; height: 2px;
            background: white;
            border-radius: 50%;
        }

        @keyframes lo-twinkle {
            0%, 100% { opacity: 0.1; transform: scale(1); }
            50%       { opacity: 1;   transform: scale(1.4); }
        }

        .lo-content {
            position: relative;
            z-index: 2;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .lo-title {
            font-family: 'Cinzel Decorative', Georgia, serif;
            font-size: 2.8em;
            font-weight: 700;
            color: #c8a84b;
            letter-spacing: 3px;
            text-shadow:
                0 0 20px rgba(200, 168, 75, 0.7),
                0 0 50px rgba(200, 168, 75, 0.3),
                0 0 90px rgba(200, 168, 75, 0.1);
            margin-bottom: 10px;
            text-align: center;
        }

        .lo-subtitle {
            font-family: 'Cinzel', Georgia, serif;
            font-size: 0.82em;
            font-weight: 600;
            color: #7a6428;
            letter-spacing: 7px;
            text-transform: uppercase;
            margin-bottom: 36px;
        }

        .lo-divider {
            width: 340px;
            height: 1px;
            background: linear-gradient(to right, transparent, #c8a84b 30%, #c8a84b 70%, transparent);
            margin-bottom: 36px;
            opacity: 0.5;
        }

        .lo-houses {
            display: flex;
            gap: 20px;
            margin-bottom: 48px;
        }

        .lo-house {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
        }

        .lo-bar { width: 60px; height: 5px; border-radius: 3px; }
        .lo-house-name {
            font-family: 'Cinzel', Georgia, serif;
            font-size: 0.6em;
            letter-spacing: 1px;
        }

        .lo-gryff { background: #7a0000; box-shadow: 0 0 8px #7a0000; }
        .lo-slyth { background: #1a472a; box-shadow: 0 0 8px #1a472a; }
        .lo-huff  { background: #ecb939; box-shadow: 0 0 8px #ecb939; }
        .lo-rave  { background: #3a5298; box-shadow: 0 0 8px #3a5298; }

        .lo-gryff-name { color: #c04040; }
        .lo-slyth-name { color: #3a8a5a; }
        .lo-huff-name  { color: #ecb939; }
        .lo-rave-name  { color: #5a72c8; }

        @keyframes lo-spin { to { transform: rotate(360deg); } }

        .lo-spinner {
            width: 52px; height: 52px;
            border: 2px solid rgba(200, 168, 75, 0.1);
            border-top-color: #c8a84b;
            border-right-color: rgba(200, 168, 75, 0.4);
            border-radius: 50%;
            animation: lo-spin 1.2s linear infinite;
            margin-bottom: 28px;
        }

        .lo-note {
            font-family: 'Cinzel', Georgia, serif;
            font-size: 0.68em;
            color: #3a3a5a;
            letter-spacing: 2px;
        }"""

LOADING_HTML = """\
    <div id="loading-overlay">
        <div class="lo-content">
            <div class="lo-title">House Cup Checkers</div>
            <div class="lo-subtitle">Harry Potter Edition</div>
            <div class="lo-divider"></div>
            <div class="lo-houses">
                <div class="lo-house">
                    <div class="lo-bar lo-gryff"></div>
                    <div class="lo-house-name lo-gryff-name">Gryffindor</div>
                </div>
                <div class="lo-house">
                    <div class="lo-bar lo-slyth"></div>
                    <div class="lo-house-name lo-slyth-name">Slytherin</div>
                </div>
                <div class="lo-house">
                    <div class="lo-bar lo-huff"></div>
                    <div class="lo-house-name lo-huff-name">Hufflepuff</div>
                </div>
                <div class="lo-house">
                    <div class="lo-bar lo-rave"></div>
                    <div class="lo-house-name lo-rave-name">Ravenclaw</div>
                </div>
            </div>
            <div class="lo-spinner"></div>
            <div class="lo-note">First visit may take up to 30 seconds</div>
        </div>
    </div>

"""

OBSERVER_JS = """\
    window.addEventListener('DOMContentLoaded', function () {
        var overlay = document.getElementById('loading-overlay');
        var infobox = document.getElementById('infobox');

        for (var i = 0; i < 180; i++) {
            var s = document.createElement('div');
            s.className = 'lo-star';
            s.style.left = (Math.random() * 100) + '%';
            s.style.top  = (Math.random() * 100) + '%';
            s.style.width  = Math.random() < 0.15 ? '3px' : '2px';
            s.style.height = s.style.width;
            s.style.animation = 'lo-twinkle ' + (2 + Math.random() * 4).toFixed(2) + 's '
                              + (Math.random() * 5).toFixed(2) + 's ease-in-out infinite';
            overlay.appendChild(s);
        }

        if (overlay && infobox) {
            new MutationObserver(function (mutations) {
                mutations.forEach(function (m) {
                    if (m.attributeName === 'style' && infobox.style.display === 'none') {
                        overlay.style.display = 'none';
                    }
                });
            }).observe(infobox, { attributes: true });
        }
    });

"""


def patch(html: str) -> str:
    patches = [
        # Title
        ("<title>hp_checkers</title>",
         "<title>Harry Potter House Cup Checkers</title>"),

        # Body background
        ("background-color:powderblue;",
         "background-color: #050510;"),

        # show_infobox — strip centering logic
        (
            'function show_infobox() {\n'
            '    infobox.style.display = "block";\n\n'
            '    // Measure box\n'
            '    const w = infobox.offsetWidth;\n'
            '    const h = infobox.offsetHeight;\n\n'
            '    // Center in viewport\n'
            '    const left = (window.innerWidth - w) / 2;\n'
            '    const top = (window.innerHeight - h) / 2;\n\n'
            '    infobox.style.left = left + "px";\n'
            '    infobox.style.top = top + "px";\n'
            '}',
            'function show_infobox() {\n'
            '    infobox.style.display = "block";\n'
            '}'
        ),

        # CSS — replace status/progress/infobox block
        (
            '        #status {\n'
            '            display: inline-block;\n'
            '            vertical-align: top;\n'
            '            margin-top: 20px;\n'
            '            margin-left: 30px;\n'
            '            font-weight: bold;\n'
            '            color: rgb(120, 120, 120);\n'
            '        }\n\n'
            '        #progress {\n'
            '            height: 20px;\n'
            '            width: 300px;\n'
            '        }\n\n'
            '        #infobox {\n'
            '            position: fixed; /* center relative to viewport */\n'
            '            background: green;\n'
            '            color: blue;\n'
            '            font-weight: bold;\n'
            '            padding: 12px 24px;\n'
            ' /*           display: none; */\n'
            '            z-index: 999999;\n'
            '        }',
            CUSTOM_CSS
        ),

        # Google Fonts + loading overlay HTML
        (
            '    <canvas class="emscripten" id="canvas"',
            LOADING_HTML + '    <canvas class="emscripten" id="canvas"'
        ),

        # Google Fonts link after favicon
        (
            '    <link rel="icon" type="image/png" href="favicon.png" sizes="16x16">',
            '    <link rel="icon" type="image/png" href="favicon.png" sizes="16x16">\n'
            + GOOGLE_FONTS
        ),

        # MutationObserver JS before closing frame_online block
        (
            '    function frame_online(url) {\n'
            '        window.frames["iframe"].location = url;\n'
            '    }\n\n'
            '    </script>',
            '    function frame_online(url) {\n'
            '        window.frames["iframe"].location = url;\n'
            '    }\n\n'
            + OBSERVER_JS
            + '    </script>'
        ),
    ]

    for old, new in patches:
        if old not in html:
            print(f"  WARNING: patch target not found — '{old[:60].strip()}...'")
        else:
            html = html.replace(old, new, 1)

    return html


def main():
    for ext in ("*.apk", "*.tar.gz"):
        for f in (ROOT / "docs").glob(ext):
            f.unlink()

    print("Building pygbag web bundle...")
    result = subprocess.run(
        [sys.executable, "-m", "pygbag", "--build", "main.py"],
        cwd=ROOT
    )
    if result.returncode != 0:
        print("pygbag build failed.")
        sys.exit(1)

    print("Copying build/web → docs/...")
    shutil.copytree(ROOT / "build" / "web", ROOT / "docs", dirs_exist_ok=True)

    print("Patching docs/index.html...")
    index = ROOT / "docs" / "index.html"
    html = index.read_text(encoding="utf-8")
    html = patch(html)
    index.write_text(html, encoding="utf-8")

    print("Done. To publish:")
    print("  git add docs/ && git commit -m 'Rebuild web' && git push")


if __name__ == "__main__":
    main()
