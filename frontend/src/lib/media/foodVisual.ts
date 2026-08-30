/**
 * The backend has NO media_url / image field on foods or restaurants
 * (confirmed in backend/app/models/restaurant.py). So every food image slot
 * uses this deterministic fallback: a cuisine-family colour treatment + a
 * short monogram derived from the dish name. Stable per dish, never identical
 * across dishes. When the backend later adds media_url, FoodImage renders the
 * real photo and this becomes the fallback only.
 */

export type CuisineFamily =
  | "italian"
  | "fast"
  | "japanese"
  | "desi"
  | "chinese"
  | "dessert"
  | "healthy"
  | "drink"
  | "grill"
  | "default";

const RULES: [RegExp, CuisineFamily][] = [
  [/piz|pasta|italian|lasagn|risotto|alfredo|calzone/i, "italian"],
  [/burger|fries|zinger|nugget|fried chicken|sandwich|hot dog|wrap|shawarma/i, "fast"],
  [/sushi|ramen|nigiri|maki|tempura|teriyaki|japanese|udon|katsu/i, "japanese"],
  [/karahi|biryani|nihari|tikka|haleem|paratha|desi|pakistani|handi|qorma|kabab|seekh|chapli/i, "desi"],
  [/chow ?mein|manchurian|noodle|chinese|dumpling|dim ?sum|kung pao|szechuan|hakka/i, "chinese"],
  [/cake|brownie|dessert|ice ?cream|pancake|waffle|donut|pastry|tiramisu|cheesecake|lava/i, "dessert"],
  [/salad|bowl|healthy|vegan|quinoa|smoothie bowl|wrap veg/i, "healthy"],
  [/coffee|latte|shake|juice|smoothie|tea|drink|mojito|lemonade|frappe/i, "drink"],
  [/bbq|grill|steak|kebab|tandoori|roast|charga|charcoal/i, "grill"],
];

export function cuisineFamily(input?: string | null): CuisineFamily {
  if (!input) return "default";
  for (const [re, fam] of RULES) if (re.test(input)) return fam;
  return "default";
}

export const FAMILY_STYLE: Record<
  CuisineFamily,
  { from: string; to: string; label: string }
> = {
  italian: { from: "#E8613C", to: "#9E2E28", label: "Italian" },
  fast: { from: "#F0A83E", to: "#C6521F", label: "Fast food" },
  japanese: { from: "#E06B54", to: "#2C3A45", label: "Japanese" },
  desi: { from: "#E0491D", to: "#6E2233", label: "Pakistani" },
  chinese: { from: "#D65440", to: "#7C2A31", label: "Chinese" },
  dessert: { from: "#E4A277", to: "#8A5A3C", label: "Dessert" },
  healthy: { from: "#5B9E6A", to: "#2E6B47", label: "Healthy" },
  drink: { from: "#B9814F", to: "#6B4536", label: "Drinks" },
  grill: { from: "#C6552F", to: "#5C2E2A", label: "Grilled" },
  default: { from: "#B98E63", to: "#5C4636", label: "Food" },
};

function hash(s: string): number {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

export function monogram(name?: string | null): string {
  if (!name) return "◆";
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "◆";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

/** deterministic 0..1 used to vary the gradient angle / blob position */
export function seedFraction(seed: string): number {
  return (hash(seed) % 1000) / 1000;
}
