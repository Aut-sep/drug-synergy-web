export const AVAILABLE_MODELS = ['DualSyn', 'MFSynDCP', 'MVCASyn', 'MTLSynergy'] as const

export type AvailableModel = (typeof AVAILABLE_MODELS)[number]
