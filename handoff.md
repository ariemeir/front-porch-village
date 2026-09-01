# Handoff — Elev8 Villages "Front Porch Village" concept study

Status as of 2026-09-01: **built, verified in a headless browser, and deployed to a
public (but noindexed) URL.**

## What this is

An interactive, real-time 3D concept study of three tiny homes with deep front
porches around a shared green, made for the Taproot opportunity *"3D Concept
Rendering: Tiny Homes & Front Porch Community"* posted by Elev8 Villages, Inc.
(Nashville, TN; founder Melissa Kaye). It is a **portfolio/pitch piece to win the
volunteer engagement**, not the final deliverable the brief asks for.

Elev8 Villages builds for young adults aging out of foster care. That framing is
in the page itself — the opening card and the first section of the design-notes
drawer — and it is the reason the porch dimensions are what they are.

It is **not an image**. It is ~1,640 lines of JavaScript that generates geometry
at page load and renders it in the browser with WebGL (Three.js r128, UMD, from
cdnjs). Any PNG of it is a screenshot.

Full rationale, scene inventory, and draft pitch text for the Taproot application
are in `README.md` in this directory. This file covers state and mechanics.

## Where it lives (read this first — it's in an odd place)

| | |
|---|---|
| Repo | `ariemeir/carefamily` (**yes, the Care Family ops repo**) |
| Branch | `claude/tiny-homes-3d-rendering-mgnxbk` |
| Path | `elev8_villages_concept/` |
| Commits | `cd41f6c` (build), `c6868bb` (resident context + standalone), `7ccc187` (Pages config) |

This is volunteer work sitting inside an unrelated production repo. That was an
accident of how the cloud session was started (carefamily was the session's source
repo, selected from the phone), not a decision. The directory is fully
self-contained — five files, nothing imports from carefamily — so it lifts out
cleanly into `~/dev/volunteer/projects/elev8-front-porch-village`, matching the
richland-cemetery-prototype layout:

```zsh
cp -R <carefamily-checkout>/elev8_villages_concept ~/dev/volunteer/projects/elev8-front-porch-village
cd ~/dev/volunteer/projects/elev8-front-porch-village
git init && git add -A && git commit -m "Front Porch Village concept study"
```

Do this before it accumulates any dependency on its current neighbors.

## Links

- Private artifact (page content only, no Claude branding in the markup, but the
  URL and viewer chrome are claude.ai):
  https://claude.ai/code/artifact/5e029e99-9e79-4c4b-a47d-7f13c84600bf
- **Public URL (live): https://front-porch-3d-demo.pages.dev** — deployed
  2026-09-01 from a laptop authenticated via `wrangler whoami`
  (arie.coach@gmail.com). Not indexed by default (see below), but reachable by
  anyone with the link.

## Deploying

Direct-upload Cloudflare Pages, manual deploy, no CI. `wrangler.toml` here
declares `pages_build_output_dir = "site"` and the project name
`front-porch-3d-demo` (renamed from the originally planned
`elev8-front-porch-village` — Pages project names can't contain underscores, and
`front-porch-3d-demo` was the closer match to what was asked for); `site/` is
committed, so there is no build step. Re-deploying after a rebuild is just:

```zsh
npx wrangler pages deploy site --project-name front-porch-3d-demo
```

Run from a machine authenticated via `wrangler whoami`. Produces
`https://front-porch-3d-demo.pages.dev` as the stable production alias, plus a
unique preview URL per deploy (the first deploy's preview URL was
`https://1991051f.front-porch-3d-demo.pages.dev`).

The page is marked **noindex** in three places (meta robots, a googlebot-specific
tag, `site/robots.txt`) and `site/_headers` sends `X-Robots-Tag`, which Pages
honors and which was confirmed present on the live response
(`x-robots-tag: noindex, nofollow, noarchive`) after deploy. It carries no
analytics and no trackers.

Not built, but worth considering: richland's `functions/_middleware.js` access-code
gate. If this link goes to donors, the same casual gate would fit, and noindex
alone is weaker protection than a code.

## File map

```
front-porch-village.html   the whole study (1,639 lines) — authored as a BODY
                           FRAGMENT: carries its own <title>, <link> and <style>
                           but no <!doctype>/<html>/<head>. Publishing it as an
                           artifact wraps it; build_standalone.py wraps it too.
build_standalone.py        lifts the head elements into a real <head>, adds the
                           robots directives, writes site/
site/index.html            generated — do not hand-edit, re-run the build
site/robots.txt            Disallow: /
site/_headers              X-Robots-Tag for Netlify/Cloudflare Pages
wrangler.toml              Pages project config (name, output dir)
README.md                  rationale, scene inventory, Taproot pitch text
```

## Architecture, for someone about to change something

Every design decision is a named variable near the top of the script block:

- `HOMES[]` — one object per home, 14 fields: `angle`/`radius` (site placement on a
  circle around the green), `width`/`depth`/`pitch`, `siding`/`roof`/`door`/`deck`/
  `furniture` hex colors, `batten` (board-and-batten vs lap siding), `doorX`/`winX`/
  `stepX` placements, and `porch` — an enum of exactly three: `"rockers"`, `"swing"`,
  `"bench"`.
- `FL`, `WALL_H`, `PORCH_D`, `PORCH_CEIL` — finished floor above grade, plate
  height, porch depth, porch ceiling. The imperial dimensions quoted in the design
  notes drawer are these numbers converted; **change one and update the drawer**.
- `KEYS[]` — time-of-day keyframes: sun elevation/azimuth/color/intensity, sky
  gradient top and bottom, hemisphere light, fog, tone-mapping exposure, and a
  `night` scalar 0→1 that drives every emissive (windows, porch lanterns, string
  lights, fire).
- `VIEWS[]` — camera presets as explicit `pos`/`look` world coordinates, converted
  to spherical on click. Two of them also set the hour.
- `TREES[]` — canopy placement, deliberately kept off the main sight lines.

Materials are procedural canvas textures (`lapCanvas`, `battenCanvas`,
`shingleCanvas`, `deckCanvas`, grass, gravel, stone), so a material change is one
hex value, never a new asset.

Geometry is generated by `makeHome(opt)` plus small factories (`makeWindow`,
`makeLamp`, `makeChair`, `makeSwing`, `makeBench`, `makeTree`, `makeFigure`,
`gardenBed`, `stringLights`). Rendering is ACES filmic tone mapping, PCF soft
shadow maps, and a gradient sky-dome shader.

## Verification done

Driven headlessly with Playwright + Chromium at 1440×880 and at 390×780 portrait:
no page errors; all six camera presets, the time slider, the notes drawer, and
clean-frame mode exercised; screenshots reviewed frame by frame. The standalone
`site/index.html` build was verified the same way.

Note for whoever re-runs this: the cloud session's egress policy blocked
`cdnjs.cloudflare.com` and Google Fonts, so the harness substituted a local
`three.min.js` (npm `three@0.128.0`, identical to r128) and the screenshots show
fallback typefaces. On a normal machine both load fine and the real faces appear.

## Known issues / fixes already applied

- **Camera presets are hand-placed world coordinates and are fragile.** Two were
  wrong on the first pass: "From the porch" put the camera *inside the seated scale
  figure's head* (a grey sphere filling the frame), and the next attempt put a porch
  post dead centre. Current values are verified by screenshot. If you move a home,
  re-check every preset visually — nothing catches this automatically.
- **Trees were originally oversized and blocked the homes.** Canopy radius reduced,
  subdivision raised, and `TREES[]` repositioned off the sight lines. Don't put a
  tree back inside the horseshoe without looking at the Arrival view.
- **String lights clipped through the porch roofs.** Attachment point moved out to
  the fascia edge (`g.userData.postTop`).
- **Night was too bright** — the lights didn't read. Hemisphere intensity, exposure,
  moon fill, and every emissive were reduced. Those values are tuned together; don't
  raise one alone.
- **Portrait framing** cropped the village. The lens now widens on narrow aspect
  ratios (`H_HALF_TAN`, constant horizontal FOV) with a slight downward tilt.

## Not yet done

- **Not reproducible.** 25 unseeded `Math.random()` calls scatter foliage, texture
  grain and shrubs. Two loads differ visibly. Fine for a live demo, **must be fixed
  with a seeded PRNG before this is ever used as a render pipeline.**
- **The site plan is only half data-driven.** Homes place from `angle`/`radius`, but
  the green radius, the loop path and `stringLights` assume exactly three homes — a
  fourth places correctly and then breaks the light strings.
- No interiors. Exteriors only.
- The drawer's imperial dimensions are hand-written prose, not derived from the
  constants. They agree today.

## Context worth not re-litigating

Melissa asked for renderings; this answers with something interactive on purpose.
The argument, which is also the pitch: the porch-to-porch relationship is spatial
and the emotional read is mostly light, so a single still has to pick one moment
and argue for it. "From the porch" (seated eye height on Home 01, looking across
the green at Home 03) and the 6:00am–9:36pm slider are the two things a still can't
do. `H` hides all panels so stills can still be pulled for a donor deck.

The final deliverable, if the engagement is won, is high-resolution rendering
matched to their Amphitheatre piece. **This is concept stage and should not be
mistaken for the finished product** — real-time WebGL with shadow maps, no global
illumination, no ambient occlusion, no reflections, no depth of field.

## Open questions for Arie

1. **Is this a pitch piece or the seed of a pipeline?** A stated goal is a
   configurable pipeline that renders a tiny house from drawings/spec. What exists
   is a parametric generator with a hardcoded inline config, a renderer, and a
   headless capture harness — the back half. Absent: any drawing/spec ingestion,
   generality beyond the one gable-front-plus-porch archetype, and photoreal
   output (that's a different renderer — headless Blender/Cycles — driven by the
   same config). The three forks that change the architecture: what the input is,
   what quality bar the output must hit, how wide the geometry vocabulary must be.
2. Move the directory out of carefamily into its own repo (above)?
3. Add richland's access-code gate before sending the link to donors?
4. The README's pitch text is a draft — Arie's voice, Arie's call.
