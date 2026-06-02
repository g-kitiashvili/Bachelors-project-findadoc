export function hasWebGL(): boolean {
  if (typeof document === 'undefined') return false; // SSR
  try {
    const canvas = document.createElement('canvas');
    return !!(canvas.getContext('webgl2') || canvas.getContext('webgl'));
  } catch {
    return false;
  }
}
