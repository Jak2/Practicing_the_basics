# Inkboard — Design Spec
**Date:** 2026-06-29
**Status:** Approved

---

## 1. What Is This?

Inkboard is a pen-first, open-source infinite canvas tool — a true Excalidraw alternative that solves the pain points Excalidraw and every other whiteboard tool ignores: native pen tablet support, layers, multi-page canvases, and offline-first collaboration.

**The launch hook:** *"The first open-source infinite canvas that actually works with your pen tablet."*

---

## 2. Problem Statement

### Excalidraw's Pricing Model (context)

| Tier | Price | What you get |
|---|---|---|
| Free | $0 | Local drawing, ephemeral collab rooms, basic export |
| Excalidraw+ | $7/user/month | Persistent cloud storage, persistent collab rooms, E2E encrypted sharing, Google Drive / OneDrive integration, version history |

**The lock-in:** Free tier rooms expire. There's no offline-first sync. Cloud persistence requires paying. Self-hosting the open-source version gives you the canvas but not the collaboration infra.

### Real User Pain Points (sourced from GitHub issues, Reddit, HN)

| Pain Point | Category | Severity |
|---|---|---|
| No pen tablet pressure/tilt support | Input | Critical |
| No layers system | Canvas | High |
| No multi-page / canvas | Canvas | High |
| Collaboration rooms are ephemeral (expire) | Collab | High |
| No offline-first sync | Storage | High |
| No grid snapping / smart guides | UX | Medium |
| No component/symbol libraries | Productivity | Medium |
| No element locking | Canvas | Medium |
| No proper PDF export | Export | Medium |
| No pen tool (Bezier curves) | Drawing | Medium |
| No dark canvas background | UX | Low |

---

## 3. Differentiation Strategy

### Blue Ocean: Pen Tablet Support

Every major whiteboard tool — Excalidraw, tldraw, Penpot, Miro, FigJam — ignores pen tablets. No pressure sensitivity, no tilt mapping, no barrel rotation. Huion H1060P, Wacom Intuos, XP-Pen Artist series users get the same dumb mouse cursor as everyone else.

Inkboard leads with this. It's an uncontested space.

### Open-Source Projects to Mine Features From

| Project | License | What to take |
|---|---|---|
| **tldraw** | MIT | Infinite canvas engine, shape bindings, multi-page — use as the base |
| **perfect-freehand** | MIT | Pressure → stroke width simulation library |
| **Penpot** | MPL-2.0 | Layers panel UI, component system, design tokens |
| **Rnote** | GPL-3 | Native pen tablet pressure/tilt/barrel via libinput (reference impl) |
| **Xournal++** | GPL-2 | PDF annotation + pen input, pressure curves (reference impl) |
| **Lorien** | MIT | Infinite canvas with pressure-sensitive brushes, minimal UI approach |
| **Mermaid.js** | MIT | Code-to-diagram (diagrams-as-code, v1.2 feature) |
| **draw.io / diagrams.net** | Apache-2 | Connector routing, shape libraries, export formats |
| **Yjs** | MIT | CRDT engine for offline-first real-time collaboration |

---

## 4. Target Users

All of the following — Inkboard is a full Excalidraw replacement, not a niche tool:

- **Developers / engineers** — system diagrams, architecture sketches, wireframes
- **Digital artists / note-takers** — pen tablet users who want a free whiteboard that respects their hardware
- **Teams** — collaborative visual thinking, product managers, designers, educators

---

## 5. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Canvas engine | **tldraw** (MIT) | Infinite canvas, multi-page, shape system — don't rebuild |
| Pen strokes | **perfect-freehand** | Pressure → stroke simulation, battle-tested |
| Pen input (browser) | **WebHID API** | Native tablet events in-browser, no drivers needed |
| Pen input (desktop) | **Electron + node-hid** | Full driver access: pressure, tilt, barrel rotation |
| Real-time collab | **Yjs + y-webrtc** | CRDT, offline-first, self-hostable signaling server |
| Framework | **React + TypeScript** | Strong ecosystem, tldraw is React-native |
| Desktop wrapper | **Electron** | Unlocks native pen APIs, local file system |
| Styling | **Tailwind CSS** | Fast UI iteration |
| Export | **html-to-image + jsPDF** | PNG, SVG, PDF pipeline |
| Build | **Vite** | Fast dev, good Electron support |
| Monorepo | **pnpm workspaces** | Web + desktop apps sharing packages |

---

## 6. Architecture

```
inkboard/
├── apps/
│   ├── web/                  # React + Vite (browser app)
│   └── desktop/              # Electron wrapper
├── packages/
│   ├── canvas/               # Core canvas engine (wraps tldraw)
│   ├── pen-input/            # WebHID + Electron pressure/tilt handling
│   ├── sync/                 # Yjs CRDT collaboration (v1.1)
│   └── export/               # SVG, PNG, PDF export
├── server/
│   └── signaling/            # y-webrtc signaling server (v1.1, self-hostable)
└── docs/
    └── specs/
```

### Key Design Decisions

**Why build on tldraw instead of from scratch?**
Building an infinite canvas engine (viewport transforms, hit testing, selection handles, snap guides) is 3-6 months of work alone. tldraw is MIT-licensed, actively maintained, and already has multi-page. We wrap it and extend it.

**Why Electron for pen support?**
The WebHID API covers ~80% of tablet use cases in modern Chrome/Edge. For full pressure curves, tilt axis, and barrel rotation (the things Huion H1060P exposes), you need native driver access. Electron's `node-hid` gives that. The web app works for basic use; the desktop app is the power-user path.

**Why Yjs over other CRDT libraries?**
Yjs has the best tldraw integration (`tldraw-yjs-example` exists in the tldraw repo), making collab implementation significantly faster. It's also used by Penpot and many other OSS tools.

---

## 7. Phased Roadmap

### Phase 1 — v0.1: Core Canvas (2-3 weeks)
- Set up monorepo (pnpm + Vite + Electron)
- Integrate tldraw as canvas engine
- Basic shapes: rectangle, ellipse, arrow, text, freehand
- Local file save/load (JSON)
- Keyboard shortcuts

### Phase 2 — v0.2: Pen Tablet Support (2-3 weeks)
- WebHID integration for browser
- Electron + node-hid for desktop
- Pressure → stroke width mapping
- Tilt → brush angle mapping (desktop only)
- Barrel rotation → eraser/tool switch (desktop only)
- Pressure curve calibration UI
- Tested on: Huion H1060P, Wacom Intuos, XP-Pen

### Phase 3 — v0.3: Layers + Multi-page (2 weeks)
- Layers panel (Penpot-inspired)
- Layer lock, hide, rename, reorder
- Multi-page support (tldraw already has this, wire UI)
- Page thumbnail strip

### Phase 4 — v1.0: Export + Sharing (1-2 weeks)
- Export: SVG, PNG, PDF
- Shareable read-only links (no account needed)
- Import Excalidraw files (.excalidraw format)
- Basic onboarding / empty state

### Phase 5 — v1.1: Offline-first Collaboration (3-4 weeks)
- Yjs CRDT integration
- Persistent rooms (don't expire)
- Works offline, syncs on reconnect
- Self-hostable signaling server
- Real-time cursors + presence

### Phase 6 — v1.2: Diagrams-as-code (1-2 weeks)
- Mermaid.js embedded in text shapes
- PlantUML support
- Live preview as you type

### Phase 7 — v2.0: Cloud Tier (Open Core)
- Hosted sync server (paid)
- Team workspaces
- Version history
- SSO / org management
- This is the monetization layer — self-host is always free

---

## 8. Monetization Model (Open Core)

| Tier | Price | What you get |
|---|---|---|
| **Community** | Free forever | Full canvas, pen support, local save, self-host collab |
| **Inkboard Cloud** | ~$6/user/month | Hosted sync, persistent rooms, version history, team workspaces |
| **Self-host Pro** | One-time or annual | Priority support, SSO, audit logs for enterprises |

**Principle:** The canvas and pen support are never paywalled. The cloud infra is the paid layer.

---

## 9. Success Criteria for v1.0

- [ ] A Huion H1060P user can draw with pressure sensitivity in the browser
- [ ] A Huion H1060P user can draw with full pressure + tilt in the desktop app
- [ ] Files save and load locally without an account
- [ ] Excalidraw `.excalidraw` files can be imported
- [ ] Export to PNG, SVG, PDF works
- [ ] Layers panel works with lock/hide/reorder
- [ ] Multi-page navigation works
- [ ] App works offline

---

## 10. Brainstorming Session Notes

This section captures the full context from the ideation session.

**Origin:** User wanted to build something like Excalidraw but differentiated. Excalidraw charges $7/user/month for cloud features that should be free. The core open-source version has critical missing features.

**Key constraint:** "Fast build project" — scope must be tight for each phase.

**Target audience decision:** All audiences (developers, artists with tablets, teams) — full replacement, not a niche tool.

**Tech stack:** TypeScript + React comfort zone, willing to learn Electron.

**Monetization:** Open core (free self-host + paid cloud), but ship first and monetize later.

**Lead differentiator chosen:** Pen tablet support as the v1 launch hook — it's a blue ocean, no competitor has it, and it's personally motivated (Huion H1060P ownership).

**Why not everything at once:** Each differentiator (pen, CRDT collab, layers, diagrams-as-code) is 2-4 weeks of focused work. Phasing ensures something ships rather than nothing.
