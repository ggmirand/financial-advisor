"use client";
import { PieChart, Pie, Tooltip, ResponsiveContainer, Cell } from "recharts";

export default function AllocationChart({ data }: { data: Record<string, number> }) {
  const rows = Object.entries(data).map(([name, value]) => ({ name, value }));
  return (
    <div className="rounded-lg border bg-white p-4">
      <h3 className="mb-2 font-semibold">Asset Allocation</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={rows} dataKey="value" nameKey="name" label />
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
