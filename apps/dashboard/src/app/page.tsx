function DashboardCard({
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

export default function DashboardHome() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <DashboardCard title="Agents" value="—" description="Registered agents" />
        <DashboardCard title="Capabilities" value="—" description="Available capabilities" />
        <DashboardCard title="Tools" value="—" description="Registered tools" />
        <DashboardCard title="Conversations" value="—" description="Active conversations" />
      </div>
    </div>
  );
}
