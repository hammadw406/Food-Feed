import { apiRequest } from "./client";
import type { RestaurantDetail } from "./types";

type Raw = Record<string, unknown>;

function num(v: unknown): number | null {
  if (v === null || v === undefined || v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}
function str(v: unknown): string | null {
  if (v === null || v === undefined) return null;
  const s = String(v).trim();
  return s.length ? s : null;
}

/**
 * GET /restaurants/{restaurant_id} — the only restaurant route the backend
 * exposes. There is NO list/search endpoint.
 */
export async function getRestaurant(
  id: number | string,
  signal?: AbortSignal,
): Promise<RestaurantDetail> {
  const raw = await apiRequest<Raw>(`/restaurants/${id}`, { signal });
  const items = Array.isArray(raw.items) ? (raw.items as Raw[]) : [];
  return {
    restaurantId: num(raw.restaurant_id) ?? Number(id),
    name: str(raw.name) ?? "Restaurant",
    area: str(raw.area),
    cuisine: str(raw.cuisine),
    priceBand: str(raw.price_band),
    rating: num(raw.rating),
    reviewCount: num(raw.review_count),
    items: items.map((it) => ({
      candidateId: String(it.candidate_id ?? ""),
      displayName: str(it.display_name) ?? "Dish",
      category: str(it.category),
      price: num(it.price),
      rating: num(it.rating),
    })),
  };
}
