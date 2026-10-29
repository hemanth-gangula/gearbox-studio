'use client';

import { useState, useEffect, useRef, Suspense, useCallback } from 'react';
import { Canvas, useThree, useFrame } from '@react-three/fiber';
import { OrbitControls, Grid, useGLTF } from '@react-three/drei';
import * as THREE from 'three';

// ---- Fit camera to the loaded model (runs once after mount) ----
function AutoCamera({ groupRef }: { groupRef: React.RefObject<THREE.Group | null> }) {
  const { camera, invalidate } = useThree();
  const fitted = useRef(false);

  useFrame(() => {
    if (fitted.current || !groupRef.current) return;
    fitted.current = true;

    const box = new THREE.Box3().setFromObject(groupRef.current);
    if (box.isEmpty()) return;

    const size = new THREE.Vector3();
    const center = new THREE.Vector3();
    box.getSize(size);
    box.getCenter(center);

    const maxDim = Math.max(size.x, size.y, size.z);
    const cam = camera as THREE.PerspectiveCamera;
    const fov = cam.fov * (Math.PI / 180);
    const dist = (maxDim / 2 / Math.tan(fov / 2)) * 2.0;

    cam.position.set(
      center.x + dist * 0.7,
      center.y + dist * 0.5,
      center.z + dist * 0.7,
    );
    cam.near = Math.max(0.1, dist * 0.01);
    cam.far = dist * 20;
    cam.updateProjectionMatrix();
    cam.lookAt(center);
    invalidate();
  });

  return null;
}

// ---- The actual GLB scene ----
function GLBScene({
  url,
  wireframe,
  explodeFactor,
}: {
  url: string;
  wireframe: boolean;
  explodeFactor: number;
}) {
  const { scene } = useGLTF(url);
  const groupRef = useRef<THREE.Group>(null!);

  // Store original positions for explode/assemble
  const origPositions = useRef<Map<string, THREE.Vector3>>(new Map());

  // Clone materials and record original positions once on mount
  useEffect(() => {
    scene.traverse((obj: any) => {
      if (obj.isObject3D && !origPositions.current.has(obj.uuid)) {
        origPositions.current.set(obj.uuid, obj.position.clone());
      }
      if (!obj.isMesh) return;
      if (!obj.userData.__matCloned) {
        obj.material = Array.isArray(obj.material)
          ? obj.material.map((m: THREE.Material) => m.clone())
          : obj.material.clone();
        obj.userData.__matCloned = true;
      }
    });
  }, [scene]);

  // Apply wireframe toggle
  useEffect(() => {
    scene.traverse((obj: any) => {
      if (!obj.isMesh) return;
      const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
      mats.forEach((m: any) => { m.wireframe = wireframe; });
    });
  }, [scene, wireframe]);

  // Apply explode factor — move each top-level child away from centre
  useEffect(() => {
    if (!groupRef.current) return;
    const children = groupRef.current.children.filter(c => c.type !== 'PerspectiveCamera');
    const total = children.length;
    children.forEach((child, i) => {
      const orig = origPositions.current.get(child.uuid);
      if (orig) {
        // Push each child outward from centre along a spread direction
        const angle = (i / total) * Math.PI * 2;
        child.position.set(
          orig.x + Math.cos(angle) * explodeFactor * 80,
          orig.y + explodeFactor * 40,
          orig.z + Math.sin(angle) * explodeFactor * 80,
        );
      }
    });
  }, [explodeFactor]);

  return (
    <group ref={groupRef}>
      <AutoCamera groupRef={groupRef} />
      <primitive object={scene} />
    </group>
  );
}

// ---- Minimal spinning wireframe cube shown while GLB is fetching ----
function LoadingCube() {
  const ref = useRef<THREE.Mesh>(null!);
  useFrame((_, delta) => {
    if (ref.current) {
      ref.current.rotation.x += delta * 0.8;
      ref.current.rotation.y += delta * 1.2;
    }
  });
  return (
    <mesh ref={ref}>
      <boxGeometry args={[20, 20, 20]} />
      <meshBasicMaterial color="#3b82f6" wireframe />
    </mesh>
  );
}

// ---- Public component ----
export interface CADViewerProps {
  glbUrl: string | null;
  wireframe?: boolean;
  explodeFactor?: number;
  backgroundColor?: string;
}

// Preload helper so pages can prime the cache before rendering the viewer
export function preloadGLB(url: string) {
  useGLTF.preload(url);
}

export default function CADViewer({
  glbUrl,
  wireframe = false,
  explodeFactor = 0,
  backgroundColor = '#1a1d28',
}: CADViewerProps) {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setReady(false);
    if (glbUrl) {
      // Preload so useGLTF inside Canvas hits the cache immediately
      useGLTF.preload(glbUrl);
      // Give the preload a moment then mark ready to mount the Canvas
      const t = setTimeout(() => setReady(true), 50);
      return () => clearTimeout(t);
    }
  }, [glbUrl]);

  if (!glbUrl) {
    return (
      <div className="flex items-center justify-center h-full" style={{ backgroundColor }}>
        <p className="text-sm" style={{ color: 'var(--workspace-text-muted)' }}>
          No 3D model available. Generate a design first.
        </p>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full" style={{ backgroundColor }}>
      {/* Loading overlay — pure HTML, no DOM conflicts with Canvas */}
      {!ready && (
        <div
          className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-3"
          style={{ backgroundColor, pointerEvents: 'none' }}
        >
          <div className="spinner" />
          <span className="text-xs" style={{ color: 'var(--workspace-text-muted)' }}>
            Preparing 3D model…
          </span>
        </div>
      )}

      {ready && (
        <Canvas
          frameloop="demand"
          camera={{ position: [0, 0, 500], fov: 45, near: 0.1, far: 10000 }}
          gl={{ antialias: true, alpha: false, powerPreference: 'high-performance' }}
          style={{ display: 'block', width: '100%', height: '100%' }}
        >
          <color attach="background" args={[backgroundColor]} />

          {/* Lights — no shadows for performance */}
          <ambientLight intensity={0.7} />
          <directionalLight position={[300, 400, 300]} intensity={1.0} />
          <directionalLight position={[-200, -150, -300]} intensity={0.4} />
          <hemisphereLight args={['#404060', '#202030', 0.5]} />

          <Suspense fallback={<LoadingCube />}>
            <GLBScene url={glbUrl} wireframe={wireframe} explodeFactor={explodeFactor} />
          </Suspense>

          <Grid
            args={[2000, 2000]}
            cellSize={20}
            cellColor="#2a2e3d"
            sectionSize={100}
            sectionColor="#3a3e4d"
            fadeDistance={1500}
            fadeStrength={1}
            position={[0, -150, 0]}
          />

          <OrbitControls
            makeDefault
            enablePan
            enableZoom
            enableRotate
            zoomSpeed={1.2}
            rotateSpeed={0.8}
            panSpeed={0.8}
            dampingFactor={0.08}
            enableDamping
            minDistance={5}
            maxDistance={8000}
          />
        </Canvas>
      )}
    </div>
  );
}
