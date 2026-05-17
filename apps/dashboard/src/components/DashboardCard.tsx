export function DashboardCard({
  title,
  value,
  description,
}: {
  title: string;
  value: string;
  description: string;
}) {
  return (
    <div className="border border-gray-200 rounded-lg p-6">
      <p className="text-sm text-gray-500">{title}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
      <p className="text-xs text-gray-400 mt-1">{description}</p>
    </div>
  );
}
