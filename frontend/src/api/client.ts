import type {
  ActionResponse,
  ConceptMap,
  DetailLevel,
  FeedbackRating,
  IdeaCard,
  LlmProvider,
  ScoreWeights,
  Settings,
} from "../types";

const API_PORT = 8765;

const defaultBaseUrl = (() => {
  if (typeof window === "undefined") {
    return `http://localhost:${API_PORT}`;
  }

  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  if ((protocol === "http:" || protocol === "https:") && hostname) {
    return `http://${hostname}:${API_PORT}`;
  }

  return `http://localhost:${API_PORT}`;
})();

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? defaultBaseUrl;

type JsonRecord = Record<string, unknown>;

const defaultScoreWeights: ScoreWeights = {
  novelty: 0.22,
  relevance: 0.18,
  distance: 0.18,
  feasibility: 0.16,
  fun: 0.16,
  api_fit: 0.1,
};

function normalizeErrorMessage(rawMessage: string, status: number): string {
  let message = rawMessage || `Request failed with status ${status}`;

  try {
    const parsed = JSON.parse(rawMessage) as { detail?: unknown; message?: unknown };
    if (typeof parsed.detail === "string" && parsed.detail.trim()) {
      message = parsed.detail;
    } else if (typeof parsed.message === "string" && parsed.message.trim()) {
      message = parsed.message;
    }
  } catch {
    // The response body is plain text.
  }

  if (message === "At least two concepts are required") {
    return "発想の材料がまだ足りません。先に素材を取り込んでから生成してください。";
  }

  if (message === "Unable to find concept combinations") {
    return "組み合わせ候補をまだ作れませんでした。素材を増やしてから再度お試しください。";
  }

  if (message === "Idea card not found") {
    return "対象のアイデアが見つかりませんでした。画面を読み直してもう一度お試しください。";
  }

  if (message === "Invalid rating") {
    return "フィードバックの値が不正です。画面を読み直してもう一度お試しください。";
  }

  return message;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const message = normalizeErrorMessage(await response.text(), response.status);
    throw new Error(message);
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
  const nestedWeights =
    (payload.score_weights as Partial<ScoreWeights> | undefined) ??
    (payload.weights as Partial<ScoreWeights> | undefined) ??
    {};

  return {
    llm_provider: String(payload.llm_provider ?? "anthropic") as LlmProvider,
    embedding_provider: "local",
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
    local_scan_dirs: Array.isArray(payload.local_scan_dirs)
      ? payload.local_scan_dirs.map((entry) => String(entry))
      : [],
    external_api_enabled: Boolean(payload.external_api_enabled ?? true),
  };
}

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
  rating: FeedbackRating;
}

export interface IngestParams {
  dirs?: string[];
  texts?: string[];
}

export interface IngestResponse {
  concepts_added: number;
  sources_scanned: number;
  directories_used: string[];
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
}: SubmitFeedbackParams): Promise<ActionResponse> {
  return request<ActionResponse>("/api/feedback", {
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

export async function updateSettings(settings: Settings): Promise<Settings> {
  const payload = await request<JsonRecord>("/api/settings", {
    method: "PUT",
    body: JSON.stringify({
      llm_provider: settings.llm_provider,
      embedding_provider: settings.embedding_provider,
      local_scan_dirs: settings.local_scan_dirs,
      external_api_enabled: settings.external_api_enabled,
      score_weights: settings.score_weights,
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
