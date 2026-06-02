import { describe, it, expect } from 'vitest';
import { classifyHit, bodyMap, organIds, type RegionId } from './regions';

// a 1.8-tall box centered on origin: y in [-0.9, 0.9], x in [-0.5, 0.5], z in [-0.25, 0.25]
const box = { min: { x: -0.5, y: -0.9, z: -0.25 }, max: { x: 0.5, y: 0.9, z: 0.25 } };
const at = (nx: number, ny: number, front = true) => ({
  x: box.min.x + nx * (box.max.x - box.min.x),
  y: box.min.y + ny * (box.max.y - box.min.y),
  z: front ? box.max.z : box.min.z,
});

describe('classifyHit', () => {
  it('top of the figure is the head', () => {
    expect(classifyHit(at(0.5, 0.92), box)).toBe('head');
  });
  it('mid-front upper torso is the chest', () => {
    expect(classifyHit(at(0.5, 0.72), box)).toBe('chest');
  });
  it('just below chest is the upper abdomen', () => {
    expect(classifyHit(at(0.5, 0.64), box)).toBe('upper-abdomen');
  });
  it('pelvis / lower belly is the lower abdomen', () => {
    expect(classifyHit(at(0.5, 0.54), box)).toBe('lower-abdomen');
  });
  it('far-left at torso height is an arm', () => {
    expect(classifyHit(at(0.04, 0.6), box)).toBe('arm');
  });
  it('low on the figure is a leg', () => {
    expect(classifyHit(at(0.45, 0.2), box)).toBe('leg');
  });
  it('a back-side torso hit is the back', () => {
    expect(classifyHit(at(0.5, 0.62, false), box)).toBe('back');
  });
});

describe('bodyMap integrity', () => {
  it('every classifiable region id has a bodyMap entry', () => {
    const regions: RegionId[] = ['head', 'chest', 'upper-abdomen', 'lower-abdomen', 'arm', 'leg', 'back'];
    for (const r of regions) expect(bodyMap[r], `missing region ${r}`).toBeTruthy();
  });
  it('every organ id has a bodyMap entry', () => {
    for (const o of organIds) expect(bodyMap[o], `missing organ ${o}`).toBeTruthy();
  });
  it('organ ids are exactly the ten expected', () => {
    expect([...organIds].sort()).toEqual(['bladder','brain','heart','intestines','kidneys','liver','lungs','pancreas','spleen','stomach']);
  });
  it('every concern option has exactly one of next/result and a bilingual label', () => {
    for (const [id, opts] of Object.entries(bodyMap)) {
      expect(opts.length, `empty options for ${id}`).toBeGreaterThan(0);
      for (const o of opts) {
        expect(!!o.next !== !!o.result, `option in ${id} needs exactly one of next/result`).toBe(true);
        expect(o.label.ka && o.label.en, `option in ${id} needs ka+en`).toBeTruthy();
        if (o.result) expect(['specialty', 'condition']).toContain(o.result.type);
      }
    }
  });
});
