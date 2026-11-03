import type { components } from "./api-types.gen";

// Types générés depuis docs/api/openapi.json (make gen-api) : une dérive du contrat casse la compilation (I-01).
type Schemas = components["schemas"];
export type Prediction = Schemas["PredictionResponse"];
export type PredictionRequest = Schemas["PredictionRequest"];
export type CropsResponse = Schemas["CropsResponse"];
export type Crop = Schemas["Crop"];
export class ApiError extends Error {}

async function parse<T>(r: Response): Promise<T> {
  const body = await r.json().catch(() => null);
  if (!r.ok) throw new ApiError(body?.error?.message ?? `Erreur ${r.status}`);
  return body as T;
}

export const getCrops = () => fetch("/api/v1/crops").then((r) => parse<CropsResponse>(r));

export const postPrediction = (crop_id: string, latitude: number, longitude: number) => {
  const body: PredictionRequest = { crop_id, location: { latitude, longitude }, window_days: 30 };
  return fetch("/api/v1/predictions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then((r) => parse<Prediction>(r));
};
