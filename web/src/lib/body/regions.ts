import type { TriageOption } from '$lib/triage';

export type RegionId = 'head' | 'chest' | 'upper-abdomen' | 'lower-abdomen' | 'arm' | 'leg' | 'back';
export type OrganId = 'brain' | 'heart' | 'lungs' | 'stomach' | 'liver' | 'intestines' | 'kidneys' | 'bladder' | 'pancreas' | 'spleen';
export type SideId = 'skin' | 'allergies' | 'child' | 'mental' | 'not-sure' | 'womens-health' | 'mens-health' | 'breast';
export type FaceId = 'eyes' | 'nose' | 'mouth' | 'jaw' | 'ear' | 'nerves';
export type TargetId = RegionId | OrganId | SideId | FaceId;

export const organIds: OrganId[] = ['brain', 'heart', 'lungs', 'stomach', 'liver', 'intestines', 'kidneys', 'bladder', 'pancreas', 'spleen'];

/** Which organs live in each outer region (Layer 2). Regions not listed (head, arm,
 *  leg, back) have no internal organs - selecting them goes straight to the result. */
export const regionOrgans: Record<RegionId, OrganId[]> = {
  head: [],
  chest: ['heart', 'lungs'],
  'upper-abdomen': ['stomach', 'liver', 'pancreas', 'spleen'],
  'lower-abdomen': ['intestines', 'kidneys', 'bladder'],
  arm: [],
  leg: [],
  back: [],
};

type Pt = { x: number; y: number; z: number };
type Box = { min: Pt; max: Pt };

/** Classify a raycast hit on the body shell into an anatomical region by its
 *  normalized position within the model's bounding box (model-agnostic). */
export function classifyHit(p: Pt, box: Box): RegionId {
  const sx = box.max.x - box.min.x, sy = box.max.y - box.min.y;
  const ny = (p.y - box.min.y) / sy;                 // 0 feet .. 1 head
  const nx = Math.abs((p.x - (box.min.x + box.max.x) / 2) / sx); // 0 center .. 0.5 edge
  const front = p.z >= (box.min.z + box.max.z) / 2;

  if (ny >= 0.85) return 'head';
  if (ny < 0.45) return 'leg';                        // everything below the hip
  if (nx > 0.18) return 'arm';                        // limbs out to the sides
  if (!front) return 'back';                          // torso, back side
  if (ny >= 0.68) return 'chest';
  if (ny >= 0.60) return 'upper-abdomen';
  return 'lower-abdomen';                             // pelvis / lower belly (0.45-0.60)
}

/** Classify a hit within the head band (ny >= 0.85) into a facial sub-region.
 *  Mirror of the face-zone logic in BodyScene's shader - keep them in sync. */
export function classifyFace(p: Pt, box: Box): FaceId {
  const sx = box.max.x - box.min.x, sy = box.max.y - box.min.y;
  const ny = (p.y - box.min.y) / sy;
  const nx = Math.abs((p.x - (box.min.x + box.max.x) / 2) / sx);
  const front = p.z >= (box.min.z + box.max.z) / 2;
  const fy = (ny - 0.85) / 0.15; // 0 chin .. 1 crown, within the head
  if (nx > 0.06) return 'ear';   // off to the sides
  if (!front) return 'nerves';   // back of head
  if (fy > 0.72) return 'nerves'; // forehead / scalp
  if (fy >= 0.5) return 'eyes';
  if (fy >= 0.32) return 'nose';
  if (fy >= 0.15) return 'mouth';
  return 'jaw';
}

const lt = (ka: string, en: string) => ({ ka, en });
const toNode = (ka: string, en: string, next: string): TriageOption => ({ label: lt(ka, en), next });
const toResult = (ka: string, en: string, type: 'specialty' | 'condition', slug: string): TriageOption =>
  ({ label: lt(ka, en), result: { type, slug } });

/** Each pickable target → the concern options shown in the refine panel.
 *  Selecting one is handed to triage.ts `advance()`. */
export const bodyMap: Record<TargetId, TriageOption[]> = {
  // ---- surface regions ----
  head: [
    toResult('თავის ტკივილი, ნერვები', 'Headaches, nerves', 'specialty', 'neurology'),
    toResult('თვალები', 'Eyes', 'specialty', 'ophthalmology'),
    toResult('ალერგია (თვალები/ცხვირი)', 'Allergy (eyes/nose)', 'specialty', 'allergology'),
    toResult('ყური, ცხვირი, ყელი', 'Ear, nose, throat', 'specialty', 'ent'),
    toResult('კბილები', 'Teeth', 'specialty', 'dentistry'),
    toResult('ფსიქიკური ჯანმრთელობა', 'Mental health', 'specialty', 'psychiatry'),
  ],
  chest: [
    toNode('გული / წნევა', 'Heart / blood pressure', 's_heart'),
    toNode('სუნთქვა, ხველა', 'Breathing, cough', 's_breathing'),
  ],
  'upper-abdomen': [
    toResult('კუჭი, მონელება', 'Stomach, digestion', 'specialty', 'gastroenterology'),
    toResult('ჰორმონები, დიაბეტი', 'Hormones, diabetes', 'specialty', 'endocrinology'),
  ],
  'lower-abdomen': [
    toResult('ნაწლავები', 'Intestines / bowel', 'specialty', 'gastroenterology'),
    toResult('შარდვა, მამაკაცის ჯანმრთელობა', 'Urinary, men’s health', 'specialty', 'urology'),
    toNode('ქალის ჯანმრთელობა', 'Women’s health', 's_womens'),
  ],
  arm: [toNode('სახსრები, ტრავმა', 'Joints, injury', 's_msk')],
  leg: [
    toNode('სახსრები, ტრავმა', 'Joints, injury', 's_msk'),
    toResult('ვარიკოზი / ვენები', 'Varicose veins', 'condition', 'varicose-veins'),
  ],
  back: [toNode('ზურგის ან სახსრების ტკივილი', 'Back or joint pain', 's_msk')],

  // ---- internal organs ----
  brain: [toNode('თავის ტკივილი, ნერვები', 'Headaches, nerves', 's_head')],
  heart: [toNode('გული / წნევა', 'Heart / blood pressure', 's_heart')],
  lungs: [toNode('სუნთქვა, ხველა', 'Breathing, cough', 's_breathing')],
  stomach: [toResult('კუჭი, მონელება', 'Stomach, digestion', 'specialty', 'gastroenterology')],
  liver: [toResult('ღვიძლი', 'Liver', 'specialty', 'gastroenterology')],
  intestines: [toResult('ნაწლავები', 'Intestines / bowel', 'specialty', 'gastroenterology')],
  kidneys: [toResult('თირკმლის დაავადება', 'Kidney disease', 'specialty', 'nephrology'), toResult('თირკმლის კენჭები', 'Kidney stones', 'specialty', 'urology')],
  bladder: [toResult('შარდოვანი', 'Urinary', 'specialty', 'urology')],
  pancreas: [toResult('პანკრეასი / დიაბეტი', 'Pancreas / diabetes', 'specialty', 'endocrinology'), toResult('საჭმლის მონელება', 'Digestion', 'specialty', 'gastroenterology')],
  spleen: [toResult('ელენთა', 'Spleen', 'specialty', 'hematology')],

  // ---- side list (non-spatial) ----
  skin: [
    toResult('კანი, თმა, ფრჩხილები', 'Skin, hair, nails', 'specialty', 'dermatology'),
    toResult('ალერგიული გამონაყარი', 'Allergic rash', 'specialty', 'allergology'),
  ],
  allergies: [toResult('ალერგია', 'Allergies', 'specialty', 'allergology')],
  child: [toResult('ბავშვი', 'A child', 'specialty', 'pediatrics')],
  mental: [
    toNode('ფსიქიკური ჯანმრთელობა', 'Mental health', 's_mental'),
  ],
  'not-sure': [toResult('არ ვარ დარწმუნებული', 'Not sure', 'specialty', 'family-medicine')],
  'womens-health': [toNode('ქალის ჯანმრთელობა', 'Women’s health', 's_womens')],
  'mens-health': [toResult('მამაკაცის ჯანმრთელობა', 'Men’s health', 'specialty', 'urology'), toResult('ანდროლოგია', 'Andrology', 'specialty', 'andrology')],
  breast: [toResult('მკერდი / სარძევე ჯირკვალი', 'Breast', 'specialty', 'mammology'), toResult('ონკოლოგია', 'Oncology', 'specialty', 'breast-oncology')],

  // ---- facial sub-regions (head zoom) ----
  eyes: [toResult('თვალები', 'Eyes', 'specialty', 'ophthalmology'), toResult('ალერგია', 'Eye allergy', 'specialty', 'allergology')],
  nose: [toResult('ცხვირი / სინუსები', 'Nose / sinuses', 'specialty', 'ent'), toResult('ალერგია', 'Nasal allergy', 'specialty', 'allergology')],
  mouth: [toResult('კბილები, პირი', 'Teeth, mouth', 'specialty', 'dentistry')],
  jaw: [toResult('ყბა', 'Jaw', 'specialty', 'maxillofacial-surgery')],
  ear: [toResult('ყური', 'Ear', 'specialty', 'ent')],
  nerves: [toResult('თავის ტკივილი, ნერვები', 'Headache, nerves', 'specialty', 'neurology')],
};
