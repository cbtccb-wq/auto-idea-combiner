import type {
  ConceptMap,
  DetailLevel,
  Feedback,
  IdeaCard,
  ScoreWeights,
  Settings,
} from "../types";

const BASE_URL = "http://localhost:8765";

type JsonRecord = Record<string, unknown>;

export interface GenerateIdeasParams {
  detailLevel?: DetailLevel;
  count?: number;
}

export interface GetIdeasParams {
  limit?: number;
  today?: boolean;
}

export interface SubmitFeedbackParams {
  ideaCardId: string;
  rating: string;
}

export interface IngestParams {
  local_scan_dirs?: string[];
  external_api_enabled?: boolean;
}

export interface IngestResponse {
  status: string;
  message?: string;
}

const defaultScoreWeights: ScoreWeights = {
  novelty: 0.22,
  relevance: 0.18,
  distance: 0.18,
  feasibility: 0.16,
  fun: 0.16,
  api_fit: 0.1,
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

function buildQuery(params: GetIdeasParams = {}): string {
  const query = new URLSearchParams();

  if (typeof params.limit === "number") {
    query.set("limit", String(params.limit));
  }
  if (typeof params.today === "boolean") {
    query.set("today", String(params.today));
  }

  const serialized = query.toString();
  return serialized ? `?${serialized}` : "";
}

function asIdeaList(payload: IdeaCard[] | JsonRecord): IdeaCard[] {
  if (Array.isArray(payload)) {
    return payload;
  }

  const ideas = payload.ideas;
  return Array.isArray(ideas) ? (ideas as IdeaCard[]) : [];
}

function normalizeSettings(payload: JsonRecord): Settings {
  const nestedWeights = (payload.score_weights as Partial<ScoreWeights> | undefined) ?? {};

  return {
    llm_provider: String(payload.llm_provider ?? "anthropic"),
    embedding_provider: String(payload.embedding_provider ?? "local"),
    score_weights: {
      novelty: Number(nestedWeights.novelty ?? payload.novelty ?? defaultScoreWeights.novelty),
      relevance: Number(
        nestedWeights.relevance ?? payload.relevance ?? defaultScoreWeights.relevance,
      ),
      distance: Number(nestedWeights.distance ?? payload.distance ?? defaultScoreWeights.distance),
      feasibility: Number(
        nestedWeights.feasibility ?? payload.feasibility ?? defaultScoreWeights.feasibility,
      ),
      fun: Number(nestedWeights.fun ?? payload.fun ?? defaultScoreWeights.fun),
      api_fit: Number(nestedWeights.api_fit ?? payload.api_fit ?? defaultScoreWeights.api_fit),
    },
    external_api_enabled: Boolean(payload.external_api_enabled ?? true),
    local_scan_dirs: Array.isArray(payload.local_scan_dirs)
      ? payload.local_scan_dirs.map((entry) => String(entry))
      : [],
  };
}

export async function generateIdeas(params: GenerateIdeasParams = {}): Promise<IdeaCard[]> {
  const payload = await request<IdeaCard[] | JsonRecord>("/api/ideas/generate", {
    method: "POST",
    body: JSON.stringify({
      detail_level: params.detailLevel ?? "standard",
      n_ideas: params.count ?? 3,
    }),
  });

  return asIdeaList(payload);
}

export async function getIdeas(params: GetIdeasParams = {}): Promise<IdeaCard[]> {
  const payload = await request<IdeaCard[] | JsonRecord>(`/api/ideas${buildQuery(params)}`);
  return asIdeaList(payload);
}

export async function submitFeedback({
  ideaCardId,
  rating,
}: SubmitFeedbackParams): Promise<Feedback> {
  return request<Feedback>("/api/feedback", {
    method: "POST",
    body: JSON.stringify({
      idea_card_id: ideaCardId,
      rating,
    }),
  });
}

export async function getConceptMap(): Promise<ConceptMap> {
  const payload = await request<Partial<ConceptMap> | JsonRecord>("/api/concepts/map");
  return {
    nodes: Array.isArray(payload.nodes) ? (payload.nodes as ConceptMap["nodes"]) : [],
    edges: Array.isArray(payload.edges) ? (payload.edges as ConceptMap["edges"]) : [],
  };
}

export async function getSettings(): Promise<Settings> {
  const payload = await request<JsonRecord>("/api/settings");
  return normalizeSettings(payload);
}

export async function updateSettings(settings: Partial<Settings>): Promise<Settings> {
  const payload = await request<JsonRecord>("/api/settings", {
    method: "PUT",
    body: JSON.stringify({
      weights: settings.score_weights ?? {},
    }),
  });

  return normalizeSettings(payload);
}

export async function ingest(payload: IngestParams = {}): Promise<IngestResponse> {
  return request<IngestResponse>("/api/ingest", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
