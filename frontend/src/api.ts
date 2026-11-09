import type { components } from "./api-types.gen";
import { API_BASE } from "./config";

// Types générés depuis docs/api/openapi.json (make gen-api) : une dérive du contrat casse la compilation (I-01).
type Schemas = components["schemas"];
export type Prediction = Schemas["PredictionResponse"];
export type PredictionRequest = Schemas["PredictionRequest"];
export type Crop = Schemas["Crop"];
export type CropsResponse = Schemas["CropsResponse"];
export type GeocodeResult = Schemas["GeocodeResult"];
export type WeatherResponse = Schemas["WeatherResponse"];
export type IndicatorsResponse = Schemas["IndicatorsResponse"];

/** Erreur de l'API (code stable du contrat) ou NETWORK_ERROR si le serveur est injoignable. */
export class ApiError extends Error {
  constructor(
    message: string,
    readonly code: string,
    readonly status: number,
    readonly requestId?: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, init);
  } catch {
    throw new ApiError("Serveur injoignable", "NETWORK_ERROR", 0);
  }
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(
      body?.error?.message ?? `Erreur ${response.status}`,
      body?.error?.code ?? `HTTP_${response.status}`,
      response.status,
      body?.request_id,
    );
  }
  return body as T;
}

const query = (params: Record<string, string | number | undefined>) => {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) if (v !== undefined && v !== "") q.set(k, String(v));
  return q.toString();
};

export const getCrops = () => request<CropsResponse>("/v1/crops");

export const geocode = (q: string) =>
  request<{ results: GeocodeResult[] }>(`/v1/geocode?${query({ q, limit: 5 })}`);

export const getWeather = (latitude: number, longitude: number, start_date: string, end_date: string) =>
  request<WeatherResponse>(`/v1/weather?${query({ latitude, longitude, start_date, end_date })}`);

export const getIndicators = (latitude: number, longitude: number, reference_date: string, window_days: number) =>
  request<IndicatorsResponse>(`/v1/indicators?${query({ latitude, longitude, reference_date, window_days })}`);

export const postPrediction = (body: PredictionRequest) =>
  request<Prediction>("/v1/predictions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
