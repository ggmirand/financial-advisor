"use client";
export default function OverviewCards({ data }: { data: any }) {
  const cards = [
    { label: "Net Worth", value: `$${data.net_worth.toLocaleString()}` },
    { label: "As of", value: new Date(data.as_of).toLocaleString() },
    { label: "Alerts", value: data.alerts.length }
  ];
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {cards.map((c) => (
        <div key={c.label} className="rounded-lg border bg-white p-4">
          <div className="text-sm text-gray-500">{c.label}</div>
          <div className="text-2xl font-semibold">{c.value}</div>
        </div>
      ))}
    </div>
  );
}
