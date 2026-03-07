export type FailureCode =
  | 'C1' | 'C2' | 'C3'
  | 'S1' | 'S2'
  | 'L1' | 'L2' | 'L3' | 'L4'
  | 'A1' | 'A2' | 'A3'
  | 'M1' | 'M2'
  | 'B1' | 'B2'
  | 'T1' | 'T2'
  | 'P1' | 'P2';

export const FAILURE_TAXONOMY: Record<FailureCode, { name: string; desc: string }> = {
  C1: { name: 'COLOR_WRONG', desc: "Colors don't match brand palette" },
  C2: { name: 'COLOR_DULL', desc: 'Colors are washed out or muddy' },
  C3: { name: 'COLOR_OVER', desc: 'Colors are over-saturated or neon' },
  S1: { name: 'STYLE_MISMATCH', desc: "Art style doesn't match brand" },
  S2: { name: 'STYLE_GENERIC', desc: 'Looks like generic stock photography' },
  L1: { name: 'LAYOUT_CLUTTERED', desc: 'Too many elements, no hierarchy' },
  L2: { name: 'LAYOUT_NO_SAFE_ZONE', desc: 'No space for text overlay' },
  L3: { name: 'LAYOUT_SUBJECT_SMALL', desc: 'Main subject is tiny' },
  L4: { name: 'LAYOUT_WRONG_ANGLE', desc: 'Camera angle is wrong' },
  A1: { name: 'ARTIFACT_DISTORTION', desc: 'Melted/warped objects' },
  A2: { name: 'ARTIFACT_TEXT', desc: 'Unwanted text appeared' },
  A3: { name: 'ARTIFACT_EXTRA', desc: 'Unexpected extra objects' },
  M1: { name: 'MOOD_WRONG', desc: "Emotional tone doesn't match" },
  M2: { name: 'MOOD_FLAT', desc: 'No visual impact, boring' },
  B1: { name: 'BG_BUSY', desc: 'Background competes with subject' },
  B2: { name: 'BG_WRONG', desc: 'Wrong setting/environment' },
  T1: { name: 'TEXTURE_PLASTIC', desc: 'Surfaces look fake' },
  T2: { name: 'TEXTURE_WRONG', desc: "Materials don't match" },
  P1: { name: 'PROMPT_IGNORED', desc: 'Model ignored key instruction' },
  P2: { name: 'PROMPT_REWRITTEN', desc: 'API rewrote critical intent' },
};

// Category color mapping for failure code badges
export function getFailureCodeColor(code: FailureCode): string {
  const prefix = code[0];
  switch (prefix) {
    case 'C': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
    case 'S': return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
    case 'L': return 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20';
    case 'A': return 'text-red-400 bg-red-500/10 border-red-500/20';
    case 'M': return 'text-purple-400 bg-purple-500/10 border-purple-500/20';
    case 'B': return 'text-gray-400 bg-gray-500/10 border-gray-500/20';
    case 'T': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
    case 'P': return 'text-red-400 bg-red-500/10 border-red-500/20';
    default: return 'text-gray-400 bg-gray-500/10 border-gray-500/20';
  }
}

// Request types
export interface PromptEngineerGenerateRequest {
  brand_id: number;
  subject: string;
  platform?: string;
  mood?: string;
  key_message?: string;
  must_include?: string[];
  must_exclude?: string[];
  text_overlay_position?: string;
}

export interface PromptEngineerDiagnoseRequest {
  image_description: string;
  original_prompt: string;
  revised_prompt?: string;
}

export interface PromptEngineerRepromptRequest {
  brand_id: number;
  original_prompt: string;
  failure_description: string;
  attempt_number?: number;
}

// Response types
export interface PromptEngineerGenerateResponse {
  brand_style_anchor: string;
  primary_prompt: string;
  variations: string[];
  platform_notes: string;
  platform: string;
  platform_spec: { ratio: string; size: string; desc: string };
  error?: string;
}

export interface PromptEngineerDiagnoseResponse {
  failure_codes: FailureCode[];
  diagnosis: string;
  severity: 'minor' | 'moderate' | 'major';
  is_systemic: boolean;
  recommendation: string;
  error?: string;
}

export interface PromptEngineerRepromptResponse {
  failure_codes: FailureCode[];
  diagnosis: string;
  corrected_prompt: string;
  patches_applied: string[];
  attempt_number: number;
  recommendation: string;
  error?: string;
}
