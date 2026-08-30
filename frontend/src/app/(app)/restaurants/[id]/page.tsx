import { RestaurantView } from "@/components/restaurant/RestaurantView";

export default function RestaurantPage({ params }: { params: { id: string } }) {
  return <RestaurantView id={params.id} />;
}
