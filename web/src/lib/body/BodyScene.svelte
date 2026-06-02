<script lang="ts">
  import * as THREE from 'three';
  import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
  import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
  import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
  import * as m from '$lib/paraglide/messages';
  import { onMount } from 'svelte';
  import { classifyHit, classifyFace, regionOrgans, type TargetId, type RegionId, type OrganId, type FaceId } from './regions';

  let { onpick, onhover }: { onpick: (id: TargetId) => void; onhover: (id: TargetId | null) => void } = $props();

  let host: HTMLDivElement;
  let layer = $state<'outer' | 'inside' | 'face'>('outer');
  let goBack = $state<() => void>(() => {});

  const REGION_F: Record<string, number> = { head: 0, chest: 1, 'upper-abdomen': 2, 'lower-abdomen': 3, arm: 4, leg: 5, back: 6 };
  const FACE_F: Record<string, number> = { eyes: 0, nose: 1, mouth: 2, jaw: 3, ear: 4, nerves: 5 };

  onMount(() => {
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xe9e7e3);
    const camera = new THREE.PerspectiveCamera(40, 1, 0.01, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    host.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; controls.enablePan = false; controls.autoRotate = false;

    scene.add(new THREE.HemisphereLight(0xffffff, 0x666666, 1.1));
    const key = new THREE.DirectionalLight(0xffffff, 1.5); key.position.set(2, 4, 3); scene.add(key);
    const rim = new THREE.DirectionalLight(0x88bbff, 0.4); rim.position.set(-3, 2, -2); scene.add(rim);

    const ro = new ResizeObserver(() => {
      const w = host.clientWidth, h = host.clientHeight; if (!w || !h) return;
      renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix();
    });
    ro.observe(host);

    const vfov = (camera.fov * Math.PI) / 180;
    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    const clock = new THREE.Clock();

    // self-hosted Draco decoder for the compressed organ meshes
    const dracoLoader = new DRACOLoader();
    dracoLoader.setDecoderPath('/draco/');
    const makeLoader = () => { const l = new GLTFLoader(); l.setDRACOLoader(dracoLoader); return l; };

    let pickProxy: THREE.Mesh | null = null; // invisible box for reliable raycasts (skinned shell raycasts at the wrong scale)
    const shellMats: THREE.MeshStandardMaterial[] = [];
    const shellShaders: { uniforms: Record<string, { value: number }> }[] = [];
    let hoveredOrgan: OrganId | null = null;

    // Light up the actual body geometry of a region by injecting a position-gated
    // emissive into the shell shader (same zone logic as classifyHit). Works on a
    // single mesh - no overlay boxes.
    function applyGlow(mat: THREE.MeshStandardMaterial) {
      mat.onBeforeCompile = (shader) => {
        shader.uniforms.uRegion = { value: -1 };
        shader.uniforms.uFace = { value: -1 };
        shader.uniforms.uMode = { value: 0 };
        shader.uniforms.uMinY = { value: -size.y / 2 };
        shader.uniforms.uH = { value: size.y };
        shader.uniforms.uW = { value: size.x };
        shader.vertexShader = 'varying vec3 vWP;\n' + shader.vertexShader.replace(
          '#include <skinning_vertex>',
          '#include <skinning_vertex>\n\tvWP = (modelMatrix * vec4(transformed, 1.0)).xyz;'
        );
        shader.fragmentShader = shader.fragmentShader
          .replace('#include <common>', '#include <common>\nvarying vec3 vWP;\nuniform float uRegion;\nuniform float uFace;\nuniform float uMode;\nuniform float uMinY;\nuniform float uH;\nuniform float uW;')
          .replace('#include <emissivemap_fragment>',
            '#include <emissivemap_fragment>\n'
            + 'float ny = (vWP.y - uMinY) / uH;\n'
            + 'float nx = abs(vWP.x) / uW;\n'
            + 'if (uMode < 0.5) {\n'
            + '  float reg;\n'
            + '  if (ny >= 0.85) reg = 0.0; else if (ny < 0.50) reg = 5.0; else if (nx > 0.18) reg = 4.0;\n'
            + '  else if (vWP.z < 0.0) reg = 6.0; else if (ny >= 0.68) reg = 1.0; else if (ny >= 0.60) reg = 2.0; else reg = 3.0;\n'
            + '  if (uRegion >= 0.0 && abs(reg - uRegion) < 0.5) { totalEmissiveRadiance += vec3(0.85, 0.42, 0.22) * 0.8; }\n'
            + '} else {\n'
            + '  float fy = (ny - 0.85) / 0.15;\n'
            + '  float fz = -1.0;\n'
            + '  if (ny >= 0.85) {\n'
            + '    if (nx > 0.06) fz = 4.0; else if (vWP.z < 0.0) fz = 5.0; else if (fy > 0.72) fz = 5.0;\n'
            + '    else if (fy >= 0.5) fz = 0.0; else if (fy >= 0.32) fz = 1.0; else if (fy >= 0.15) fz = 2.0; else fz = 3.0;\n'
            + '  }\n'
            + '  if (uFace >= 0.0 && abs(fz - uFace) < 0.5) { totalEmissiveRadiance += vec3(0.85, 0.42, 0.22) * 0.9; }\n'
            + '}\n');
        shellShaders.push(shader as unknown as { uniforms: Record<string, { value: number }> });
      };
    }
    let modelBox = new THREE.Box3();
    let size = new THREE.Vector3(1, 1.8, 0.3);
    const organMap = new Map<OrganId, THREE.Object3D>();
    const organsRoot = new THREE.Group();
    organsRoot.rotation.x = -Math.PI / 2; // BodyParts3D is Z-up; scene is Y-up
    let pickables: THREE.Object3D[] = [];
    const outerPos = new THREE.Vector3(0, 0, 5);

    // camera tween between the full-body shot and a region close-up
    let twActive = false, twT = 0, twDur = 0.6;
    const twFromP = new THREE.Vector3(), twToP = new THREE.Vector3();
    const twFromT = new THREE.Vector3(), twToT = new THREE.Vector3();
    function startTween(toP: THREE.Vector3, toT: THREE.Vector3, dur = 0.6) {
      twFromP.copy(camera.position); twToP.copy(toP);
      twFromT.copy(controls.target); twToT.copy(toT);
      twT = 0; twDur = dur; twActive = true; controls.enabled = false;
    }

    function setShellOpacity(o: number) { shellMats.forEach((mm) => (mm.opacity = o)); }

    function showHighlight(region: RegionId | null) {
      const rf = region ? (REGION_F[region] ?? -1) : -1;
      shellShaders.forEach((s) => { if (s.uniforms.uMode) s.uniforms.uMode.value = 0; if (s.uniforms.uRegion) s.uniforms.uRegion.value = rf; });
    }
    function showFace(face: FaceId | null) {
      const ff = face ? (FACE_F[face] ?? -1) : -1;
      shellShaders.forEach((s) => { if (s.uniforms.uMode) s.uniforms.uMode.value = 1; if (s.uniforms.uFace) s.uniforms.uFace.value = ff; });
    }
    function highlightOrgan(id: OrganId | null) {
      if (hoveredOrgan === id) return;
      hoveredOrgan = id;
      organMap.forEach((o, key) => o.traverse((c) => {
        const mm = (c as THREE.Mesh).material as THREE.MeshStandardMaterial;
        if (!mm || !('emissive' in mm)) return;
        if (key === id) { mm.color.setHex(0xff7a45); mm.emissive.setHex(0xff5a1e); mm.emissiveIntensity = 0.9; }
        else { mm.color.setHex(0xb6453f); mm.emissive.setHex(0x3a1412); mm.emissiveIntensity = 0.15; }
      }));
    }

    function organMaterial() {
      return new THREE.MeshStandardMaterial({ color: 0xb6453f, roughness: 0.55, emissive: 0x3a1412, emissiveIntensity: 0.15 });
    }
    function buildOrgans() {
      scene.add(organsRoot);
      const real: OrganId[] = ['heart', 'lungs', 'liver', 'stomach', 'intestines', 'kidneys', 'bladder', 'pancreas', 'spleen'];
      let pending = real.length;
      const finish = () => { if (--pending === 0) alignOrgans(); };
      const loader = makeLoader();
      for (const id of real) {
        loader.load(
          `/models/organs/${id}.glb`,
          (og) => {
            const obj = og.scene;
            obj.traverse((o) => { if ((o as THREE.Mesh).isMesh) { o.name = `organ:${id}`; (o as THREE.Mesh).material = organMaterial(); } });
            obj.visible = false;
            organsRoot.add(obj); // keep native (shared) anatomical coordinates
            organMap.set(id, obj);
            finish();
          },
          undefined,
          finish
        );
      }
    }
    // Fit the shared organ cluster (true relative layout + sizes) into the body's torso.
    function alignOrgans() {
      organsRoot.updateWorldMatrix(true, true);
      const box = new THREE.Box3().setFromObject(organsRoot);
      if (box.isEmpty()) return;
      const oldC = box.getCenter(new THREE.Vector3());
      const s = (0.32 * size.y) / Math.max(box.getSize(new THREE.Vector3()).y, 1e-4); // organs span ~pelvis..upper-chest
      organsRoot.scale.setScalar(s);
      organsRoot.position.copy(new THREE.Vector3(0, (0.66 - 0.5) * size.y, 0.04 * size.z)).sub(oldC.multiplyScalar(s));
    }

    function enterRegion(region: RegionId) {
      const ids = regionOrgans[region];
      organMap.forEach((o) => (o.visible = false));
      showHighlight(null);
      const active = ids.map((id) => organMap.get(id)).filter(Boolean) as THREE.Object3D[];
      active.forEach((o) => (o.visible = true)); // shown at their real anatomical positions
      pickables = active;
      setShellOpacity(0.12);
      hoveredOrgan = null;
      layer = 'inside';
      // zoom to wherever the organs actually sit in the body
      const rbox = new THREE.Box3();
      active.forEach((o) => rbox.expandByObject(o));
      if (rbox.isEmpty()) { startTween(outerPos.clone(), new THREE.Vector3(0, 0, 0)); return; }
      const c = rbox.getCenter(new THREE.Vector3());
      const r = Math.max(...rbox.getSize(new THREE.Vector3()).toArray()) * 0.5 || 1;
      const dist = (r / Math.sin(vfov / 2)) * 1.8;
      startTween(new THREE.Vector3(c.x, c.y, c.z + dist), c.clone());
    }

    function enterHead() {
      organMap.forEach((o) => (o.visible = false));
      showHighlight(null);
      showFace(null);
      hoveredOrgan = null;
      pickables = pickProxy ? [pickProxy] : [];
      setShellOpacity(0.85);
      layer = 'face';
      const hy0 = modelBox.min.y + 0.85 * size.y;
      const cy = (hy0 + modelBox.max.y) / 2;
      const dist = ((modelBox.max.y - hy0) * 0.9) / Math.tan(vfov / 2);
      startTween(new THREE.Vector3(0, cy, dist), new THREE.Vector3(0, cy, 0));
    }

    function exitToOuter() {
      organMap.forEach((o) => (o.visible = false));
      showHighlight(null);
      showFace(null);
      hoveredOrgan = null;
      pickables = pickProxy ? [pickProxy] : [];
      setShellOpacity(0.55);
      layer = 'outer';
      onhover(null);
      startTween(outerPos.clone(), new THREE.Vector3(0, 0, 0));
    }
    goBack = exitToOuter;

    makeLoader().load('/models/mannequin.glb', (g) => {
      const model = g.scene;
      model.traverse((o) => {
        if ((o as THREE.Mesh).isMesh) {
          o.frustumCulled = false;
          const mat = new THREE.MeshStandardMaterial({ color: 0xcfd4da, roughness: 0.85, transparent: true, opacity: 0.55, depthWrite: false });
          applyGlow(mat);
          (o as THREE.Mesh).material = mat; shellMats.push(mat);
        }
      });
      // measure true rendered size (this GLB's Armature scale fools setFromObject)
      model.updateWorldMatrix(true, true);
      const worldB = new THREE.Box3().setFromObject(model);
      const geomB = new THREE.Box3(); const tb = new THREE.Box3();
      model.traverse((o) => {
        const mesh = o as THREE.Mesh;
        if (!mesh.isMesh) return;
        if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
        if (mesh.geometry.boundingBox) { tb.copy(mesh.geometry.boundingBox); geomB.union(tb); }
      });
      const useGeom = geomB.getSize(new THREE.Vector3()).y > worldB.getSize(new THREE.Vector3()).y;
      const srcBox = useGeom ? geomB : worldB;
      size = srcBox.getSize(new THREE.Vector3());
      model.position.sub(srcBox.getCenter(new THREE.Vector3()));
      model.updateWorldMatrix(true, true);
      scene.add(model);

      modelBox = new THREE.Box3(size.clone().multiplyScalar(-0.5), size.clone().multiplyScalar(0.5));
      const aspect = camera.aspect || (host.clientWidth / host.clientHeight) || 1;
      const hfov = 2 * Math.atan(Math.tan(vfov / 2) * aspect);
      const dist = Math.max((size.y / 2) / Math.tan(vfov / 2), (size.x / 2) / Math.tan(hfov / 2)) * 1.05;
      outerPos.set(0, 0, dist);
      camera.near = Math.max(dist / 100, 1e-4); camera.far = dist * 100; camera.updateProjectionMatrix();
      camera.position.copy(outerPos);
      camera.lookAt(0, 0, 0);
      controls.target.set(0, 0, 0);
      controls.minDistance = dist * 0.2; controls.maxDistance = dist * 3; controls.update();

      // invisible proxy at the rendered body's box - raycast target for outer regions
      const proxy = new THREE.Mesh(
        new THREE.BoxGeometry(size.x, size.y, size.z),
        new THREE.MeshBasicMaterial({ colorWrite: false, depthWrite: false })
      );
      scene.add(proxy);
      pickProxy = proxy;
      pickables = [proxy];

      buildOrgans();
    }, undefined, (err) => console.warn('[body] mannequin failed to load', err));

    function resolve(clientX: number, clientY: number): { id: TargetId | null; point: THREE.Vector3 | null } {
      if (!pickables.length) return { id: null, point: null };
      const r = renderer.domElement.getBoundingClientRect();
      pointer.x = ((clientX - r.left) / r.width) * 2 - 1;
      pointer.y = -((clientY - r.top) / r.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);
      const hits = raycaster.intersectObjects(pickables, true);
      if (!hits.length) return { id: null, point: null };
      if (layer === 'inside') {
        const named = hits.find((h) => h.object.name.startsWith('organ:'));
        return { id: named ? (named.object.name.slice('organ:'.length) as TargetId) : null, point: hits[0].point };
      }
      if (layer === 'face') {
        return { id: classifyFace(hits[0].point, { min: modelBox.min, max: modelBox.max }), point: hits[0].point };
      }
      return { id: classifyHit(hits[0].point, { min: modelBox.min, max: modelBox.max }), point: hits[0].point };
    }

    const el = renderer.domElement;
    el.addEventListener('click', (e) => {
      const { id } = resolve(e.clientX, e.clientY);
      if (!id) return;
      if (layer === 'outer' && id === 'head') { enterHead(); return; }
      if (layer === 'outer' && regionOrgans[id as RegionId]?.length) { enterRegion(id as RegionId); return; }
      onpick(id);
    });
    el.addEventListener('pointermove', (e) => {
      const { id } = resolve(e.clientX, e.clientY);
      el.style.cursor = id ? 'pointer' : 'default';
      if (layer === 'outer') showHighlight(id as RegionId | null);
      else if (layer === 'face') showFace(id as FaceId | null);
      else highlightOrgan(id as OrganId | null);
      onhover(id);
    });

    let raf = 0;
    (function loop() {
      raf = requestAnimationFrame(loop);
      const dt = clock.getDelta();
      if (twActive) {
        twT += dt / twDur;
        const k = Math.min(twT, 1);
        const e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
        camera.position.lerpVectors(twFromP, twToP, e);
        const tg = new THREE.Vector3().lerpVectors(twFromT, twToT, e);
        camera.lookAt(tg);
        if (k >= 1) { controls.target.copy(tg); controls.enabled = true; twActive = false; }
      } else {
        controls.update();
      }
      renderer.render(scene, camera);
    })();

    return () => { cancelAnimationFrame(raf); ro.disconnect(); controls.dispose(); renderer.dispose(); el.remove(); };
  });
</script>

<div class="scene-wrap">
  <div bind:this={host} class="scene"></div>
  {#if layer !== 'outer'}
    <button type="button" class="back" onclick={goBack}>{m.triage_back()}</button>
  {/if}
</div>

<style>
  .scene-wrap { position: relative; width: 100%; height: 100%; min-height: 520px; }
  .scene { width: 100%; height: 100%; min-height: 520px; border-radius: 16px; overflow: hidden; background: var(--bg-soft); }
  .back {
    position: absolute; top: 12px; left: 12px; z-index: 2;
    background: rgba(255, 255, 255, 0.9); border: 1px solid var(--line);
    border-radius: 100px; padding: 0.4rem 0.9rem; font-size: 0.85rem; font-weight: 600;
    color: var(--ink); cursor: pointer;
  }
  .back:hover { border-color: var(--accent); color: var(--accent); }
</style>
