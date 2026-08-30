import { FoodDetailView } from "@/components/food/FoodDetailView";

export default function FoodPage({ params }: { params: { id: string } }) {
  return <FoodDetailView id={decodeURIComponent(params.id)} />;
}
