"use client";

import { useQuery } from "@tanstack/react-query";
import { getRestaurant } from "@/lib/api/restaurants";

export function useRestaurant(id: number | string | null) {
  return useQuery({
    queryKey: ["restaurant", String(id)],
    queryFn: ({ signal }) => getRestaurant(id as number, signal),
    enabled: id !== null && id !== undefined && String(id).length > 0,
    retry: 1,
  });
}
