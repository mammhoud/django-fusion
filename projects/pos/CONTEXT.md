# Forge POS

A desktop point-of-sale application built on Tauri 2 + Rust with a React/Vite
frontend and SQLite storage, sold in four editions that share one codebase.

## Deployments

**Terminal**:
A single point-of-sale instance running the desktop app on one device.
_Avoid_: POS, register, device

**Multi-terminal network**:
A set of terminals that share one cloud master and stay in sync.
_Avoid_: multi-store, fleet

**Self-hosted**:
An edition you run yourself on your own hardware (Community, Standard, Pro).
_Avoid_: on-premise, local

**Hosted**:
The Cloud edition, where the cloud master is operated for you.
_Avoid_: managed, SaaS

## Editions

**Edition**:
A priced configuration of the product with its own feature set: Community (free, offline-first), Standard (standalone + sidecar), Pro (multi-terminal + cloud master), Cloud (hosted multi-terminal).
_Avoid_: Minimal, Solo, Full (legacy names)

## Architecture

**Sidecar**:
The embedded Python (Robyn) API server that extends a terminal with a REST API, inventory, analytics, and sync in Standard and above.
_Avoid_: backend, API server

**Cloud master**:
The central sync hub that Pro and Cloud editions run; terminals push their data to it.
_Avoid_: cloud server, central server

**Cloud sync client**:
The Standard-edition component that pushes products, sales, and nodes to a cloud master.
_Avoid_: sync, client
