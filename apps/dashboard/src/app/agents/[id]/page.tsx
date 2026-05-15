export default async function AgentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Agent Detail</h1>
      <p className="text-gray-500">Agent ID: {id}</p>
      <p className="text-gray-400 mt-4">Connect to the registry service to view agent details.</p>
    </div>
  );
}
