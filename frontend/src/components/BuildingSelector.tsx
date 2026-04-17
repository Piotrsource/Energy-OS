import { useEffect } from "react";
import { useApi } from "@/hooks/useApi";
import type { Building, PaginatedResponse } from "@/types";

interface Props {
  value: string;
  onChange: (id: string) => void;
}

export default function BuildingSelector({ value, onChange }: Props) {
  const { data } = useApi<PaginatedResponse<Building>>("/buildings?limit=500");
  const buildings = data?.items;

  useEffect(() => {
    if (!value && buildings?.length === 1) {
      onChange(buildings[0].id);
    }
  }, [value, buildings, onChange]);

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
    >
      <option value="">Select building...</option>
      {buildings?.map((b) => (
        <option key={b.id} value={b.id}>
          {b.name}
        </option>
      ))}
    </select>
  );
}
