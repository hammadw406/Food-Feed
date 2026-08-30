import { apiRequest } from "./client";

export async function getHealth(): Promise<{ status: string }> {
  return apiRequest("/health");
}
