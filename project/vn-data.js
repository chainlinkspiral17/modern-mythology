// vn-data.js — OPFS-backed data layer for Modern Mythology
// Exposes window.VNData for use by both the game engine and scene editor.
//
// Storage layout (Origin Private File System):
//   scenes/vol{N}/{sceneId}.json   — scene content files
//   saves/slot_{N}.json            — save slots
//   profile.json                   — persistent flags and gallery unlocks
//
// Falls back to localStorage if OPFS is unavailable.

window.VNData = (() => {
  const USE_OPFS = typeof navigator !== 'undefined' && 'storage' in navigator && 'getDirectory' in navigator.storage;

  // ── OPFS helpers ─────────────────────────────────────────────────────────
  let _opfsRoot = null;
  async function _root() {
    if (!_opfsRoot) _opfsRoot = await navigator.storage.getDirectory();
    return _opfsRoot;
  }

  async function _dir(...parts) {
    let d = await _root();
    for (const part of parts) d = await d.getDirectoryHandle(part, { create: true });
    return d;
  }

  async function _writeFile(dirHandle, filename, data) {
    const fh = await dirHandle.getFileHandle(filename, { create: true });
    const w = await fh.createWritable();
    await w.write(typeof data === 'string' ? data : JSON.stringify(data, null, 2));
    await w.close();
  }

  async function _readFile(dirHandle, filename) {
    try {
      const fh = await dirHandle.getFileHandle(filename);
      const file = await fh.getFile();
      return JSON.parse(await file.text());
    } catch { return null; }
  }

  async function _listFiles(dirHandle) {
    const results = [];
    try {
      for await (const [name, handle] of dirHandle.entries()) {
        if (handle.kind === 'file' && name.endsWith('.json')) {
          results.push({ name, handle });
        }
      }
    } catch {}
    return results;
  }

  // ── localStorage fallback helpers ─────────────────────────────────────────
  const LS_PREFIX = 'mm_vnd_';
  function _lsWrite(key, data) {
    try { localStorage.setItem(LS_PREFIX + key, JSON.stringify(data)); } catch {}
  }
  function _lsRead(key) {
    try { return JSON.parse(localStorage.getItem(LS_PREFIX + key) || 'null'); } catch { return null; }
  }
  function _lsKeys(prefix) {
    const keys = [];
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && k.startsWith(LS_PREFIX + prefix)) keys.push(k.slice(LS_PREFIX.length));
      }
    } catch {}
    return keys;
  }

  // ── Scenes ────────────────────────────────────────────────────────────────
  async function writeScene(scene) {
    if (!scene || !scene.id || !scene.vol) return;
    if (USE_OPFS) {
      try {
        const d = await _dir('scenes', `vol${scene.vol}`);
        await _writeFile(d, `${scene.id}.json`, scene);
        return;
      } catch (e) { console.warn('VNData OPFS write failed, using localStorage', e); }
    }
    _lsWrite(`scene_${scene.id}`, scene);
  }

  async function readScene(sceneId) {
    if (USE_OPFS) {
      try {
        for (let vol = 1; vol <= 10; vol++) {
          const d = await _dir('scenes', `vol${vol}`);
          const data = await _readFile(d, `${sceneId}.json`);
          if (data) return data;
        }
      } catch {}
    }
    return _lsRead(`scene_${sceneId}`);
  }

  async function readAllScenes() {
    const all = {};
    if (USE_OPFS) {
      try {
        const scenesDir = await _dir('scenes');
        for await (const [volName, volHandle] of scenesDir.entries()) {
          if (volHandle.kind !== 'directory') continue;
          const files = await _listFiles(volHandle);
          for (const { handle } of files) {
            const file = await handle.getFile();
            try {
              const scene = JSON.parse(await file.text());
              if (scene && scene.id) all[scene.id] = scene;
            } catch {}
          }
        }
        return all;
      } catch {}
    }
    // localStorage fallback
    for (const key of _lsKeys('scene_')) {
      const scene = _lsRead(key);
      if (scene && scene.id) all[scene.id] = scene;
    }
    return all;
  }

  async function deleteScene(sceneId, vol) {
    if (USE_OPFS) {
      try {
        const d = await _dir('scenes', `vol${vol}`);
        await d.removeEntry(`${sceneId}.json`);
        return;
      } catch {}
    }
    try { localStorage.removeItem(LS_PREFIX + `scene_${sceneId}`); } catch {}
  }

  // Seed OPFS from DEMO_SCENES on first run (only if no scenes exist yet).
  async function seedDemoScenes(demoScenes) {
    const existing = await readAllScenes();
    if (Object.keys(existing).length > 0) return; // already seeded
    for (const [key, scene] of Object.entries(demoScenes)) {
      if (!scene || !scene.id || !Array.isArray(scene.nodes)) continue;
      // DEMO_SCENES scenes often lack a vol property — infer it from the id
      // e.g. 'vol1_briar_falls' → 1, or from a numeric key like DEMO_SCENES[1]
      const vol = scene.vol || (() => {
        const fromId = String(scene.id).match(/^vol(\d+)/);
        if (fromId) return parseInt(fromId[1]);
        if (/^\d+$/.test(String(key))) return parseInt(key);
        return null;
      })();
      if (!vol) continue;
      await writeScene({ ...scene, vol });
    }
  }

  // ── Saves ─────────────────────────────────────────────────────────────────
  const MAX_SLOTS = 8;

  async function writeSave(slot, data) {
    const record = { ...data, slot, savedAt: Date.now() };
    if (USE_OPFS) {
      try {
        const d = await _dir('saves');
        await _writeFile(d, `slot_${slot}.json`, record);
        return;
      } catch {}
    }
    _lsWrite(`save_${slot}`, record);
  }

  async function readSave(slot) {
    if (USE_OPFS) {
      try {
        const d = await _dir('saves');
        return await _readFile(d, `slot_${slot}.json`);
      } catch {}
    }
    return _lsRead(`save_${slot}`);
  }

  async function listSaves() {
    const slots = [];
    for (let i = 0; i < MAX_SLOTS; i++) {
      const s = await readSave(i);
      slots.push(s ? { ...s, slot: i, used: true } : { slot: i, used: false });
    }
    return slots;
  }

  async function deleteSave(slot) {
    if (USE_OPFS) {
      try {
        const d = await _dir('saves');
        await d.removeEntry(`slot_${slot}.json`);
        return;
      } catch {}
    }
    try { localStorage.removeItem(LS_PREFIX + `save_${slot}`); } catch {}
  }

  // ── Profile (persistent flags, gallery unlocks) ───────────────────────────
  async function readProfile() {
    if (USE_OPFS) {
      try {
        const r = await _root();
        const data = await _readFile(r, 'profile.json');
        if (data) return data;
      } catch {}
    }
    return _lsRead('profile') || {};
  }

  async function writeProfile(data) {
    if (USE_OPFS) {
      try {
        const r = await _root();
        await _writeFile(r, 'profile.json', data);
        return;
      } catch {}
    }
    _lsWrite('profile', data);
  }

  async function setFlag(key, val) {
    const profile = await readProfile();
    profile[key] = val;
    await writeProfile(profile);
  }

  async function getFlag(key, defaultVal = false) {
    const profile = await readProfile();
    return profile[key] !== undefined ? profile[key] : defaultVal;
  }

  // ── Export to real filesystem directory ───────────────────────────────────
  async function exportToDirectory() {
    if (!window.showDirectoryPicker) {
      alert('Directory export requires Chrome or Edge. Use the JSON export instead.');
      return false;
    }
    let dir;
    try { dir = await window.showDirectoryPicker({ mode: 'readwrite' }); }
    catch (e) { if (e.name !== 'AbortError') console.error(e); return false; }

    const allScenes = await readAllScenes();
    const scenesDir = await dir.getDirectoryHandle('scenes', { create: true });
    for (const scene of Object.values(allScenes)) {
      const volDir = await scenesDir.getDirectoryHandle(`vol${scene.vol}`, { create: true });
      await _writeFile(volDir, `${scene.id}.json`, scene);
    }
    return true;
  }

  // ── Import from real filesystem directory ─────────────────────────────────
  async function importFromDirectory() {
    if (!window.showDirectoryPicker) {
      alert('Directory import requires Chrome or Edge. Use the JSON import instead.');
      return false;
    }
    let dir;
    try { dir = await window.showDirectoryPicker({ mode: 'read' }); }
    catch (e) { if (e.name !== 'AbortError') console.error(e); return false; }

    let count = 0;
    try {
      const scenesDir = await dir.getDirectoryHandle('scenes');
      for await (const [, volHandle] of scenesDir.entries()) {
        if (volHandle.kind !== 'directory') continue;
        for await (const [, fileHandle] of volHandle.entries()) {
          if (fileHandle.kind !== 'file') continue;
          const file = await fileHandle.getFile();
          if (!file.name.endsWith('.json')) continue;
          try {
            const scene = JSON.parse(await file.text());
            if (scene && scene.id) { await writeScene(scene); count++; }
          } catch {}
        }
      }
    } catch (e) { console.warn('Import error', e); }
    return count;
  }

  // ── Status ────────────────────────────────────────────────────────────────
  function isOPFSAvailable() { return USE_OPFS; }

  async function getStorageEstimate() {
    if (navigator.storage && navigator.storage.estimate) {
      const { usage, quota } = await navigator.storage.estimate();
      return { usageMB: (usage / 1024 / 1024).toFixed(1), quotaMB: (quota / 1024 / 1024).toFixed(0) };
    }
    return null;
  }

  return {
    writeScene, readScene, readAllScenes, deleteScene, seedDemoScenes,
    writeSave, readSave, listSaves, deleteSave,
    readProfile, writeProfile, setFlag, getFlag,
    exportToDirectory, importFromDirectory,
    isOPFSAvailable, getStorageEstimate,
  };
})();
