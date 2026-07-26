# 📊 Scripts Usage Analysis

**Path:** `projects/assets/scripts/`
**Status:** ✅ Active — used by asset build system

---

## Overview

Workspace asset CLI scripts used for building frontend bundles, running collectstatic, loading fixtures, and populating data.

---

## File Usage

| File | Used By | Notes |
|------|---------|-------|
| `workspace.mjs` | **Build system** | Main Node.js CLI for asset management. Invoked via `package.json` scripts. Supports building, watching, cleaning, collectstatic, fixture loading, and site management for all sites (lms, vresume, cypercloud, crm, lms-fusion, cms-fusion). |

---

## Usage by Project

| Project | Uses Scripts? | How |
|---------|--------------|-----|
| **lms** | ✅ Yes | `npm --prefix assets run build:structa` |
| **cms-fusion** | ✅ Yes | `npm --prefix assets run build --site cms-fusion` |
| **lms-fusion** | ✅ Yes | `npm --prefix assets run build --site lms-fusion` |
| **portfolio** | ✅ Yes | `npm --prefix assets run build:vresume` |
| **cypercloud** | ✅ Yes | `npm --prefix assets run build:cypercloud` |
| **ctc-research** | ✅ Yes | `npm --prefix assets run build:ctc` |
