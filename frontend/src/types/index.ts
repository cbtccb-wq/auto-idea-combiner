export type DetailLevel = "light" | "standard" | "deep";
export type LlmProvider = "anthropic" | "openai" | "gemini" | "local";
export type EmbeddingProvider = "local";

export type FeedbackRating =
  | "great"
  | "ok"
  | "no"
  | "closer"
  | "further"
  | "practical"
  | "wilder";

export interface IdeaCard {
  id: string;
  title: string;
  concept_a: string;
  concept_b: string;
  summary: string;
  why_interesting: string;
  target_user: string;
  main_tech: string;
  mvp_outline: string;
  differentiator: string;
  fun_point: string;
  risks: string;
  novelty_score: number;
  relevance_score: number;
  distance_score: number;
  feasibility_score: number;
  fun_score: number;
  api_fit_score: number;
  total_score: number;
  detail_level: string;
  created_at: string;
}

export interface ActionResponse {
  ok: boolean;
}

export interface ConceptNode {
  id: string;
  label: string;
  frequency: number;
  source: string;
}

export interface ConceptEdge {
  source: string;
  target: string;
  weight: number;
  distance: number;
}

export interface ConceptMap {
  nodes: ConceptNode[];
  edges: ConceptEdge[];
}

export interface ScoreWeights {
  novelty: number;
  relevance: number;
  distance: number;
  feasibility: number;
  fun: number;
  api_fit: number;
}

export interface Settings {
  llm_provider: LlmProvider;
  embedding_provider: EmbeddingProvider;
  score_weights: ScoreWeights;
  local_scan_dirs: string[];
  external_api_enabled: boolean;
}
