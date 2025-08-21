"use client";
export default function GoalGauge({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  return (
    <div className="rounded-lg border bg-white p-4 flex flex-col justify-between">
      <h3 className="mb-2 font-semibold">Goal Probability</h3>
      <div className="w-full bg-gray-200 rounded-full h-6 overflow-hidden">
        <div className="h-6 rounded-full" style={{ width: `${pct}%`, background: 'linear-gradient(90deg, #22c55e, #16a34a)' }} />
      </div>
      <div className="mt-2 text-sm text-gray-700">{pct}%</div>
    </div>
  );
}
