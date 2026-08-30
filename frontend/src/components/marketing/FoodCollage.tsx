import { FoodImage } from "@/components/media/FoodImage";

/**
 * Landing-page visual. Uses the same deterministic food treatment as the feed
 * so the marketing surface and the product look like one thing. No stock
 * photography, no external image URLs.
 */
const TILES = [
  { name: "Wood-fired Margherita", category: "pizza", seed: "collage-pizza", span: "row-span-2" },
  { name: "Chicken Karahi", category: "karahi desi", seed: "collage-karahi", span: "" },
  { name: "Salmon Nigiri", category: "sushi japanese", seed: "collage-sushi", span: "" },
  { name: "Beef Seekh Kebab", category: "bbq grill", seed: "collage-kebab", span: "row-span-2" },
  { name: "Chocolate Lava Cake", category: "dessert", seed: "collage-cake", span: "" },
  { name: "Chow Mein", category: "chinese noodle", seed: "collage-chow", span: "" },
];

export function FoodCollage() {
  return (
    <div className="grid grid-cols-2 gap-3 sm:gap-4">
      {TILES.map((t) => (
        <div
          key={t.seed}
          className={`overflow-hidden rounded-card border border-hairline shadow-card ${t.span}`}
        >
          <FoodImage
            name={t.name}
            category={t.category}
            seed={t.seed}
            className="h-40 sm:h-48"
          />
        </div>
      ))}
    </div>
  );
}
