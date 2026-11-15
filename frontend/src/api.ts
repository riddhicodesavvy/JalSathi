import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import type { Dataset, Feature, History, Registry } from "./types";
export const API = import.meta.env.VITE_API_URL || "/api/v1";
export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(API + path, init);
  } catch {
    throw new Error(
      "Cannot reach the API. Check that the backend is running, then retry.",
    );
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(
      body?.error?.message || `Request failed (${response.status}).`,
    );
  }
  return response.json();
}
export function useFeatures() {
  return useQuery({
    queryKey: ["features"],
    queryFn: ({ signal }) => request<Feature[]>("/features", { signal }),
    staleTime: Infinity,
  });
}
export function useModels() {
  return useQuery({
    queryKey: ["models"],
    queryFn: ({ signal }) => request<Registry>("/models", { signal }),
    staleTime: 60000,
  });
}
export function useDataset() {
  return useQuery({
    queryKey: ["dataset"],
    queryFn: ({ signal }) => request<Dataset>("/dataset/summary", { signal }),
    staleTime: Infinity,
  });
}
export function useHistory(offset = 0) {
  return useQuery({
    queryKey: ["history", offset],
    queryFn: ({ signal }) =>
      request<History>(`/analyses?limit=10&offset=${offset}`, { signal }),
  });
}
export async function download(path: string, filename: string) {
  try {
    const response = await fetch(API + path);
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      throw new Error(body?.error?.message || "Download failed.");
    }
    const url = URL.createObjectURL(await response.blob());
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    toast.success("Download ready.");
  } catch (error) {
    toast.error(error instanceof Error ? error.message : "Download failed.");
  }
}
